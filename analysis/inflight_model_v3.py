"""
Fits and scores the in-flight overrun models (ex-ante, behaviour, both), then calibration and SHAP.
Reads data/inflight_checkpoints_v2.csv. The figures and reports folders must already exist.
The clustered bootstrap (3 x 400 resamples) and the SHAP pass are what make it slow.
"""
import json, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from lightgbm import LGBMClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import (roc_auc_score, average_precision_score, brier_score_loss,
                             precision_recall_fscore_support, precision_recall_curve)
from sklearn.calibration import calibration_curve
import shap
D="/Users/huzaifa/dissertation"; FIG=f"{D}/figures"; REP=f"{D}/reports"
RNG=np.random.default_rng(42)

df=pd.read_csv(f"{D}/data/inflight_checkpoints_v2.csv", parse_dates=["cp_date","end_date","created"])
n0=len(df)
# a checkpoint is only a forecast if the overrun wasn't already decided. compare against
# planned_h itself, an expm1 round-trip of log_planned lets determined rows slip through
df=df[df["hours_at_cp"] < df["planned_h"]].copy()
print(f"A3 validity rule (exact): kept {len(df):,} of {n0:,} rows "
      f"({1-len(df)/n0:.1%} excluded as already determined at the checkpoint)")

# the team's prior overrun rate has to be as-of the checkpoint: a past project counts only
# if it had already finished by that date, otherwise the feature carries outcomes nobody
# could have seen yet. team_prior_n is the count of priors that were actually knowable.
proj=(df.groupby("project_id")
        .agg(team_id=("team_id","first"), end=("end_date","max"), breach=("breach","first"))
        .reset_index())
prior_rate=np.full(len(df), np.nan); prior_n=np.zeros(len(df))
pos={ix:i for i,ix in enumerate(df.index)}
for team, idx in df.groupby("team_id").groups.items():
    sub=df.loc[idx]
    pool=proj[proj.team_id==team]
    if pool.empty: continue
    ends=pool["end"].values.astype("datetime64[ns]"); outs=pool["breach"].values.astype(float)
    pids=pool["project_id"].values
    order=np.argsort(ends); ends=ends[order]; outs=outs[order]; pids=pids[order]
    cum=np.cumsum(outs)
    for rid, cpd, own in zip(sub.index, sub["cp_date"].values, sub["project_id"].values):
        k=int(np.searchsorted(ends, np.datetime64(cpd), side="left"))   # closed strictly before cpd
        if k==0: continue
        s=cum[k-1]; n=k
        if own in pids[:k]:                       # a project must not inform its own prior
            j=int(np.where(pids[:k]==own)[0][0]); s-=outs[j]; n-=1
        if n>0:
            prior_rate[pos[rid]]=s/n; prior_n[pos[rid]]=n
df["team_prior_overrun"]=prior_rate; df["team_prior_n"]=prior_n
known=df.team_prior_overrun.notna().mean()
print(f"A1 as-of team prior: {known:.1%} of rows have >=1 prior whose outcome was genuinely known")

EXANTE=["checkpoint","log_planned","team_prior_n","team_prior_overrun"]
BEHAV =["checkpoint","n_decl","span_days","active_days","idle_frac","decl_per_active_day",
        "hours_per_active_day","mean_gap","max_gap","std_gap","cv_gap","max_day_hours",
        "max_day_share","max_decl_hours","n_users","top_user_share","user_entropy","user_hhi"]
FULL  =sorted(set(EXANTE)|set(BEHAV)|{"hours_at_cp"})

# split on wall-clock time rather than project creation date. standing at T you only have
# the projects that had already closed, and everything after it is a real forecast.
T=df["cp_date"].quantile(0.70)
tr=df[(df["end_date"]<=T)].copy()          # outcome on the record by T
te=df[(df["cp_date"]>T)].copy()            # checkpoints reached after T
base=tr["breach"].mean()
# teams with no knowable history fall back to the training base rate, not to zero
for part in (tr,te): part["team_prior_overrun"]=part["team_prior_overrun"].fillna(base)
ytr,yte=tr["breach"].values, te["breach"].values
floor=float(yte.mean()); spw=(ytr==0).sum()/max((ytr==1).sum(),1)
print(f"A2 wall-clock split at T={pd.Timestamp(T).date()}: train {len(tr):,} rows "
      f"(outcome known by T) | test {len(te):,} rows (checkpoints after T) | test floor {floor:.3f}")

