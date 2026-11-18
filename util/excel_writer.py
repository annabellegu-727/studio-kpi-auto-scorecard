"""
Optional write-back to the tracker.

Both actions are OFF by default (config.WRITE_BACK_TRACKER /
config.MERGE_ENG_DETAILS). Reason: the tracker already contains this week's
Cumulative-breakdown row (it ends at 11.8), so appending again would create a
duplicate week. Turn them on only when you are feeding a brand-new week.

All key reads use .get() with fallbacks, so a missing metric can never raise
KeyError and kill the run.
"""
import pandas as pd
from openpyxl import load_workbook

from config import TRACKER_PATH, SHEET_OVERALL_KPI
from util.logger import logger


def _safe_num(value, default=0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def append_tracker_row(tracker_path, kpi_data, week_label, force=False):
    """Append one week to Cumulative-breakdown unless that week is already there."""
    try:
        wb = load_workbook(tracker_path)
        ws = wb.worksheets[1]  # Cumulative-breakdown

        existing = set()
        for row in ws.iter_rows(min_col=2, max_col=2, values_only=True):
            if row and isinstance(row[0], str):
                existing.add(row[0].strip())

        label = f"Shanghai - {week_label}"
        if label in existing and not force:
            logger.info("Week %s already in Cumulative-breakdown, skip append", week_label)
            return False

        ws.append([
            label,
            _safe_num(kpi_data.get("utilization")),
            int(_safe_num(kpi_data.get("ytd_engs"))),
            None, None,
            int(_safe_num(kpi_data.get("mkt_eng"))),
            _safe_num(kpi_data.get("mkt_pct")),
            _safe_num(kpi_data.get("global_journey")),
            _safe_num(kpi_data.get("global_journey_pct")),
            _safe_num(kpi_data.get("prog_rate")),
            int(_safe_num(kpi_data.get("prog_total"))),
            int(_safe_num(kpi_data.get("prog_completed"))),
            _safe_num(kpi_data.get("named_pct")),
            int(_safe_num(kpi_data.get("named_total"))),
            int(_safe_num(kpi_data.get("named_completed"))),
            _safe_num(kpi_data.get("horizon_prog_pct")),
            int(_safe_num(kpi_data.get("horizon_prog_total"))),
            int(_safe_num(kpi_data.get("horizon_prog_completed"))),
            int(_safe_num(kpi_data.get("opp_prog_num"))),
            _safe_num(kpi_data.get("opp_prog_m")),
            int(_safe_num(kpi_data.get("opp_create_num"))),
            _safe_num(kpi_data.get("opp_create_m")),
            int(_safe_num(kpi_data.get("opp_won_num"))),
            _safe_num(kpi_data.get("opp_won_m")),
        ])
        wb.save(tracker_path)
        logger.info("Append week %s to Cumulative-breakdown done", week_label)
        return True
    except Exception as exc:  # noqa: BLE001 - surface any IO issue, never crash the run
        logger.error("Append tracker row failed: %s", exc)
        return False


def get_existing_event_ids(tracker_path=TRACKER_PATH):
    try:
        df = pd.read_excel(tracker_path, sheet_name=2)
        if "EVENT ID" not in df.columns:
            return set()
        return set(df["EVENT ID"].dropna().astype(str))
    except Exception as exc:  # noqa: BLE001
        logger.warning("Read event ids failed: %s", exc)
        return set()


def merge_eng_details(tracker_path=TRACKER_PATH, scorecard_path=None,
                      sheet_name="4Q Completed Engs"):
    """Incrementally merge engagement detail rows into sheet index 2, de-duped by EVENT ID."""
    if scorecard_path is None:
        return 0
    try:
        df_new = pd.read_excel(scorecard_path, sheet_name=sheet_name)
        if "EVENT ID" not in df_new.columns:
            logger.warning("Sheet %s has no EVENT ID column, skip merge", sheet_name)
            return 0
        existing = get_existing_event_ids(tracker_path)
        df_add = df_new[~df_new["EVENT ID"].astype(str).isin(existing)]
        if df_add.empty:
            logger.info("No new eng details to add")
            return 0
        with pd.ExcelWriter(tracker_path, engine="openpyxl", mode="a",
                            if_sheet_exists="overlay") as writer:
            df_add.to_excel(writer, sheet_name=2, index=False, header=False,
                            startrow=writer.sheets[2].max_row)
        logger.info("Add %d new eng records", len(df_add))
        return len(df_add)
    except Exception as exc:  # noqa: BLE001
        logger.error("Merge eng details failed: %s", exc)
        return 0
