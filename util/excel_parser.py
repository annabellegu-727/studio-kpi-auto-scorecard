"""
Parse the weekly scorecard.

Two sources are used, because they answer different questions:

1) "Overall KPI Summary " -> the current-week snapshot for Shanghai.
   This sheet is the live one (Data as of 8th Nov 2026) and holds everything
   the 7 KPI cards need except utilization: marketing originated %, YTD
   progression %, pipeline $M (progressed / created / won).

2) "Horizon Accts Penetration " -> horizon account penetration (China row,
   within 100 miles). Updated once every 2 weeks.

Utilization is not in either sheet: it comes from the tracker
(Cumulative-breakdown, latest Shanghai row), see read_latest_studio_row().

All column indices live in config.py. Nothing here guesses a column position.
"""
import math
import pandas as pd

from config import (
    SCORECARD_PATH, TRACKER_PATH, SHEET_OVERALL_KPI, SHEET_HORIZON_PEN,
    SHEET_CUMULATIVE, STUDIO_NAME, HORIZON_REGION, KPI_COL, HORIZON_COL,
    CUM_COL, CUM_DATA_START_ROW, BASE_FACTOR, HORIZON_TOTAL_ACCOUNTS,
)
from util.logger import logger

# Strings that appear in these workbooks where a number is expected
EMPTY_TOKENS = {"", "/", "-", "--", "nan", "NaN", "None", "none", "n/a", "N/A"}