def mk(): return LGBMClassifier(n_estimators=600,learning_rate=0.03,num_leaves=31,subsample=0.8,
    colsample_bytree=0.8,min_child_samples=40,scale_pos_weight=spw,random_state=42,verbose=-1)
# PR-AUC is the number to read. breaches are rare, so ROC looks respectable for anything
# that merely sorts the easy negatives. print both and let the gap speak.
def ev(name,p):
    ap=average_precision_score(yte,p); auc=roc_auc_score(yte,p); br=brier_score_loss(yte,p)
    pr,rc,f1,_=precision_recall_fscore_support(yte,(p>=.5).astype(int),average="binary",zero_division=0)
    print(f"  {name:<40} PR-AUC {ap:.3f} | ROC {auc:.3f} | Brier {br:.3f} | F1 {f1:.3f}")
    return dict(model=name,PR_AUC=round(ap,3),ROC_AUC=round(auc,3),Brier=round(br,3),F1=round(f1,3))

print("\n--- deployment-realistic evaluation ---")
res=[ev("B0 prevalence floor", np.full(len(yte), base))]
m_ex=mk().fit(tr[EXANTE],ytr); p_ex=m_ex.predict_proba(te[EXANTE])[:,1]
res.append(ev("B1 ex-ante (size + as-of team history)", p_ex))
m_be=mk().fit(tr[BEHAV],ytr);  p_be=m_be.predict_proba(te[BEHAV])[:,1]
res.append(ev("B2 behaviour only (declaration stream)", p_be))
m_fu=mk().fit(tr[FULL],ytr);   p_fu=m_fu.predict_proba(te[FULL])[:,1]
res.append(ev("B3 FULL (ex-ante + behaviour)", p_fu))
inc=res[3]["PR_AUC"]-res[1]["PR_AUC"]
print(f"\n  behaviour increment over ex-ante : {inc:+.3f} PR-AUC")
print(f"  lift over prevalence floor       : {res[3]['PR_AUC']/floor:.2f}x")

# checkpoints from the same project are anything but independent, so resample whole
# projects. a row-wise bootstrap here would give a flatteringly tight interval.
def boot(p, B=400):
    g=te["project_id"].values; uniq=np.unique(g); out=[]
    idx={u:np.where(g==u)[0] for u in uniq}
    for _ in range(B):
        pick=RNG.choice(uniq, size=len(uniq), replace=True)
        sel=np.concatenate([idx[u] for u in pick])
        if 0 < yte[sel].sum() < len(sel): out.append(average_precision_score(yte[sel], p[sel]))
    return float(np.percentile(out,2.5)), float(np.percentile(out,97.5))
lo,hi=boot(p_fu); lo_b,hi_b=boot(p_be); lo_i,hi_i=boot(p_fu-p_ex+floor)  # AP is rank-based, so +floor is cosmetic
print(f"  FULL PR-AUC 95% CI (clustered by project): [{lo:.3f}, {hi:.3f}]")
print(f"  behaviour-only 95% CI                    : [{lo_b:.3f}, {hi_b:.3f}]")

# prevalence is not the same a quarter of the way in as it is three quarters in, so a
# pooled floor would make one checkpoint look clever and another look useless
print("\n--- per checkpoint (each against its own prevalence floor) ---")
per={}
for c in (0.25,0.50,0.75):
    m_=te["checkpoint"].eq(c).values
    if m_.sum()<50: continue
    f_=float(yte[m_].mean()); ap=average_precision_score(yte[m_],p_fu[m_])
    apb=average_precision_score(yte[m_],p_be[m_])
    per[str(c)]=dict(n=int(m_.sum()),floor=round(f_,3),PR_AUC=round(ap,3),
                     lift=round(ap/f_,2),PR_AUC_behaviour=round(apb,3))
    print(f"  cp {int(c*100)}%  n={m_.sum():5d}  floor {f_:.3f}  PR-AUC {ap:.3f}  lift {ap/f_:.2f}x  (behaviour {apb:.3f})")

# isotonic needs a slice the model has never seen, so hold back the late fifth of training
# by date and fit the mapping there. skipped entirely if that slice is too thin to be useful.
cut2=tr["cp_date"].quantile(0.8)
f_,c_=tr[tr.cp_date<=cut2], tr[tr.cp_date>cut2]
if len(c_)>200:
    mf=mk().fit(f_[FULL],f_["breach"].values)
    iso=IsotonicRegression(out_of_bounds="clip").fit(mf.predict_proba(c_[FULL])[:,1], c_["breach"].values)
    p_cal=np.clip(iso.transform(mf.predict_proba(te[FULL])[:,1]),0.02,0.98)
