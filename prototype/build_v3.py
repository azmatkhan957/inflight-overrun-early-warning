# -*- coding: utf-8 -*-
"""Builds the standalone prototype page: one CSS/JS template with the data inlined at __DATA__.
Input is prototype_data_v2.json; v3 re-skinned it as a governance document rather than a
dashboard, the numbers are still v2's. Writes a body fragment and a full page into D, which is a
hard-coded absolute path."""
import json
D="/Users/huzaifa/dissertation/prototype"
data=json.load(open(f"{D}/prototype_data_v2.json"))

BODY = r"""
<style>
:root{
  --paper:#eceeec; --plane:#f7f8f7; --sunk:#e3e6e4; --rule:#c9cfcb; --rule-2:#dde2df;
  --ink:#141816; --ink-2:#414a45; --ink-3:#6d7873;
  --sig:#0f4c4a; --sig-2:#12605d; --sig-wash:#dde8e6;
  --ok:#2c6144; --warn:#8a5a12; --crit:#94302c;
  --ok-w:#dde7de; --warn-w:#f0e5cf; --crit-w:#f0dcda;
  --mono:ui-monospace,"SF Mono",SFMono-Regular,Menlo,"DejaVu Sans Mono",Consolas,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
@media (prefers-color-scheme:dark){:root{
  --paper:#0f1211; --plane:#161a19; --sunk:#1c2120; --rule:#2c3432; --rule-2:#232a29;
  --ink:#e6ebe8; --ink-2:#b0bab6; --ink-3:#7d8a88;
  --sig:#5fb3ad; --sig-2:#7cc9c3; --sig-wash:#14302e;
  --ok:#63b487; --warn:#d19b46; --crit:#e08079;
  --ok-w:#15271d; --warn-w:#2a2114; --crit-w:#2b1817;
}}
:root[data-theme="dark"]{
  --paper:#0f1211; --plane:#161a19; --sunk:#1c2120; --rule:#2c3432; --rule-2:#232a29;
  --ink:#e6ebe8; --ink-2:#b0bab6; --ink-3:#7d8a88;
  --sig:#5fb3ad; --sig-2:#7cc9c3; --sig-wash:#14302e;
  --ok:#63b487; --warn:#d19b46; --crit:#e08079;
  --ok-w:#15271d; --warn-w:#2a2114; --crit-w:#2b1817;
}
:root[data-theme="light"]{
  --paper:#eceeec; --plane:#f7f8f7; --sunk:#e3e6e4; --rule:#c9cfcb; --rule-2:#dde2df;
  --ink:#141816; --ink-2:#414a45; --ink-3:#6d7873;
  --sig:#0f4c4a; --sig-2:#12605d; --sig-wash:#dde8e6;
  --ok:#2c6144; --warn:#8a5a12; --crit:#94302c;
  --ok-w:#dde7de; --warn-w:#f0e5cf; --crit-w:#f0dcda;
}
#ews *{box-sizing:border-box}
#ews{font-family:var(--sans);background:var(--paper);color:var(--ink);min-height:100vh;
  font-size:13.5px;line-height:1.45;font-variant-numeric:tabular-nums;padding-bottom:40px}
#ews :focus-visible{outline:2px solid var(--sig);outline-offset:1px}
@media (prefers-reduced-motion:reduce){#ews *{transition:none!important}}
#ews .mono{font-family:var(--mono)}
#ews .cap{font-family:var(--mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;
  color:var(--ink-3);font-weight:500}

/* ---- masthead: a document header, not a hero ---- */
#ews .head{border-bottom:2px solid var(--ink);padding:16px 22px 11px;display:flex;
  justify-content:space-between;align-items:flex-end;gap:20px;flex-wrap:wrap;background:var(--plane)}
#ews .head .ttl{font-size:17px;font-weight:650;letter-spacing:-.01em;margin:2px 0 3px}
#ews .head .desc{color:var(--ink-2);font-size:12.5px;max-width:66ch}
#ews .head .ref{font-family:var(--mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--sig)}
#ews .spec{display:flex;gap:0;border:1px solid var(--rule);background:var(--plane)}
#ews .spec div{padding:5px 11px;border-right:1px solid var(--rule-2)}
#ews .spec div:last-child{border-right:0}
#ews .spec .k{font-family:var(--mono);font-size:9px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-3)}
#ews .spec .v{font-family:var(--mono);font-size:13px;font-weight:600;color:var(--ink)}
#ews .tbtn{font-family:var(--mono);font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;
  background:none;border:1px solid var(--rule);color:var(--ink-2);padding:6px 10px;cursor:pointer}
#ews .tbtn:hover{border-color:var(--sig);color:var(--sig)}

/* ---- control strip ---- */
#ews .controls{display:flex;gap:26px;align-items:flex-end;flex-wrap:wrap;padding:12px 22px;
  background:var(--plane);border-bottom:1px solid var(--rule)}
#ews .ctl{display:flex;flex-direction:column;gap:5px}
#ews .ctl>label,#ews .ctl>.cap{margin-bottom:1px}
#ews .hint{font-size:11px;color:var(--ink-3);margin-top:2px}
#ews .seg{display:inline-flex;border:1px solid var(--rule)}
#ews .seg button{font-family:var(--mono);border:0;border-right:1px solid var(--rule);background:transparent;
  padding:6px 13px;font-size:12px;color:var(--ink-3);cursor:pointer;font-weight:500}
#ews .seg button:last-child{border-right:0}
#ews .seg button[aria-pressed="true"]{background:var(--sig);color:var(--plane);font-weight:600}
#ews select,#ews input[type=search]{font-family:var(--sans);border:1px solid var(--rule);background:var(--plane);
  color:var(--ink);padding:6px 9px;font-size:12.5px;border-radius:0}
#ews input[type=search]{min-width:190px}
#ews input[type=range]{accent-color:var(--sig);width:140px}
#ews .tolrow{display:flex;align-items:center;gap:10px}
#ews .tolv{font-family:var(--mono);font-size:15px;font-weight:600;color:var(--sig);min-width:36px}
#ews .key{display:flex;gap:14px;margin-left:auto;align-items:center;font-size:11.5px;color:var(--ink-3)}
#ews .sw{width:10px;height:10px;display:inline-block;margin-right:5px;vertical-align:-1px}
#ews .s-ok{background:var(--ok)} #ews .s-warn{background:var(--warn)} #ews .s-crit{background:var(--crit)}

/* ---- readout: one continuous instrument strip, not four cards ---- */
#ews .readout{display:flex;flex-wrap:wrap;border-bottom:1px solid var(--rule);background:var(--sunk)}
#ews .readout .cell{flex:1 1 190px;padding:11px 22px;border-right:1px solid var(--rule-2)}
#ews .readout .cell:last-child{border-right:0}
#ews .readout .v{font-family:var(--mono);font-size:25px;font-weight:600;letter-spacing:-.02em;line-height:1.1}
#ews .readout .n{font-size:11.5px;color:var(--ink-3);margin-top:2px}
#ews .readout .crit .v{color:var(--crit)} #ews .readout .ok .v{color:var(--ok)}

/* ---- panels ---- */
#ews .cols{display:grid;grid-template-columns:minmax(0,1.02fr) minmax(0,.98fr);align-items:start}
@media(max-width:1040px){#ews .cols{grid-template-columns:1fr}}
#ews .col{border-right:1px solid var(--rule)}
#ews .col:last-child{border-right:0}
#ews .colhead{padding:9px 22px;border-bottom:1px solid var(--rule);display:flex;
  justify-content:space-between;align-items:center;background:var(--plane)}
#ews .scroll{max-height:600px;overflow:auto;overscroll-behavior:contain}
#ews .scroll:focus-visible{outline:2px solid var(--sig);outline-offset:-2px}
#ews table{width:100%;border-collapse:collapse}
#ews thead th{font-family:var(--mono);font-size:9.5px;letter-spacing:.07em;text-transform:uppercase;
  color:var(--ink-3);font-weight:500;text-align:left;padding:7px 10px;background:var(--plane);
  border-bottom:1px solid var(--rule);position:sticky;top:0;z-index:1;cursor:pointer;user-select:none}
#ews thead th:first-child{padding-left:22px}
#ews th.num,#ews td.num{text-align:right}
#ews tbody td{padding:7px 10px;border-bottom:1px solid var(--rule-2);font-size:12.5px}
#ews tbody td:first-child{padding-left:22px}
#ews tbody tr{cursor:pointer}
#ews tbody tr:hover td{background:var(--sunk)}
#ews tbody tr[aria-selected="true"] td{background:var(--sig-wash);
  box-shadow:inset 0 -1px 0 var(--rule)}
#ews tbody tr[aria-selected="true"] td:first-child{box-shadow:inset 3px 0 0 var(--sig),inset 0 -1px 0 var(--rule)}
#ews td.code{font-family:var(--mono);font-weight:600;font-size:12.5px}
#ews .num-mono{font-family:var(--mono)}
#ews .flag{font-family:var(--mono);font-size:10.5px;letter-spacing:.04em;text-transform:uppercase;font-weight:600}
#ews .f-ok{color:var(--ok)} #ews .f-warn{color:var(--warn)} #ews .f-crit{color:var(--crit)}
/* scale with a real tolerance mark */
#ews .scale{position:relative;height:4px;background:var(--sunk);margin-top:4px;min-width:74px;
  border:1px solid var(--rule-2);border-left:0;border-right:0}
#ews .scale>i{position:absolute;left:0;top:0;bottom:0;display:block}
#ews .scale>b{position:absolute;top:-3px;bottom:-3px;width:1px;background:var(--ink-2)}

/* ---- detail ---- */
#ews .detail{padding:14px 22px 22px}
#ews .dtop{border-bottom:1px solid var(--rule);padding-bottom:9px;margin-bottom:12px}
#ews .dtop .id{font-family:var(--mono);font-size:18px;font-weight:600;letter-spacing:-.01em}
#ews .dtop .meta{font-size:12px;color:var(--ink-3);margin-top:2px}
#ews .pair{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--rule);margin-bottom:11px}
#ews .pair>div{padding:10px 13px}
#ews .pair>div:first-child{border-right:1px solid var(--rule)}
#ews .pair .v{font-family:var(--mono);font-size:29px;font-weight:600;letter-spacing:-.025em;line-height:1.1}
#ews .pair .n{font-size:11px;color:var(--ink-3);margin-top:1px}
#ews .diverge{border-left:2px solid var(--sig);padding:8px 12px;background:var(--sig-wash);
  font-size:12.5px;color:var(--ink-2);margin-bottom:12px}
#ews .diverge b{color:var(--sig)}
#ews .diverge .cap{display:block;margin-bottom:3px}
#ews .diverge.hot{border-left-color:var(--crit);background:var(--crit-w)}
#ews .diverge.hot b,#ews .diverge.hot .cap{color:var(--crit)}
#ews .diverge.calm{border-left-color:var(--ok);background:var(--ok-w)}
#ews .diverge.calm b,#ews .diverge.calm .cap{color:var(--ok)}
#ews .diverge.agree{border-left-color:var(--ink-3);background:var(--sunk)}
#ews .diverge.agree b{color:var(--ink)} #ews .diverge.agree .cap{color:var(--ink-3)}
#ews .trk{display:grid;grid-template-columns:1fr 1fr 1fr;border:1px solid var(--rule)}
#ews .trk .c{padding:8px 4px;text-align:center;border-right:1px solid var(--rule-2)}
#ews .trk .c:last-child{border-right:0}
#ews .trk .c[aria-current="true"]{background:var(--sig-wash);box-shadow:inset 0 -2px 0 var(--sig)}
#ews .trk .c .v{font-family:var(--mono);font-size:17px;font-weight:600}
#ews .sec{display:flex;justify-content:space-between;align-items:baseline;
  border-bottom:1px solid var(--rule);padding-bottom:4px;margin:18px 0 9px}
#ews .drv{display:grid;grid-template-columns:12px 1fr 66px;gap:9px;align-items:center;
  padding:5px 0;border-bottom:1px dotted var(--rule-2)}
#ews .drv:last-of-type{border-bottom:0}
#ews .drv .ar{font-family:var(--mono);font-weight:700;text-align:center;font-size:11px}
#ews .drv .ar.up{color:var(--crit)} #ews .drv .ar.down{color:var(--ok)}
#ews .drv .t{font-size:12.5px;font-weight:600}
#ews .drv .t em{font-style:normal;font-family:var(--mono);color:var(--ink-2);font-weight:500;font-size:12px}
#ews .drv .h{font-size:11px;color:var(--ink-3);display:block;font-weight:400}
#ews .drv .b{height:3px;background:var(--sunk)}
#ews .drv .b>span{display:block;height:100%}
#ews .snap{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid var(--rule)}
#ews .snap>div{padding:7px 11px;border-right:1px solid var(--rule-2);border-bottom:1px solid var(--rule-2)}
#ews .snap>div:nth-child(3n){border-right:0}
#ews .snap>div:nth-last-child(-n+3){border-bottom:0}
#ews .snap .v{font-family:var(--mono);font-size:15px;font-weight:600;margin-top:1px}

/* ---- exception report as a ruled form ---- */
#ews .form{border:1px solid var(--ink);margin-top:18px;background:var(--plane)}
#ews .form.clear{border-color:var(--rule)}
#ews .form>header{border-bottom:1px solid var(--ink);padding:8px 13px;display:flex;
  justify-content:space-between;align-items:center;gap:10px}
#ews .form.raised>header{background:var(--crit-w)}
#ews .form.clear>header{background:var(--ok-w);border-bottom-color:var(--rule)}
#ews .form>header .t{font-family:var(--mono);font-size:11px;letter-spacing:.09em;text-transform:uppercase;font-weight:600}
#ews .form.raised>header .t{color:var(--crit)} #ews .form.clear>header .t{color:var(--ok)}
#ews .form dl{margin:0}
#ews .form .fr{display:grid;grid-template-columns:104px 1fr;border-bottom:1px dotted var(--rule-2)}
#ews .form .fr:last-child{border-bottom:0}
#ews .form dt{font-family:var(--mono);font-size:9.5px;letter-spacing:.06em;text-transform:uppercase;
  color:var(--ink-3);padding:8px 10px 8px 13px;border-right:1px solid var(--rule-2);font-weight:500}
#ews .form dd{margin:0;padding:8px 13px;font-size:12.5px}
#ews .form ol{margin:0;padding-left:16px} #ews .form li{margin-bottom:2px}
#ews .btn{font-family:var(--mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;
  border:1px solid var(--rule);background:var(--plane);color:var(--ink-2);padding:4px 9px;cursor:pointer}
#ews .btn:hover{border-color:var(--sig);color:var(--sig)}
#ews .reveal{margin-top:13px}
#ews .reveal .out{margin-top:7px;padding:9px 12px;background:var(--sunk);border-left:2px solid var(--ink-3);font-size:12.5px}
#ews .empty{padding:28px 22px;text-align:center;color:var(--ink-3)}
#ews .foot{padding:14px 22px 0;border-top:1px solid var(--rule);margin-top:0;color:var(--ink-3);
  font-size:11.5px;line-height:1.7;max-width:118ch}
#ews .foot b{color:var(--ink-2);font-weight:600}

/* ================= small screens =================
   The portfolio stops being a table and becomes one record per card, because six
   columns cannot survive a phone. Everything else tightens rather than shrinks. */
@media (max-width:760px){
  #ews{font-size:14px}
  #ews .head,#ews .controls,#ews .colhead,#ews .detail,#ews .foot{padding-left:14px;padding-right:14px}
  #ews .readout .cell{padding:10px 14px}

  /* masthead stacks; the spec strip spans the width instead of forcing overflow */
  #ews .head{flex-direction:column;align-items:stretch;gap:11px;padding-top:14px}
  #ews .head .desc{max-width:none}
  #ews .head>div:last-child{display:flex;gap:9px;align-items:stretch}
  #ews .spec{flex:1;min-width:0}
  #ews .spec div{flex:1;min-width:0;padding:5px 4px;text-align:center}
  #ews .spec .v{font-size:12px}

  /* controls: a 2-up grid so the preamble does not eat a whole screen.
     The checkpoint segment and the tolerance slider need full width; the
     materiality floor and the search box sit side by side. */
  #ews .controls{display:grid;grid-template-columns:1fr 1fr;gap:11px 10px;
    padding-top:11px;padding-bottom:11px;align-items:end}
  #ews .ctl{width:auto;min-width:0}
  #ews .ctl:nth-of-type(1),#ews .ctl:nth-of-type(2){grid-column:1/-1}
  #ews .ctl:nth-of-type(3) .hint,#ews .ctl:nth-of-type(4) .hint{display:none}
  #ews .key{grid-column:1/-1}
  /* touch targets: 44px minimum, and 16px text so iOS Safari does not auto-zoom on focus */
  #ews .seg{width:100%} #ews .seg button{flex:1;padding:0;min-height:44px;font-size:13px}
  #ews select,#ews input[type=search]{width:100%;min-width:0;min-height:44px;padding:10px 11px;font-size:16px}
  #ews .tbtn{min-height:44px;padding:0 14px}
  #ews .btn{min-height:38px;padding:0 12px}
  #ews .tolrow{width:100%;min-height:44px}
  #ews input[type=range]{flex:1;width:auto;min-width:0;height:44px}
  #ews .key{margin-left:0;width:100%;flex-wrap:wrap;gap:8px 14px}

  /* readout as a 2x2 block rather than four full-height bands */
  #ews .readout .cell{flex:1 1 50%;min-width:0;border-bottom:1px solid var(--rule-2)}
  #ews .readout .cell:nth-child(2n){border-right:0}
  #ews .readout .cell:nth-last-child(-n+2){border-bottom:0}
  #ews .readout .v{font-size:21px}
  #ews .readout .n{font-size:10.5px}

  /* portfolio: table -> stacked records */
  #ews .col{border-right:0;border-bottom:1px solid var(--rule)}
  /* keep the list in its own scroll window so the controls above and the detail
     below stay reachable instead of sitting 192 records apart */
  #ews .scroll{max-height:58vh;min-height:260px;overflow-y:auto;overscroll-behavior:contain;
    -webkit-overflow-scrolling:touch}
  #ews thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
  #ews table,#ews tbody,#ews tr,#ews td{display:block;width:auto}
  #ews tbody tr{display:grid;grid-template-columns:1fr 1fr;grid-template-areas:
      "code status" "meta plan" "fc beh";
    gap:3px 12px;padding:11px 14px;border-bottom:1px solid var(--rule-2)}
  #ews tbody tr:hover td{background:none}
  #ews tbody tr[aria-selected="true"]{background:var(--sig-wash);
    box-shadow:inset 3px 0 0 var(--sig)}
  #ews tbody tr[aria-selected="true"] td{background:none;box-shadow:none}
  #ews tbody td{padding:0;border:0;text-align:left}
  #ews tbody td:first-child{padding-left:0}
  #ews tbody td:nth-child(1){grid-area:code;font-size:14px}
  #ews tbody td:nth-child(2){grid-area:meta;color:var(--ink-3);font-size:12px}
  #ews tbody td:nth-child(3){grid-area:plan;color:var(--ink-3);font-size:12px;text-align:right}
  #ews tbody td:nth-child(4){grid-area:fc}
  #ews tbody td:nth-child(5){grid-area:beh}
  #ews tbody td:nth-child(6){grid-area:status;text-align:right}
  #ews tbody td:nth-child(4)::before{content:"Forecast";display:block;font-family:var(--mono);
    font-size:9px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);margin-bottom:1px}
  #ews tbody td:nth-child(5)::before{content:"Behaviour";display:block;font-family:var(--mono);
    font-size:9px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);margin-bottom:1px}
  #ews .scale{min-width:0}

  /* detail: let the wide blocks breathe */
  #ews .snap{grid-template-columns:1fr 1fr}
  #ews .snap>div:nth-child(3n){border-right:1px solid var(--rule-2)}
  #ews .snap>div:nth-child(2n){border-right:0}
  #ews .snap>div:nth-last-child(-n+2){border-bottom:0}
  #ews .snap>div:nth-child(5){border-bottom:1px solid var(--rule-2)}
  #ews .pair .v{font-size:25px}
  #ews .form .fr{grid-template-columns:1fr}
  #ews .form dt{border-right:0;border-bottom:1px dotted var(--rule-2);padding:6px 13px 4px}
  #ews .form dd{padding-top:6px}
  #ews .trk .c .v{font-size:15px}
  #ews .drv{grid-template-columns:12px 1fr;gap:8px}
  #ews .drv .b{grid-column:2;height:3px}
}
@media (max-width:380px){
  #ews .spec .k{font-size:8px} #ews .spec .v{font-size:11px}
  #ews .readout .v{font-size:19px}
}
</style>

<div id="ews">
  <div class="head">
    <div>
      <div class="ref">Design-science artefact: working prototype</div>
      <div class="ttl">In-Flight Overrun Early-Warning System</div>
      <div class="desc">Forecasts whether a live project will breach its planned-hours baseline, read from
        time-declaration behaviour at fixed effort checkpoints, and converts the forecast into PRINCE2
        management-by-exception.</div>
    </div>
    <div style="display:flex;gap:10px;align-items:center">
      <div class="spec" id="spec"></div><span id="themeslot"></span></div>
  </div>

  <div class="controls">
    <div class="ctl"><span class="cap" id="cpl">Checkpoint: planned effort used</span>
      <div class="seg" role="group" aria-labelledby="cpl" id="seg"></div></div>
    <div class="ctl"><label class="cap" for="tol">PRINCE2 tolerance</label>
      <div class="tolrow"><input id="tol" type="range" min="0.15" max="0.85" step="0.01" value="0.60">
        <span class="tolv" id="tolv">0.60</span></div>
      <span class="hint">Escalate when forecast &ge; tolerance</span></div>
    <div class="ctl"><label class="cap" for="mat">Materiality floor</label>
      <select id="mat"><option value="0">All projects</option><option value="4">&ge; 4 h planned</option>
        <option value="8" selected>&ge; 8 h planned</option><option value="16">&ge; 16 h planned</option>
        <option value="40">&ge; 40 h planned</option></select>
      <span class="hint">Below this, too small to govern by exception</span></div>
    <div class="ctl"><label class="cap" for="q">Find project or team</label>
      <input id="q" type="search" placeholder="PRJ-1042 / Team C" autocomplete="off"></div>
    <div class="key"><span><i class="sw s-ok"></i>Within tolerance</span>
      <span><i class="sw s-warn"></i>Approaching</span><span><i class="sw s-crit"></i>Exception</span></div>
  </div>

  <div class="readout" id="readout"></div>

  <div class="cols">
    <section class="col" aria-label="Project portfolio">
      <div class="colhead"><span class="cap">Portfolio: forecast at <span id="cptitle">50%</span> effort</span>
        <span class="cap" id="count"></span></div>
      <div class="scroll" id="scroll" tabindex="0" role="region" aria-label="Project list, scrollable"><table>
        <thead><tr>
          <th tabindex="0" data-s="code">Project</th><th tabindex="0" data-s="team">Team</th>
          <th tabindex="0" data-s="planned" class="num">Planned</th>
          <th tabindex="0" data-s="p" class="num">Forecast</th>
          <th tabindex="0" data-s="pbeh" class="num">Behaviour</th>
          <th>Status</th></tr></thead>
        <tbody id="rows"></tbody></table></div>
    </section>
    <section class="col" aria-label="Project detail and governance" aria-live="polite">
      <div class="colhead"><span class="cap">Project detail &amp; governance</span></div>
      <div class="detail" id="detail"></div>
    </section>
  </div>

  <div class="foot" id="note"></div>
</div>

<script>
(function(){
const DATA=__DATA__, M=DATA.model;
const S={cp:50,tol:0.60,mat:8,q:"",sort:"p",dir:-1,sel:null};
const $=s=>document.querySelector(s), pc=v=>Math.round(v*100);
const cls=p=>p>=S.tol?"crit":(p>=S.tol*0.8?"warn":"ok");
const lab=p=>p>=S.tol?"Exception":(p>=S.tol*0.8?"Approaching":"Within tol.");
const cv=c=>c==="crit"?"var(--crit)":c==="warn"?"var(--warn)":"var(--ok)";
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

function theme(){
  const b=document.createElement("button"); b.className="tbtn"; b.type="button";
  const cur=()=>document.documentElement.getAttribute("data-theme")
    ||(matchMedia("(prefers-color-scheme:dark)").matches?"dark":"light");
  const paint=()=>{b.textContent=cur()==="dark"?"Light":"Dark";
    b.setAttribute("aria-label","Switch to "+(cur()==="dark"?"light":"dark")+" theme");};
  b.onclick=()=>{document.documentElement.setAttribute("data-theme",cur()==="dark"?"light":"dark");paint();};
  paint(); $("#themeslot").appendChild(b);
}
function spec(){
  $("#spec").innerHTML=`<div><div class="k">Model</div><div class="v">GBT</div></div>
   <div><div class="k">PR-AUC</div><div class="v">${M.pr_auc}</div></div>
   <div><div class="k">Recall @0.41</div><div class="v">${pc(M.recall)}%</div></div>
   <div><div class="k">Projects</div><div class="v">${M.projects.toLocaleString()}</div></div>`;
}
function view(sort=true){
  let l=DATA.projects.map(p=>{const c=p.checkpoints[S.cp];return c?{...p,p:c.p,pbeh:c.pbeh,cp:c}:null}).filter(Boolean);
  if(S.mat)l=l.filter(x=>x.planned>=S.mat);
  if(S.q){const q=S.q.toLowerCase();l=l.filter(x=>x.code.toLowerCase().includes(q)||x.team.toLowerCase().includes(q));}
  if(sort){const k=S.sort;l.sort((a,b)=>{const x=a[k],y=b[k];
    return (typeof x==="string"?x.localeCompare(y):x-y)*S.dir;});}
  return l;
}
/* One place computes the operating point, so the exception report can never quote a
   different sensitivity from the panel. Measured on the held-out slice on screen. */
function stats(){
  const l=view(false), fl=l.filter(x=>x.p>=S.tol), pos=l.filter(x=>x.actual_breach);
  const tp=fl.filter(x=>x.actual_breach).length;
  return {n:l.length, ex:fl.length, prec:fl.length?tp/fl.length:0,
          rec:pos.length?tp/pos.length:0, missed:pos.length-tp,
          share:l.length?fl.length/l.length:0};
}
function readout(){
  const G=stats(), n=G.n, ex=G.ex, prec=G.prec, rec=G.rec, share=G.share, missed=G.missed;
  const load=share>0.45?"beyond most review capacity":share>0.3?"a heavy review load":"a workable review load";
  $("#readout").innerHTML=`
   <div class="cell"><div class="cap">In flight</div><div class="v">${n}</div>
     <div class="n">at ${S.cp}% of planned effort, above materiality</div></div>
   <div class="cell crit"><div class="cap">Exceptions to raise</div><div class="v">${ex}</div>
     <div class="n">${pc(share)}% of portfolio, ${load}</div></div>
   <div class="cell ok"><div class="cap">Flagged &amp; really overran</div><div class="v">${pc(prec)}%</div>
     <div class="n">catches ${pc(rec)}% of all overruns</div></div>
   <div class="cell crit"><div class="cap">Missed at this tolerance</div><div class="v">${missed}</div>
     <div class="n">overran but were never flagged</div></div>`;
}
function seg(){
  $("#seg").innerHTML=[25,50,75].map(c=>`<button type="button" data-cp="${c}" aria-pressed="${c===S.cp}">${c}%</button>`).join("");
  $("#seg").querySelectorAll("button").forEach(b=>b.onclick=()=>{S.cp=+b.dataset.cp;render();});
}
const scale=(v,c)=>`<div class="scale"><i style="width:${pc(v)}%;background:${c}"></i>
  <b style="left:${pc(S.tol)}%" title="tolerance"></b></div>`;
function rows(){
  const l=view(); $("#cptitle").textContent=S.cp+"%"; $("#count").textContent=l.length+" shown";
  if(!l.length){$("#rows").innerHTML=`<tr><td colspan="6" class="empty">No project matches &ldquo;${esc(S.q)}&rdquo;.</td></tr>`;return;}
  $("#rows").innerHTML=l.map(x=>{const c=cls(x.p);
    return `<tr tabindex="0" role="button" data-code="${x.code}" aria-selected="${x.code===S.sel}">
      <td class="code">${x.code}</td><td>${x.team}</td><td class="num num-mono">${x.planned} h</td>
      <td class="num"><span class="num-mono" style="color:${cv(c)};font-weight:600">${pc(x.p)}%</span>
        ${scale(x.p,cv(c))}</td>
      <td class="num"><span class="num-mono">${pc(x.pbeh)}%</span>${scale(x.pbeh,"var(--sig)")}</td>
      <td><span class="flag f-${c}">${lab(x.p)}</span></td></tr>`;}).join("");
  $("#rows").querySelectorAll("tr[data-code]").forEach(tr=>{
    const go=()=>{S.sel=tr.dataset.code;render();
      if(window.matchMedia("(max-width:760px)").matches){
        const d=document.querySelector("#detail");
        if(d)d.scrollIntoView({behavior:matchMedia("(prefers-reduced-motion:reduce)").matches?"auto":"smooth",block:"start"});}};
    tr.onclick=go; tr.onkeydown=e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();go();}};});
}
const drvs=(list,max)=>list.map(d=>`<div class="drv">
  <span class="ar ${d.dir}" aria-hidden="true">${d.dir==="up"?"▲":"▼"}</span>
  <span class="t">${esc(d.label)} <em>${esc(d.value)}</em>
    <span class="h">${d.hint?esc(d.hint)+", ":""}${d.dir==="up"?"raises":"lowers"} the forecast</span></span>
  <span class="b"><span style="width:${Math.max(6,Math.round(d.mag/max*100))}%;
    background:${d.dir==="up"?"var(--crit)":"var(--ok)"}"></span></span></div>`).join("");
function detail(){
  const l=view(); if(!l.length){$("#detail").innerHTML='<p class="empty">Select a project.</p>';return;}
  const p=l.find(x=>x.code===S.sel)||l[0]; S.sel=p.code;
  const c=p.cp,k=cls(c.p),raised=c.p>=S.tol, G=stats();
  const trk=[25,50,75].map(n=>{const q=p.checkpoints[n];
    return q?`<div class="c" aria-current="${n===S.cp}"><div class="cap">${n}% effort</div>
      <div class="v" style="color:${cv(cls(q.p))}">${pc(q.p)}%</div></div>`
     :`<div class="c"><div class="cap">${n}%</div><div class="v" style="color:var(--ink-3)">n/a</div></div>`;}).join("");
  const bmax=Math.max(...c.behaviour.map(d=>d.mag),1e-6), cmax=Math.max(...c.context.map(d=>d.mag),1e-6);
  /* The behaviour-only model is weaker, so isotonic shrinks it toward the base rate.
     Differencing the two scores therefore measures that shrinkage rather than genuine
     disagreement, and against held-out outcomes the resulting banner pointed the wrong
     way. Removed rather than shown misleadingly. */
  const rank=`Higher risk than <b>${pc(c.pctile)}%</b> of projects at the same checkpoint.`;
  const up=c.behaviour.filter(d=>d.dir==="up").slice(0,3);
  const cause=up.length?up.map(d=>`${d.label.toLowerCase()} (${d.value})`).join("; ")
    :"no single behavioural signal dominates; risk is carried by track record and size";
  const act=c.p>=0.65?"Escalate to the Project Board now; re-baseline or re-scope before more effort is booked."
    :c.p>=S.tol?"Raise an exception; agree corrective action with the Project Board before the next checkpoint."
    :"Continue within tolerance; re-assess at the next checkpoint.";
  const row=(k_,v_)=>`<div class="fr"><dt>${k_}</dt><dd>${v_}</dd></div>`;
  const form=raised
   ?`<div class="form raised"><header><span class="t">PRINCE2 Exception Report (draft)</span>
       <button class="btn" type="button" id="cp">Copy</button></header><dl id="rep">
       ${row("Project",`${p.code} &middot; ${p.team}`)}
       ${row("Raised at",`${S.cp}% of planned effort, with ${c.snap.hours} h booked of ${p.planned} h planned`)}
       ${row("Exception",`Forecast probability of breaching the planned-hours baseline is <b>${pc(c.p)}%</b>, against a tolerance of ${pc(S.tol)}%.`)}
       ${row("Cause",`Leading behavioural signals: ${esc(cause)}.`)}
       ${row("Impact",`${c.snap.n_decl} entries by ${c.snap.n_users} contributor(s) over ${c.snap.span} days; longest silence ${c.snap.maxgap} days; ${c.snap.hpad} h per active day. ${rank}`)}
       ${row("Options",`<ol><li>Continue unchanged and accept the forecast risk.</li>
         <li>Corrective action: rebalance contributors or close the silence gaps, then re-assess at the next checkpoint.</li>
         <li>Re-baseline the planned hours with the customer, or reduce scope to fit the baseline.</li></ol>`)}
       ${row("Recommendation",act)}
       ${row("Basis",`Gradient-boosted model, PR-AUC ${M.pr_auc}. At the tolerance and filters currently set, ${pc(G.prec)}% of flagged projects went on to overrun and ${pc(G.rec)}% of all overruns were caught (${G.missed} missed). Features use only data available at the checkpoint.`)}
     </dl></div>`
   :`<div class="form clear"><header><span class="t">Within tolerance: no exception</span></header>
      <dl>${row("Position",`Forecast ${pc(c.p)}% sits below the ${pc(S.tol)}% tolerance. ${rank}`)}
          ${row("Action",`Continue monitoring to the next checkpoint.`)}</dl></div>`;
  $("#detail").innerHTML=`
   <div class="dtop"><div class="id">${p.code}</div>
     <div class="meta">${p.team} &middot; ${p.planned} h planned &middot; team has overrun ${pc(p.team_prior)}% of past projects</div></div>
   <div class="pair">
     <div><div class="cap">Overall forecast</div><div class="v" style="color:${cv(k)}">${pc(c.p)}%</div>
       <div class="n">chance of breaching the baseline</div></div>
     <div><div class="cap">Behavioural signal</div><div class="v" style="color:var(--sig)">${pc(c.pbeh)}%</div>
       <div class="n">separate, weaker model; not on the same scale as the forecast</div></div></div>
   <div class="sec"><span class="cap">Risk trajectory</span></div><div class="trk">${trk}</div>
   <div class="sec"><span class="cap">What is happening now</span>
     <span class="cap" style="color:var(--sig)">${pc(c.beh_share)}% of this explanation</span></div>
   ${drvs(c.behaviour,bmax)}
   <div class="sec"><span class="cap">Context: track record &amp; size</span></div>${drvs(c.context,cmax)}
   <div class="sec"><span class="cap">Behavioural snapshot</span></div>
   <div class="snap">
     <div><div class="cap">Entries</div><div class="v">${c.snap.n_decl}</div></div>
     <div><div class="cap">Contributors</div><div class="v">${c.snap.n_users}</div></div>
     <div><div class="cap">Span</div><div class="v">${c.snap.span} d</div></div>
     <div><div class="cap">Intensity</div><div class="v">${c.snap.hpad} h/d</div></div>
     <div><div class="cap">Longest silence</div><div class="v">${c.snap.maxgap} d</div></div>
     <div><div class="cap">Idle share</div><div class="v">${pc(c.snap.idle)}%</div></div></div>
   ${form}
   <div class="reveal"><button class="btn" type="button" id="rv">Reveal actual outcome</button>
     <div class="out" id="rvout" hidden>Finished at a <b>${p.actual_ratio}&times;</b> effort ratio and
       <b style="color:${p.actual_breach?"var(--crit)":"var(--ok)"}">${p.actual_breach?"overran":"stayed within budget"}</b>.
       Historical validation only; unknown to the model at the time of the forecast.</div></div>`;
  const rv=$("#rv"); if(rv)rv.onclick=()=>{$("#rvout").hidden=false;rv.hidden=true;};
  const b=$("#cp"); if(b)b.onclick=()=>{const t="PRINCE2 EXCEPTION REPORT (draft)\n"+$("#rep").innerText;
    navigator.clipboard&&navigator.clipboard.writeText(t).then(()=>{b.textContent="Copied";
      setTimeout(()=>b.textContent="Copy",1600);});};
}
function note(){
  $("#note").innerHTML=`<b>Provenance.</b> Gradient-boosted trees trained on the Gryzzly time-declaration dataset
   (Levy, 2024): ${M.rows.toLocaleString()} valid checkpoint observations across ${M.projects.toLocaleString()} projects.
   Every feature is computed strictly from data available at the checkpoint, so no future information reaches a forecast.
   ${M.excluded.toLocaleString()} observations where the baseline had already been exceeded were excluded, because there the
   outcome is arithmetic rather than a forecast. Held-out temporal test, split by project: PR-AUC <b>${M.pr_auc}</b> against a
   ${M.floor} prevalence floor; behavioural signals alone reach <b>${M.behaviour_only}</b> and add <b>+${M.incremental}</b>
   over track record and size, carrying ${pc(M.beh_share)}% of the model's explanation. Accuracy improves as a project unfolds
   (${M.per_cp["0.25"]} &rarr; ${M.per_cp["0.5"]} &rarr; ${M.per_cp["0.75"]}). The tolerance defaults to 0.60 rather than the
   statistical max-F1 point (0.41), because maximising F1 flags about two-thirds of the portfolio, more than a PMO can
   review; setting it by <b>governance capacity</b> keeps the alert list workable, and the readout above reports the precision
   and recall that follow from wherever the tolerance is set. Probabilities are calibrated and reported within a 2% to 98% band;
   the tool never claims certainty. Research prototype, not a production system.`;
}
function render(){seg();readout();rows();detail();}
$("#tol").addEventListener("input",e=>{S.tol=+e.target.value;$("#tolv").textContent=S.tol.toFixed(2);render();});
$("#q").addEventListener("input",e=>{S.q=e.target.value.trim();render();});
$("#mat").addEventListener("change",e=>{S.mat=+e.target.value;S.sel=null;render();});
document.querySelectorAll("#ews thead th[data-s]").forEach(th=>{
  const go=()=>{const k=th.dataset.s;S.dir=(S.sort===k)?-S.dir:(k==="code"||k==="team"?1:-1);S.sort=k;render();};
  th.onclick=go; th.onkeydown=e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();go();}};});
theme(); spec(); note(); render();
})();
</script>
"""

# the json ships inside the page itself, so no pretty printing
body = BODY.replace("__DATA__", json.dumps(data, separators=(",", ":")))
open(f"{D}/_artifact_body.html","w").write(body)
open(f"{D}/inflight_earlywarning.html","w").write(
  '<!doctype html><html lang="en"><head><meta charset="utf-8">'
  '<meta name="viewport" content="width=device-width,initial-scale=1">'
  '<title>In-Flight Overrun Early-Warning System</title></head><body style="margin:0">'
  + body + '</body></html>')
print("built v3 (%.0f KB)" % (len(body)/1024))
