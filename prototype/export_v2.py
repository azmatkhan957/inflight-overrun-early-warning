# -*- coding: utf-8 -*-
"""Builds the JSON the prototype page reads: one record per project, three checkpoints each.
Expects data/inflight_checkpoints.csv and reports/inflight_metrics_v2.json to already exist.
Only rows whose outcome is still open are used, so the counts are smaller than the raw file.
The SHAP pass over the test set is the slow part.
"""
import json, numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from lightgbm import LGBMClassifier
from sklearn.isotonic import IsotonicRegression
import shap
D="/Users/huzaifa/dissertation"
df=pd.read_csv(f"{D}/data/inflight_checkpoints.csv")
df["created"]=pd.to_datetime(df["created"],errors="coerce",utc=True)
df["planned_h"]=np.expm1(df["log_planned"])
# the validity rule. once logged hours have passed the plan the overrun is a fact, not a
# forecast, so those rows can't be shown as predictions. dropping them costs accuracy on paper.
df["determined"]=df["hours_at_cp"]>=df["planned_h"]
valid=df[~df["determined"]].copy()

# two feature sets on purpose: what was knowable at kickoff, and what the team has actually
# done since. fitting both is what lets the page show the gap between them.
EXANTE=["checkpoint","log_planned","team_prior_n","team_prior_overrun"]
BEHAV =["checkpoint","n_decl","span_days","active_days","idle_frac","decl_per_active_day",
        "hours_per_active_day","mean_gap","max_gap","std_gap","cv_gap","max_day_hours",
        "max_day_share","max_decl_hours","n_users","top_user_share","user_entropy","user_hhi"]
FULL  =sorted(set(EXANTE)|set(BEHAV)|{"hours_at_cp"})
BEH_SET=set(BEHAV)-{"checkpoint"}

LABEL={"team_prior_overrun":"Team's past overrun rate","log_planned":"Planned size","hours_at_cp":"Hours logged so far",
 "checkpoint":"Progress point","team_prior_n":"Team track-record length","hours_per_active_day":"Daily logging intensity",
 "max_decl_hours":"Largest single time entry","span_days":"Calendar span so far","max_day_hours":"Busiest day",
 "decl_per_active_day":"Entries per active day","user_hhi":"Work concentration","user_entropy":"Contributor spread",
 "top_user_share":"Top contributor's share","max_day_share":"Share of hours in busiest day","mean_gap":"Average silence gap",
 "max_gap":"Longest silence gap","std_gap":"Gap variability","cv_gap":"Logging irregularity","idle_frac":"Idle-day fraction",
 "n_users":"Contributors","n_decl":"Time entries","active_days":"Active days"}
HINT={"hours_per_active_day":"hours logged per working day","max_gap":"longest run of days with nothing logged",
 "user_hhi":"how much the effort sits with one person","idle_frac":"share of the elapsed period with no entries",
 "cv_gap":"how uneven the logging rhythm is","max_decl_hours":"biggest single entry booked",
 "span_days":"days from first entry to now","user_entropy":"how evenly work is shared","top_user_share":"largest single contributor share",
 "decl_per_active_day":"entries booked on each active day","max_day_share":"concentration of effort into one day",
 "n_users":"people booking time","n_decl":"entries booked so far","active_days":"days with any entry",
 "mean_gap":"typical spacing between entries","std_gap":"spread of those gaps","max_day_hours":"most hours in a single day"}
def fmt(f,v):
    if f=="team_prior_overrun": return f"{v*100:.0f}% of past projects"
    if f=="log_planned": return f"{np.expm1(v):.0f} h planned"
    if f in ("n_users","n_decl","active_days","team_prior_n"): return f"{int(round(v))}"
    if f in ("span_days","max_gap"):
        n=int(round(v)); return f"{n} day" + ("" if n==1 else "s")
    if f in ("hours_per_active_day",): return f"{v:.1f} h/day"
    if f in ("hours_at_cp","max_decl_hours","max_day_hours"): return f"{v:.1f} h"
    if f in ("idle_frac","max_day_share","top_user_share"): return f"{v*100:.0f}%"
    return f"{v:.2f}" if abs(v)>=0.005 else "0.00"     # avoid a displayed "-0.00"

