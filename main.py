"""
Studio KPI automation entry.

Flow:
1. parse the scorecard (Overall KPI Summary + Horizon penetration)
2. optionally write back to the tracker (off by default, see config)
3. render dashboard.html from the tracker history + current snapshot
"""
from util.excel_parser import parse_scorecard
from util.excel_writer import append_tracker_row, merge_eng_details
from util.render_html import render_dashboard
from util.logger import logger
from config import (
    SCORECARD_PATH, TRACKER_PATH, WRITE_BACK_TRACKER, MERGE_ENG_DETAILS,
)


def run(week_label=None):
    logger.info("==== Start KPI automation run ====")

    kpi = parse_scorecard(SCORECARD_PATH, TRACKER_PATH)

    if WRITE_BACK_TRACKER:
        append_tracker_row(TRACKER_PATH, kpi, kpi.get("week_label") or week_label)
    else:
        logger.info("Write-back disabled (week already present in tracker)")

    if MERGE_ENG_DETAILS:
        merge_eng_details(TRACKER_PATH, SCORECARD_PATH)

    html_path = render_dashboard(kpi, week_label)
    logger.info("==== All task finished: %s ====", html_path)
    return html_path


if __name__ == "__main__":
    run()
