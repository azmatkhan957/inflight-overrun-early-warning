"""Draws figures 4, 5 and 6 into ~/dissertation/figures.
Expects reports/inflight_metrics_v3.json and data/gryzzly_overrun_clean.csv to exist already.
Agg backend, so nothing opens on screen. Runs in a few seconds.
"""
import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
D="/Users/huzaifa/dissertation"; FIG=f"{D}/figures"
NAVY="#1F3864"; TEAL="#0f4c4a"; MUT="#7aa6a3"; GOLD="#b08d57"; GREY="#8a908d"
M=json.load(open(f"{D}/reports/inflight_metrics_v3.json"))

# figure 4 is a schematic, not plotted data. every coordinate here is hand placed,
# and the rng is seeded so the declaration ticks land in the same spots on a redraw.
fig,ax=plt.subplots(figsize=(9.8,4.4)); ax.set_xlim(0,10); ax.set_ylim(0,5.0); ax.axis("off")
ax.text(5,4.72,"Constructing a checkpoint observation from the declaration stream",
        ha="center",fontsize=11.5,fontweight="bold",color=NAVY)
ax.plot([0.7,8.5],[2.6,2.6],color=GREY,lw=1.2,zorder=1)
rng=np.random.default_rng(7); xs=np.sort(rng.uniform(0.9,8.3,17))
for x in xs: ax.plot([x,x],[2.6,2.6+rng.uniform(.14,.55)],color=TEAL,lw=2.4,solid_capstyle="round",zorder=2)
ax.text(0.7,3.42,"time declarations",fontsize=8.6,color=TEAL,zorder=6)
for frac,x in zip([0.25,0.50,0.75],[3.0,5.2,7.4]):
    ax.plot([x,x],[1.62,3.32],color=NAVY,lw=1.5,ls="--",zorder=3)
    ax.add_patch(FancyBboxPatch((x-.68,1.08),1.36,.48,boxstyle="round,pad=0.02",
        lw=1.2,edgecolor=NAVY,facecolor="#e8edf6",zorder=4))
    ax.text(x,1.32,f"{int(frac*100)}% of planned",ha="center",va="center",fontsize=8.4,
            color=NAVY,fontweight="bold",zorder=5)
# bracket goes under the timeline. above it and it runs straight into the ticks
ax.annotate("",xy=(3.0,2.16),xytext=(0.75,2.16),arrowprops=dict(arrowstyle="<->",color=GOLD,lw=1.4))
ax.text(1.87,1.92,"window [0, t]: the only data a\nforecast at this checkpoint may use",
        ha="center",va="top",fontsize=8.2,color=GOLD,zorder=6)
ax.add_patch(FancyBboxPatch((8.72,2.30),1.15,.62,boxstyle="round,pad=0.02",
    lw=1.3,edgecolor="#94302c",facecolor="#fbeaea",zorder=4))
ax.text(9.30,2.61,"outcome\n(future)",ha="center",va="center",fontsize=8,
        color="#94302c",fontweight="bold",zorder=5)
ax.add_patch(FancyArrowPatch((8.52,2.6),(8.69,2.6),arrowstyle="-|>",mutation_scale=13,color="#94302c",zorder=4))
ax.text(5,0.52,"A row is retained only where cumulative effort at the checkpoint is still below the planned baseline;\n"
               "otherwise the outcome is already determined and the row is arithmetic rather than a forecast.",
        ha="center",fontsize=8.4,color="#333333")
plt.tight_layout(); plt.savefig(f"{FIG}/checkpoint_construction.png",dpi=160,bbox_inches="tight"); plt.close()

# figure 5: the cap at 4 is for the histogram only. the tail is long enough that
# without it every bar but the first collapses. right panel keeps the raw values and goes log.
d=pd.read_csv(f"{D}/data/gryzzly_overrun_clean.csv")
r=d["ratio"].clip(upper=4)
fig,ax=plt.subplots(1,2,figsize=(10.4,3.9))
ax[0].hist(r,bins=70,color=TEAL,edgecolor="white",linewidth=.3)
ax[0].axvline(1.0,color="#94302c",ls="--",lw=1.5,label="planned-hours baseline")
ax[0].set(title="Distribution of actual / planned effort",xlabel="ratio (capped at 4)",ylabel="projects")
ax[0].legend(fontsize=8)
q=np.linspace(.5,.999,220); ax[1].plot(q*100,d["ratio"].quantile(q).values,color=TEAL,lw=1.8)
ax[1].axhline(1.0,color="#94302c",ls="--",lw=1.2)
ax[1].set(title="Upper tail of the same distribution",xlabel="percentile",ylabel="actual / planned",yscale="log")
ax[1].text(52,d["ratio"].quantile(.999)*.35,f"overall overrun rate {(d.ratio>1).mean():.3f}",fontsize=8.6,color="#333333")
plt.tight_layout(); plt.savefig(f"{FIG}/overrun_distribution.png",dpi=160,bbox_inches="tight"); plt.close()

# figure 6: PR-AUC moves with prevalence, so the left curve is not comparable across
# checkpoints on its own. right panel divides each point by that checkpoint's own floor.
per=M["per_checkpoint"]; ks=sorted(per,key=float); x=[int(float(k)*100) for k in ks]
ap=[per[k]["PR_AUC"] for k in ks]; fl=[per[k]["floor"] for k in ks]; lift=[per[k]["lift"] for k in ks]
fig,ax=plt.subplots(1,2,figsize=(10.6,3.9))
ax[0].plot(x,ap,"o-",color=TEAL,lw=2,label="PR-AUC (full model)")
ax[0].plot(x,fl,"s--",color=GREY,lw=1.6,label="prevalence floor at that checkpoint")
ax[0].fill_between(x,fl,ap,color=TEAL,alpha=.10)
ax[0].set(title="Raw PR-AUC rises, but so does prevalence",xlabel="% of planned effort used",ylabel="PR-AUC")
ax[0].legend(fontsize=8); ax[0].set_ylim(0.2,0.7)
ax[1].plot(x,lift,"o-",color="#94302c",lw=2)
ax[1].axhline(1.0,color=GREY,ls=":",lw=1.2); ax[1].set_ylim(0.9,1.6)
for xi,li in zip(x,lift): ax[1].annotate(f"{li:.2f}x",(xi,li),textcoords="offset points",xytext=(0,8),ha="center",fontsize=9)
ax[1].set(title="Lift over each checkpoint's own floor declines",xlabel="% of planned effort used",ylabel="PR-AUC / floor")
plt.tight_layout(); plt.savefig(f"{FIG}/checkpoint_performance.png",dpi=160,bbox_inches="tight"); plt.close()
print("wrote checkpoint_construction.png, overrun_distribution.png, checkpoint_performance.png")