# split on project start date, not at random. a random split puts later projects in training
# and the model then sees the future.
pc=valid.groupby("project_id")["created"].min().sort_values()
cut=pc.iloc[int(len(pc)*0.70)]; tr_ids=set(pc[pc<=cut].index)
tr=valid[valid.project_id.isin(tr_ids)].copy(); te=valid[~valid.project_id.isin(tr_ids)].copy()
# teams with no history yet fall back to the base rate, taken from train only so the
# as-of prior can't carry test outcomes into the features.
base=tr["breach"].mean()
for p in (tr,te): p["team_prior_overrun"]=p["team_prior_overrun"].fillna(base)
y=tr["breach"].values; spw=(y==0).sum()/(y==1).sum()
def mk(): return LGBMClassifier(n_estimators=600,learning_rate=.03,num_leaves=31,subsample=.8,
    colsample_bytree=.8,min_child_samples=40,scale_pos_weight=spw,random_state=42,verbose=-1)
m_full=mk().fit(tr[FULL],y); m_beh=mk().fit(tr[BEHAV],y)
# raw scores aren't probabilities and the page quotes them as percentages, so refit on the
# earlier 80% of training projects and calibrate on the slice held back. the two models above
# stay fitted on all of train, they're only used for SHAP.
tp=tr.groupby("project_id")["created"].min().sort_values(); fid=set(tp[tp<=tp.iloc[int(len(tp)*.8)]].index)
f_,c_=tr[tr.project_id.isin(fid)],tr[~tr.project_id.isin(fid)]
mf=mk().fit(f_[FULL],f_["breach"].values)
iso=IsotonicRegression(out_of_bounds="clip").fit(mf.predict_proba(c_[FULL])[:,1],c_["breach"].values)
mb=mk().fit(f_[BEHAV],f_["breach"].values)
isob=IsotonicRegression(out_of_bounds="clip").fit(mb.predict_proba(c_[BEHAV])[:,1],c_["breach"].values)

te=te.copy()
# clipped to 2-98%. nothing in this data earns the right to tell a manager something is certain.
te["p"]   = np.clip(iso.transform(mf.predict_proba(te[FULL])[:,1]),0.02,0.98)
te["pbeh"]= np.clip(isob.transform(mb.predict_proba(te[BEHAV])[:,1]),0.02,0.98)
# rank within the checkpoint, since a 25%-through project isn't comparable to a 75% one
te["pctile"]=te.groupby("checkpoint")["p"].rank(pct=True)

# shap returns a list per class on some lightgbm/shap pairings and a plain array on others
sv=shap.TreeExplainer(m_full).shap_values(te[FULL]); sv=sv[1] if isinstance(sv,list) else sv
SV=pd.DataFrame(sv,columns=FULL,index=te.index)

# portfolio: projects observed at all three checkpoints, spread across the risk range
cnt=te.groupby("project_id")["checkpoint"].nunique(); pool=cnt[cnt==3].index
mid=te[(te.project_id.isin(pool))&(te.checkpoint==0.5)].sort_values("p")
# even spacing along the sorted range, otherwise the page fills up with quiet low-risk projects
pick=list(mid.project_id.iloc[np.linspace(0,len(mid)-1,min(240,len(mid))).astype(int)])
src=pd.read_csv(f"{D}/data/gryzzly_overrun_clean.csv").set_index("id")
sub=te[te.project_id.isin(pick)]

