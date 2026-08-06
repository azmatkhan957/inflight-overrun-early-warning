"""
Builds the checkpoint table: one row per (project, checkpoint) at 25/50/75% of the planned
budget, with features computed only from the declarations up to that point.
Label is the final outcome (elapsed > planned), which is the only thing here that looks ahead.
Reads the full declaration export, so expect a few minutes on 4.4M rows.
"""
import re, sys, numpy as np, pandas as pd
DATA="/Users/huzaifa/dissertation/data"
DECL = f"{DATA}/declarations_full.csv"
CHECKPOINTS = [0.25, 0.50, 0.75]

def dur_to_h(s):
    if not isinstance(s, str): return np.nan
    h=re.search(r'([\d.]+)h',s); m=re.search(r'([\d.]+)m',s); sec=re.search(r'([\d.]+)s',s)
    t=0.0
    if h: t+=float(h.group(1))
    if m: t+=float(m.group(1))/60
    if sec: t+=float(sec.group(1))/3600
    return t

def shannon(shares):
    p=shares[shares>0]
    return float(-(p*np.log(p)).sum()) if len(p) else 0.0

# only projects with a planned baseline: without one there is nothing to overrun
proj=pd.read_csv(f"{DATA}/gryzzly_overrun_clean.csv")
proj["created"]=pd.to_datetime(proj["created_at"], errors="coerce", utc=True)
proj=proj[(proj["planned_h"]>0)&proj["created"].notna()].copy()
proj["breach"]=(proj["ratio"]>1.0).astype(int)
planned=dict(zip(proj.id, proj.planned_h))
usable=set(proj.id)
print(f"usable projects (planned baseline): {len(usable):,} | overrun rate {proj.breach.mean():.3f}")

# team track record as of the project's creation date. shift() before expanding() so a project
# never contributes to its own prior, and the sort makes "prior" mean earlier in time.
proj=proj.sort_values("created")
g=proj.groupby("team_id")
proj["team_prior_n"]=g.cumcount()
proj["team_prior_overrun"]=g["breach"].apply(lambda s:s.shift().expanding().mean()).reset_index(level=0,drop=True)
prior_map_n=dict(zip(proj.id, proj.team_prior_n))
prior_map_r=dict(zip(proj.id, proj.team_prior_overrun))
meta=proj.set_index("id")[["created","team_id","planned_h","ratio","breach"]]

# declarations only carry task_id, so hop through tasks to reach the project
tasks=pd.read_csv(f"{DATA}/tasks.csv", usecols=["id","project_id"])
t2p=dict(zip(tasks.id, tasks.project_id))
print(f"tasks: {len(tasks):,}")

print("reading full declarations ...", flush=True)
dec=pd.read_csv(DECL, usecols=["date","duration","user_id","task_id"])
print(f"declarations: {len(dec):,}")
# two flavours of duration exist in the exports: raw nanoseconds, or a string like '3h 20m'
if np.issubdtype(dec["duration"].dtype, np.number):
    dec["hours"]=dec["duration"].astype("float64")/3.6e12     # ns -> h
else:
    dec["hours"]=dec["duration"].map(dur_to_h)
dec["project_id"]=dec["task_id"].map(t2p)
dec["date"]=pd.to_datetime(dec["date"], errors="coerce")
dec=dec.dropna(subset=["project_id","date","hours"])
dec=dec[dec["project_id"].isin(usable) & (dec["hours"]>0)].copy()
print(f"declarations mapped to usable projects: {len(dec):,} across {dec.project_id.nunique():,} projects")

# sanity check before anything is built on top: the declaration stream should roughly
# reconstruct the elapsed hours the platform reports. a low ratio means missing time entries.
tot=dec.groupby("project_id")["hours"].sum()
cov=pd.DataFrame({"decl_h":tot}).join(proj.set_index("id")[["elapsed_h","planned_h"]], how="inner")
cov["cov_ratio"]=cov["decl_h"]/cov["elapsed_h"].replace(0,np.nan)
print(f"coverage (declared hrs / authoritative elapsed hrs): median {cov.cov_ratio.median():.2f}, "
      f"within [0.8,1.25]: {cov.cov_ratio.between(0.8,1.25).mean():.1%}")

# one pass per project, snapshotting the stream at each checkpoint. this is the slow bit.
dec=dec.sort_values(["project_id","date"])
rows=[]
for pid, grp in dec.groupby("project_id", sort=False):
    P=planned.get(pid)
    if not P or P<=0: continue
    d=grp[["date","hours","user_id"]].reset_index(drop=True)
    d["cum"]=d["hours"].cumsum()
    tot_h=d["cum"].iloc[-1]
    for c in CHECKPOINTS:
        thr=c*P
        if tot_h < thr:            # never burned this much of the budget, so no checkpoint here
            continue
        idx=int(np.searchsorted(d["cum"].values, thr, side="left"))
        w=d.iloc[:idx+1]           # inclusive of the crossing declaration, nothing after it
        n=len(w)
        days=w["date"]
        span=(days.max()-days.min()).days + 1
        active=days.dt.normalize().nunique()
        # gaps are between distinct active days, not between declarations: a busy day can hold
        # a dozen entries and that is not a rhythm signal
        ad=np.sort(days.dt.normalize().unique())
        gaps=np.diff(ad).astype("timedelta64[D]").astype(float) if len(ad)>1 else np.array([0.0])
        byday=w.groupby(days.dt.normalize())["hours"].sum()
        hrs=w["hours"].sum()
        byuser=w.groupby("user_id")["hours"].sum(); ushare=(byuser/byuser.sum()).values
        rows.append(dict(
            project_id=pid, checkpoint=c,
            cp_date=w["date"].max(), end_date=d["date"].max(),
            n_decl=n, span_days=span, active_days=active,
            idle_frac=float(1-active/span) if span>0 else 0.0,
            decl_per_active_day=n/active if active>0 else 0.0,
            hours_at_cp=float(hrs), hours_per_active_day=float(hrs/active) if active>0 else 0.0,
            mean_gap=float(gaps.mean()), max_gap=float(gaps.max()), std_gap=float(gaps.std()),
            cv_gap=float(gaps.std()/gaps.mean()) if gaps.mean()>0 else 0.0,
            max_day_hours=float(byday.max()), max_day_share=float(byday.max()/hrs) if hrs>0 else 0.0,
            max_decl_hours=float(w["hours"].max()),
            n_users=int(byuser.size), top_user_share=float(ushare.max()),
            user_entropy=shannon(ushare), user_hhi=float((ushare**2).sum()),
            log_planned=float(np.log1p(P)), planned_h=float(P),
            team_prior_n=float(prior_map_n.get(pid, 0)),
            team_prior_overrun=float(prior_map_r.get(pid, np.nan)),
            created=meta.loc[pid,"created"], team_id=meta.loc[pid,"team_id"],
            breach=int(meta.loc[pid,"breach"]),
        ))

df=pd.DataFrame(rows)
print(f"\ncheckpoint rows: {len(df):,} across {df.project_id.nunique():,} projects")
print("per-checkpoint counts & breach rate:")
print(df.groupby("checkpoint").agg(n=("breach","size"), breach_rate=("breach","mean")).round(3).to_string())
df.to_csv(f"{DATA}/inflight_checkpoints_v2.csv", index=False)
print(f"\nsaved -> {DATA}/inflight_checkpoints_v2.csv")
