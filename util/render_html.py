"""
Render dashboard.html.

History series come from ONE place only: the "Cumulative-breakdown" sheet of
Studio Internal_Goal Tracking.xlsx, filtered to the Shanghai rows.

Column mapping (see CUM_COL in config.py):
    col1  "Shanghai - 11.8"                     week label
    col2  Utilization                           0..1
    col3  2026 YTD Engs                         count
    col6  Marketing Originated                  count
    col7  % of Marketing Org Engs               ratio, only filled from wk 9 onward
    col29 YTD Progression rate (All Client)     ratio, only sparsely filled
    col43 $M Opps Progressed
    col45 $M Opps Created
    col47 $M Opps Won

Fallbacks (all logged, none invented):
    mkt_pct  -> col7, else col6 / col3   (identical values wherever both exist)
    prog     -> col29, else carry forward the last published YTD value
                (a YTD ratio stays valid until a new one is published)
"""
import pandas as pd
from jinja2 import Environment, FileSystemLoader

from config import (
    TRACKER_PATH, HTML_OUT_PATH, TEMPLATE_NAME, SHEET_CUMULATIVE, CUM_COL,
    CUM_DATA_START_ROW, STUDIO_NAME, KPI_TARGETS, BASE_FACTOR,
    UTILIZATION_PRECISION, HORIZON_TOTAL_ACCOUNTS,
)
from util.logger import logger

TEMPLATE_DIR = "template"


def _history_frame(tracker_path=TRACKER_PATH):
    df = pd.read_excel(tracker_path, sheet_name=SHEET_CUMULATIVE, header=None)
    keep = []
    for idx in range(CUM_DATA_START_ROW, len(df)):
        label = df.iloc[idx, CUM_COL["label"]]
        if isinstance(label, str) and label.strip().lower().startswith(STUDIO_NAME.lower()):
            keep.append(idx)
    if not keep:
        raise ValueError(f"no {STUDIO_NAME} rows in {SHEET_CUMULATIVE}")
    return df.iloc[keep]


def _num(value):
    from util.excel_parser import to_num
    return to_num(value)


def build_history(tracker_path=TRACKER_PATH):
    df = _history_frame(tracker_path)

    weeks, eng, util, mkt, prog, prg, cre, won = [], [], [], [], [], [], [], []
    carried_prog = None
    filled_mkt = 0
    filled_prog = 0

    for _, row in df.iterrows():
        label = str(row[CUM_COL["label"]]).strip()
        week = label.split("-")[-1].strip() if "-" in label else label
        weeks.append(week)

        eng_v = _num(row[CUM_COL["eng"]])
        eng.append(int(round(eng_v)) if eng_v is not None else None)
        util.append(_num(row[CUM_COL["util"]]))

        # ---- marketing originated % ----
        m = _num(row[CUM_COL["mkt_pct"]])
        if m is None:
            mkt_eng = _num(row[CUM_COL["mkt_eng"]])
            if mkt_eng is not None and eng_v:
                m = mkt_eng / eng_v
                filled_mkt += 1
        mkt.append(m)

        # ---- progression rate (YTD, all client) ----
        p = _num(row[CUM_COL["prog_ytd"]])
        if p is None and carried_prog is not None:
            p = carried_prog
            filled_prog += 1
        if p is not None:
            carried_prog = p
        prog.append(p)

        prg.append(_num(row[CUM_COL["prg_m"]]))
        cre.append(_num(row[CUM_COL["cre_m"]]))
        won.append(_num(row[CUM_COL["won_m"]]))

    logger.info(
        "History: %d weeks (%s .. %s) | mkt derived from counts on %d rows | prog carried forward on %d rows",
        len(weeks), weeks[0], weeks[-1], filled_mkt, filled_prog,
    )
    return {
        "W": weeks, "ENG": eng, "UTIL": util, "MKT": mkt, "PROG": prog,
        "PRG": prg, "CRE": cre, "WON": won,
    }


def _target_series(eng_series, factor):
    """Dynamic target = base factor * YTD engagements, per week."""
    return [round(factor * e, 2) if e else None for e in eng_series]


def _flag(ratio, target):
    return ("ok", "达标") if ratio >= target else ("off", "未达标")