projects=[]
for i,pid in enumerate(pick):
    rows=sub[sub.project_id==pid].sort_values("checkpoint")
    if rows.empty: continue
    cps={}
    for idx,r in rows.iterrows():
        s=SV.loc[idx]
        # keep the behavioural and context contributions apart so the live signal doesn't get
        # drowned out by "big project, shaky team", which is true but not actionable
        beh=s[[f for f in FULL if f in BEH_SET]]; ctx=s[[f for f in FULL if f in ("log_planned","team_prior_overrun","team_prior_n")]]
        def pack(series,n):
            # ranked by absolute contribution, sign only picks the arrow direction
            top=series.reindex(series.abs().sort_values(ascending=False).index).head(n)
            return [dict(k=f,label=LABEL.get(f,f),hint=HINT.get(f,""),value=fmt(f,r[f]),
                         dir=("up" if v>0 else "down"),mag=round(float(abs(v)),4)) for f,v in top.items()]
        cps[int(r.checkpoint*100)]=dict(
            p=round(float(r.p),3), pbeh=round(float(r.pbeh),3), pctile=round(float(r.pctile),3),
            behaviour=pack(beh,4), context=pack(ctx,3),
            # how much of the explanation is behaviour. epsilon guards the all-zero case.
            beh_share=round(float(beh.abs().sum()/(beh.abs().sum()+ctx.abs().sum()+1e-9)),3),
            snap=dict(n_decl=int(r.n_decl),n_users=int(r.n_users),span=int(r.span_days),
                      hpad=round(float(r.hours_per_active_day),1),maxgap=int(r.max_gap),
                      entropy=round(float(r.user_entropy),2),idle=round(float(r.idle_frac),2),
                      hours=round(float(r.hours_at_cp),1)))
    r0=rows.iloc[0]
    # code and team are made-up display labels. the real project id stays in this script.
    projects.append(dict(code=f"PRJ-{1000+i*7:04d}", team=f"Team {chr(65+i%12)}{(i//12)%9+1}",
        planned=round(float(r0.planned_h),1), team_prior=round(float(r0.team_prior_overrun),3),
        actual_breach=int(r0.breach), actual_ratio=(round(float(src.loc[pid,"ratio"]),2) if pid in src.index else None),
        checkpoints=cps))

# headline numbers come from the evaluation run rather than being recomputed here, so this
# has to be re-run whenever that json is regenerated. PR-AUC not ROC: breaches are rare enough
# that ROC-AUC looks respectable even when the model is nearly useless.
meta=json.load(open(f"{D}/reports/inflight_metrics_v2.json"))
out=dict(model=dict(pr_auc=meta["calibrated"]["PR_AUC"], pr_auc_raw=meta["results"][-1]["PR_AUC"],
    behaviour_only=meta["results"][3]["PR_AUC"], exante_only=meta["results"][2]["PR_AUC"],
    floor=meta["per_checkpoint"]["0.25"]["breach"], recall=meta["governance_recall"],
    precision=meta["governance_precision"], threshold=meta["governance_threshold"],
    projects=meta["projects"], rows=meta["valid_rows"], excluded=meta["rows_excluded_by_rule"],
    beh_share=meta["behaviour_share_of_shap"], incremental=meta["behaviour_incremental_over_exante"],
    per_cp={k:v["PR_AUC"] for k,v in meta["per_checkpoint"].items()}),
  projects=projects)
json.dump(out,open(f"{D}/prototype/prototype_data_v2.json","w"),separators=(",",":"))
import os
print(f"portfolio projects: {len(projects)}  file: {os.path.getsize(f'{D}/prototype/prototype_data_v2.json')/1024:.0f} KB")
allp=[c['p'] for p in projects for c in p['checkpoints'].values()]
print(f"probability range: {min(allp):.2f}-{max(allp):.2f} (no 0%/100% claims)")
bs=[c['beh_share'] for p in projects for c in p['checkpoints'].values()]
print(f"behaviour share of explanation: median {np.median(bs):.0%}, >50% in {np.mean(np.array(bs)>0.5):.0%} of views")
print(f"actual overrun rate in portfolio: {np.mean([p['actual_breach'] for p in projects]):.0%}")