else:
    p_cal=p_fu
cal=ev("B3 + isotonic calibration", p_cal)
dec=pd.DataFrame({"p":p_cal,"y":yte}); dec["d"]=pd.qcut(dec.p,10,labels=False,duplicates="drop")
bias=float((dec.groupby("d").p.mean()-dec.groupby("d").y.mean()).mean())
print(f"  mean over-forecast across deciles: {bias:+.3f}  ({'over' if bias>0 else 'under'}-predicting)")

sv=shap.TreeExplainer(m_fu).shap_values(te[FULL]); sv=sv[1] if isinstance(sv,list) else sv  # older shap hands back a list per class
mabs=pd.Series(np.abs(sv).mean(0),index=FULL).sort_values(ascending=False)
# checkpoint sits in both feature lists, so it is kept out of the behavioural share
beh_share=float(mabs[[f for f in FULL if f in BEHAV and f!="checkpoint"]].sum()/mabs.sum())
print(f"\n  behavioural share of SHAP magnitude: {beh_share:.1%}")
print("  top drivers:"); [print(f"     {k:<22}{v:.4f}") for k,v in mabs.head(6).items()]

# figures. panel one plots the calibrated scores, the two baselines stay raw.
fig,ax=plt.subplots(1,3,figsize=(16,4.6))
pr_,rc_,_=precision_recall_curve(yte,p_cal)
ax[0].plot(rc_,pr_,color="#0f4c4a",label=f"Full model (AP {cal['PR_AUC']:.2f})")
pr2,rc2,_=precision_recall_curve(yte,p_be); ax[0].plot(rc2,pr2,color="#7aa6a3",ls="--",label=f"Behaviour only (AP {res[2]['PR_AUC']:.2f})")
pr3,rc3,_=precision_recall_curve(yte,p_ex); ax[0].plot(rc3,pr3,color="#b08d57",ls=":",label=f"Ex-ante only (AP {res[1]['PR_AUC']:.2f})")
ax[0].axhline(floor,ls=":",c="grey",label=f"prevalence floor {floor:.2f}")
ax[0].set(title="Precision-recall, deployment-realistic split",xlabel="Recall",ylabel="Precision"); ax[0].legend(fontsize=8)
fr,mp=calibration_curve(yte,p_cal,n_bins=10,strategy="quantile")
ax[1].plot(mp,fr,"o-",color="#0f4c4a"); ax[1].plot([0,1],[0,1],"k--")
ax[1].set(title=f"Calibration (Brier {cal['Brier']:.3f})",xlabel="Forecast probability",ylabel="Observed frequency")
cps=sorted(per); x=[int(float(c)*100) for c in cps]
ax[2].plot(x,[per[c]["lift"] for c in cps],"o-",color="#0f4c4a",label="full")
ax[2].plot(x,[per[c]["PR_AUC_behaviour"]/per[c]["floor"] for c in cps],"s--",color="#7aa6a3",label="behaviour only")
ax[2].axhline(1.0,ls=":",c="grey",label="no skill")
ax[2].set(title="Lift over each checkpoint's own floor",xlabel="% planned effort used",ylabel="PR-AUC / floor"); ax[2].legend(fontsize=8)
plt.tight_layout(); plt.savefig(f"{FIG}/results_v3.png",dpi=140); plt.close()
plt.figure(); shap.summary_plot(sv,te[FULL],feature_names=FULL,show=False,max_display=12)
plt.tight_layout(); plt.savefig(f"{FIG}/shap_v3.png",dpi=140,bbox_inches="tight"); plt.close()

json.dump(dict(
  protocol="wall-clock split at T; as-of-checkpoint team prior; exact validity rule; project-clustered bootstrap",
  decision_date=str(pd.Timestamp(T).date()), rows_valid=int(len(df)), rows_excluded=int(n0-len(df)),
  train_rows=int(len(tr)), test_rows=int(len(te)), test_floor=round(floor,3),
  results=res, calibrated=cal, calibration_bias=round(bias,3),
  full_ci=[round(lo,3),round(hi,3)], behaviour_ci=[round(lo_b,3),round(hi_b,3)],
  behaviour_increment=round(float(inc),3), lift=round(res[3]["PR_AUC"]/floor,2),
  per_checkpoint=per, behaviour_share_of_shap=round(beh_share,3),
  top_shap=mabs.head(10).round(4).to_dict()), open(f"{REP}/inflight_metrics_v3.json","w"), indent=2)
print(f"\nsaved -> {REP}/inflight_metrics_v3.json + figures/results_v3.png + figures/shap_v3.png")
