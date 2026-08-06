# In-Flight Overrun Early-Warning System

Computing artefact accompanying the MSc dissertation *A Behavioural Early-Warning Model of
In-Flight Effort Overrun in SME Service Projects: A Leakage-Controlled Machine-Learning
Approach Using the Gryzzly Time-Declaration Dataset*.

MSc Information Technology with Project Management, University of the West of Scotland.

| | |
|---|---|
| Muhammad Athar Rehan | B01822447 |
| Muhammad Yahya Moeen | B01834191 |
| Azmat Khan (group leader) | B01828957 |
| Muhammad Hamaish Naeem | B01834617 |

## What this does

Small and medium-sized service firms rarely maintain the costed baseline that earned value
management presupposes, so they have no instrument that warns them a live project is heading
past its planned hours. This artefact forecasts that breach from the only trace such firms
reliably keep: the time-declaration log.

At 25, 50 and 75 per cent of planned effort consumed, it reads behavioural signals from the
declarations booked so far, which is logging rhythm, silence gaps, contributor concentration
and burst intensity, and returns a calibrated probability that the project will exceed its
planned-hours baseline. The probability is then translated into a PRINCE2 exception report.

## Headline results

Evaluated on a deployment-realistic split: train on projects whose outcome was known by a
wall-clock decision date, score only checkpoints occurring after it.

| Model | Features | PR-AUC | ROC-AUC | Brier |
|---|---|---|---|---|
| Prevalence floor | none | 0.364 | 0.500 | 0.241 |
| Ex-ante | size + as-of team history | 0.477 | 0.631 | 0.229 |
| Behaviour only | declaration stream | 0.466 | 0.619 | 0.236 |
| **Full** | **both** | **0.520** | **0.676** | **0.216** |

Behavioural signals add **+0.043 PR-AUC** over an honestly constructed ex-ante baseline.
95% confidence interval for the full model, bootstrapped clustered by project: [0.496, 0.548].

**An honest caveat that the dissertation makes prominently.** Raw PR-AUC rises across the
three checkpoints (0.436, 0.496, 0.603), but so does breach prevalence (0.298, 0.364, 0.460).
Measured as lift over each checkpoint's own floor, performance *declines* (1.46x, 1.36x,
1.31x). The instrument is therefore most useful **earliest**, which is also where a warning is
worth most. Any claim that it sharpens as a project unfolds would be an artefact of prevalence.

## Leakage control

The protocol exists because an earlier version of this pipeline scored higher and was wrong.
An adversarial audit produced 51 verified findings and forced three corrections:

1. **Already-determined outcomes.** A checkpoint is a genuine forecast only if effort consumed
   is still below the planned baseline. Where it is not, "prediction" is arithmetic. This
   removes 8.9 per cent of rows.
2. **The team-history feature.** Previously an expanding mean over projects ordered by
   *creation* date, so it consumed outcomes not yet knowable. Rebuilt as-of the checkpoint: a
   prior project counts only if it finished strictly before the observation.
3. **The train/test split.** Previously by creation date, so roughly a quarter of training
   labels did not exist at the cut. Replaced with a wall-clock decision date.

Together these moved the headline from an inflated 0.593 to an honest **0.520**. The behaviour
increment survived, and slightly strengthened, because the leakage sat in the ex-ante branch.

## Reproducing

The dataset is not redistributed here. Download it from figshare
([10.6084/m9.figshare.28114247](https://doi.org/10.6084/m9.figshare.28114247), CC BY 4.0) and
place `declarations.csv`, `tasks.csv` and `projects_computed.csv` in `data/`.

```bash
pip install -r requirements.txt
python analysis/inflight_features_v2.py   # declarations -> checkpoint observations
python analysis/inflight_model_v3.py      # model, evaluation, calibration, SHAP
python analysis/figures_v3.py             # dissertation figures
python prototype/export_v2.py             # model outputs for the prototype
python prototype/build_v3.py              # build the self-contained prototype page
```

`inflight_features_v2.py` takes a few minutes over the 4.4 million declarations; the rest run
in under a minute. Metrics are written to `reports/inflight_metrics_v3.json`.

## The prototype

`prototype/inflight_earlywarning.html` is a single self-contained page with no server or
build step. Open it in a browser, or see the running instance at http://45.32.176.169.

It shows a portfolio of held-out projects with their forecast at each checkpoint, separates
the behavioural signal from what track record and project size alone imply, explains each flag
through SHAP attributions, and drafts a PRINCE2 exception report for any project over
tolerance. The tolerance defaults to 0.60 rather than the statistical max-F1 point of 0.41,
because maximising F1 flags roughly two-thirds of the portfolio, more than a project office
can review; setting it by review capacity keeps the alert list workable.

## Layout

```
analysis/    feature engineering, model, evaluation, figures
prototype/   data export, page builder, the self-contained artefact
reports/     metrics produced by the pipeline
figures/     figures used in the dissertation
```

## Use of this code

This repository accompanies an MSc dissertation submitted to the University of the West of
Scotland and is published so the work can be read and verified. No licence is granted, so all
rights are reserved by the authors; please get in touch before reusing the code.

The Gryzzly dataset is the work of its authors and is licensed CC BY 4.0; see `CITATION.md`.