def to_num(value):
    """Cell -> float. Returns None for blanks, slashes and other non-numbers."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)
    text = str(value).strip()
    if text in EMPTY_TOKENS:
        return None
    text = text.replace(",", "").replace("$", "").replace("%", "")
    try:
        return float(text)
    except ValueError:
        return None


def to_int(value):
    num = to_num(value)
    return int(round(num)) if num is not None else 0


def safe_div(numerator, denominator):
    """Zero-division and type safe."""
    try:
        num = float(numerator)
        den = float(denominator)
    except (TypeError, ValueError):
        return 0.0
    if den == 0:
        return 0.0
    return num / den


def _label_of(row, columns=(1, 2, 0)):
    """First non-empty text label in the given columns."""
    for col in columns:
        if col >= len(row):
            continue
        cell = row[col]
        if isinstance(cell, str):
            text = cell.strip()
            if text:
                return text
    return ""


def find_label_row(df, wanted):
    """Locate a row whose label cell equals `wanted` (case/space tolerant)."""
    target = wanted.strip().lower()
    for idx in range(len(df)):
        label = _label_of(df.iloc[idx]).lower()
        if label == target:
            return idx
    return None


def read_latest_studio_row(tracker_path=TRACKER_PATH):
    """Latest Cumulative-breakdown row for STUDIO_NAME -> dict of raw values."""
    df = pd.read_excel(tracker_path, sheet_name=SHEET_CUMULATIVE, header=None)
    rows = []
    for idx in range(CUM_DATA_START_ROW, len(df)):
        label = _label_of(df.iloc[idx], columns=(CUM_COL["label"],))
        if label.lower().startswith(STUDIO_NAME.lower()):
            rows.append((idx, label))
    if not rows:
        raise ValueError(f"no {STUDIO_NAME} row found in {SHEET_CUMULATIVE}")
    idx, label = rows[-1]
    row = df.iloc[idx]
    values = {key: row[col] if col < len(row) else None for key, col in CUM_COL.items()}
    week = label.split("-")[-1].strip() if "-" in label else label
    values["_row"] = idx
    values["_label"] = label
    values["_week"] = week
    return values


def parse_horizon(scorecard_path=SCORECARD_PATH):
    """Horizon penetration, China row, within 100 miles."""
    df = pd.read_excel(scorecard_path, sheet_name=SHEET_HORIZON_PEN, header=None)
    idx = find_label_row(df, HORIZON_REGION)
    if idx is None:
        logger.warning("Horizon region %s not found, horizon card falls back to 0", HORIZON_REGION)
        return {"total": 0, "engaged": 0, "pct": 0.0}
    row = df.iloc[idx]
    total = to_int(row[HORIZON_COL["total_100mi"]])
    engaged = to_int(row[HORIZON_COL["engaged_100mi"]])
    pct = to_num(row[HORIZON_COL["pct_100mi"]])
    if pct is None:
        pct = safe_div(engaged, total)
    return {"total": total, "engaged": engaged, "pct": pct}


def parse_scorecard(file_path=SCORECARD_PATH, tracker_path=TRACKER_PATH):
    """Return the full KPI dict consumed by the writer and the dashboard."""
    df = pd.read_excel(file_path, sheet_name=SHEET_OVERALL_KPI, header=None)

    idx = find_label_row(df, STUDIO_NAME)
    if idx is None:
        raise ValueError(f"row '{STUDIO_NAME}' not found in sheet '{SHEET_OVERALL_KPI}'")
    row = df.iloc[idx]

    def cell(key, as_int=False):
        col = KPI_COL[key]
        value = row[col] if col < len(row) else None
        return to_int(value) if as_int else to_num(value)

    eng_ytd = cell("eng_ytd", as_int=True)
    mkt_eng = cell("mkt_eng", as_int=True)
    mkt_pct = cell("mkt_pct")
    if mkt_pct is None:
        mkt_pct = safe_div(mkt_eng, eng_ytd)

    gj_num = cell("gj_num", as_int=True)
    gj_pct = cell("gj_pct")
    if gj_pct is None:
        gj_pct = safe_div(gj_num, eng_ytd)

    prog_ytd_pct = cell("prog_ytd_pct")
    prog_ytd_eng = cell("prog_ytd_eng", as_int=True)
    prog_ytd_done = cell("prog_ytd_done", as_int=True)
    if prog_ytd_pct is None:
        prog_ytd_pct = safe_div(prog_ytd_done, prog_ytd_eng)

    named_pct = cell("named_pct")
    named_eng = cell("named_eng", as_int=True)
    named_done = cell("named_done", as_int=True)
    if named_pct is None:
        named_pct = safe_div(named_done, named_eng)

    horizon_prog_pct = cell("horizon_pct")
    horizon_eng = cell("horizon_eng", as_int=True)
    horizon_done = cell("horizon_done", as_int=True)
    if horizon_prog_pct is None:
        horizon_prog_pct = safe_div(horizon_done, horizon_eng)

    # utilization + week label always come from the tracker (single source of truth)
    latest = read_latest_studio_row(tracker_path)
    utilization = to_num(latest.get("util")) or 0.0
    if eng_ytd == 0:
        eng_ytd = to_int(latest.get("eng"))

    horizon = parse_horizon(file_path)

    # dynamic $M targets = base factor * YTD engagements
    target_prg = round(BASE_FACTOR["progressed"] * eng_ytd, 2)
    target_cre = round(BASE_FACTOR["created"] * eng_ytd, 2)
    target_won = round(BASE_FACTOR["won"] * eng_ytd, 2)

    kpi_data = {
        # card metrics
        "utilization": utilization,
        "ytd_engs": eng_ytd,
        "mkt_eng": mkt_eng,
        "mkt_pct": mkt_pct or 0.0,
        "global_journey": gj_num,
        "global_journey_pct": gj_pct or 0.0,
        "prog_rate": prog_ytd_pct or 0.0,
        "prog_total": prog_ytd_eng,
        "prog_completed": prog_ytd_done,
        "named_pct": named_pct or 0.0,
        "named_total": named_eng,
        "named_completed": named_done,
        "horizon_prog_pct": horizon_prog_pct or 0.0,
        "horizon_prog_total": horizon_eng,
        "horizon_prog_completed": horizon_done,
        # horizon account penetration (card 4)
        "horizon_total": horizon["total"],
        "horizon_completed": horizon["engaged"],
        "horizon_pct": horizon["pct"],
        # pipeline
        "opp_prog_num": cell("opp_prog_num", as_int=True),
        "opp_prog_m": cell("opp_prog_m") or 0.0,
        "opp_create_num": cell("opp_create_num", as_int=True),
        "opp_create_m": cell("opp_create_m") or 0.0,
        "opp_won_num": cell("opp_won_num", as_int=True),
        "opp_won_m": cell("opp_won_m") or 0.0,
        # dynamic targets
        "target_prg_m": target_prg,
        "target_cre_m": target_cre,
        "target_won_m": target_won,
        # meta
        "week_label": latest["_week"],
        "as_of": _as_of_text(df),
    }

    logger.info(
        "Parsed %s wk%s | util=%.2f%% eng=%d mkt=%.2f%% prog=%.2f%% "
        "prg=$%.2fM cre=$%.2fM won=$%.2fM horizon=%d/%d",
        STUDIO_NAME, kpi_data["week_label"], kpi_data["utilization"] * 100,
        kpi_data["ytd_engs"], kpi_data["mkt_pct"] * 100, kpi_data["prog_rate"] * 100,
        kpi_data["opp_prog_m"], kpi_data["opp_create_m"], kpi_data["opp_won_m"],
        kpi_data["horizon_completed"], kpi_data["horizon_total"],
    )
    return kpi_data


def _as_of_text(df):
    """'Data as of \n8th Nov 2026' -> '8 Nov 2026'."""
    for idx in range(min(6, len(df))):
        for value in df.iloc[idx].tolist():
            if isinstance(value, str) and "Data as of" in value:
                text = " ".join(value.replace("Data as of", "").split())
                return text.strip()
    return ""


if __name__ == "__main__":
    parse_scorecard()
