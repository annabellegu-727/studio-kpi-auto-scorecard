"""
Studio KPI Automation Entry
"""
from util.excel_parser import parse_scorecard
from util.excel_writer import append_tracker_row, merge_eng_details
from util.render_html import render_dashboard
from config import SCORECARD_PATH, TRACKER_PATH
from util.logger import logger

if __name__ == "__main__":
    # ========== 在这里修改当周标签，例如 "11.8"
    WEEK_LABEL = "11.8"
    # ==========

    logger.info("==== Start KPI automation run ====")
    kpi_result = parse_scorecard(SCORECARD_PATH)
    append_tracker_row(TRACKER_PATH, kpi_result, WEEK_LABEL)
    merge_eng_details(TRACKER_PATH, SCORECARD_PATH)
    render_dashboard(kpi_result, WEEK_LABEL)
    logger.info("==== All task finished ====")