def build_kpi_cards(kpi_data):
    util = kpi_data["utilization"] or 0.0
    mkt = kpi_data["mkt_pct"] or 0.0
    prog = kpi_data["prog_rate"] or 0.0
    hz_total = kpi_data["horizon_total"] or 0
    hz_done = kpi_data["horizon_completed"] or 0
    hz_pct = kpi_data["horizon_pct"] or 0.0

    prg = kpi_data["opp_prog_m"] or 0.0
    cre = kpi_data["opp_create_m"] or 0.0
    won = kpi_data["opp_won_m"] or 0.0
    t_prg = kpi_data["target_prg_m"]
    t_cre = kpi_data["target_cre_m"]
    t_won = kpi_data["target_won_m"]

    util_state, util_label = _flag(util, KPI_TARGETS["utilization"])
    mkt_state, mkt_label = _flag(mkt, KPI_TARGETS["marketing_origin_pct"])
    if mkt_state == "off":
        gap = KPI_TARGETS["marketing_origin_pct"] * 100 - mkt * 100
        mkt_label = f"差 {gap:.1f}pp"

    prog_state, prog_label = _flag(prog, KPI_TARGETS["progression_rate"])
    hz_state, hz_label = _flag(hz_pct, KPI_TARGETS["horizon_penetration"])
    if hz_state == "off":
        gap_acc = HORIZON_TOTAL_ACCOUNTS * KPI_TARGETS["horizon_penetration"] - hz_done
        hz_label = f"差 {gap_acc:.1f} 个账户"

    prg_state, prg_label = _flag(prg / t_prg if t_prg else 0, 1.0)
    cre_state, cre_label = _flag(cre / t_cre if t_cre else 0, 1.0)
    won_state, won_label = _flag(won / t_won if t_won else 0, 1.0)

    return [
        {
            "k": "Utilization",
            "v": f"{util * 100:.{UTILIZATION_PRECISION}f}%",
            "t": f"目标 {KPI_TARGETS['utilization'] * 100:.0f}%",
            "pct": round(util * 100, 1),
            "tg": KPI_TARGETS["utilization"] * 100,
            "s": util_state, "label": util_label,
        },
        {
            "k": "% Mkt Org Engs",
            "v": f"{mkt * 100:.1f}%",
            "t": f"目标 {KPI_TARGETS['marketing_origin_pct'] * 100:.0f}%",
            "pct": round(mkt * 100, 1),
            "tg": KPI_TARGETS["marketing_origin_pct"] * 100,
            "s": mkt_state, "label": mkt_label,
        },
        {
            "k": "Progression Rate",
            "v": f"{prog * 100:.1f}%",
            "t": f"目标 {KPI_TARGETS['progression_rate'] * 100:.0f}%",
            "pct": round(prog * 100, 1),
            "tg": KPI_TARGETS["progression_rate"] * 100,
            "s": prog_state, "label": prog_label,
        },
        {
            "k": "Horizon Account",
            "v": f"{hz_done}/{hz_total}",
            "t": f"目标 {KPI_TARGETS['horizon_penetration'] * 100:.0f}% (约 {HORIZON_TOTAL_ACCOUNTS * KPI_TARGETS['horizon_penetration']:.1f} 个)",
            "pct": round(hz_pct * 100, 1),
            "tg": KPI_TARGETS["horizon_penetration"] * 100,
            "s": hz_state, "label": hz_label,
        },
        {
            "k": "$M Opps Progressed",
            "v": f"{prg:.2f}",
            "t": f"目标 {t_prg:.1f}M",
            "pct": round(prg / t_prg * 100, 1) if t_prg else 0,
            "tg": 100, "s": prg_state, "label": prg_label,
        },
        {
            "k": "$M Opps Create",
            "v": f"{cre:.2f}",
            "t": f"目标 {t_cre:.1f}M",
            "pct": round(cre / t_cre * 100, 1) if t_cre else 0,
            "tg": 100, "s": cre_state, "label": cre_label,
        },
        {
            "k": "$M Opps Won",
            "v": f"{won:.2f}",
            "t": f"目标 {t_won:.1f}M",
            "pct": round(won / t_won * 100, 1) if t_won else 0,
            "tg": 100, "s": won_state, "label": won_label,
        },
    ]


def render_dashboard(kpi_data, week_label=None, output_path=HTML_OUT_PATH,
                     tracker_path=TRACKER_PATH):
    history = build_history(tracker_path)

    # The scorecard snapshot is authoritative for the current week; align the
    # last point of the history lines with it so card and chart never disagree.
    if history["MKT"] and kpi_data.get("mkt_pct"):
        history["MKT"][-1] = kpi_data["mkt_pct"]
    if history["PROG"] and kpi_data.get("prog_rate"):
        history["PROG"][-1] = kpi_data["prog_rate"]

    targets = {
        "TPRG": _target_series(history["ENG"], BASE_FACTOR["progressed"]),
        "TCRE": _target_series(history["ENG"], BASE_FACTOR["created"]),
        "TWON": _target_series(history["ENG"], BASE_FACTOR["won"]),
    }

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)
    template = env.get_template(TEMPLATE_NAME)

    cards = build_kpi_cards(kpi_data)
    label = week_label or kpi_data.get("week_label") or ""

    html = template.render(
        week_label=label,
        as_of=kpi_data.get("as_of", ""),
        studio=STUDIO_NAME,
        KPI=cards,
        W=history["W"], ENG=history["ENG"], UTIL=history["UTIL"],
        MKT=history["MKT"], PROG=history["PROG"],
        PRG=history["PRG"], CRE=history["CRE"], WON=history["WON"],
        TPROG=targets["TPRG"], TCRE=targets["TCRE"], TWON=targets["TWON"],
        weeks=len(history["W"]),
    )

    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(html)
    logger.info("Dashboard written: %s (weeks=%d)", output_path, len(history["W"]))
    return output_path
