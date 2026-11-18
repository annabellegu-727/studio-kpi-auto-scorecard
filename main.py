"""
Studio KPI automation entry.

Flow:
1. parse the scorecard (Overall KPI Summary + Horizon penetration)
2. Auto‑check duplicate week label; append only when new week
3. render dashboard.html from the tracker history + current snapshot
"""
import pandas as pd
from util.excel_parser import parse_scorecard
from util.excel_writer import append_week_data, save_tracker_excel
from util.render_html import render_dashboard
from util.logger import logger
from config import (
    SCORECARD_PATH, TRACKER_PATH, STUDIO_NAME, WEEK_LABEL, HTML_OUT_PATH, SHEET_CUMULATIVE
)


def run(week_label=None):
    logger.info("==== Start KPI automation run ====")

    # 使用config里的周标签
    current_week = week_label if week_label is not None else WEEK_LABEL
    kpi = parse_scorecard(SCORECARD_PATH, TRACKER_PATH)

    # 读取追踪表，用于自动查重
    tracker_df = pd.read_excel(TRACKER_PATH, sheet_name=SHEET_CUMULATIVE)
    full_tracker_label = f"{STUDIO_NAME} - {current_week}"

    # 自动查重：存在就跳过，不存在才追加
    tracker_df, did_write = append_week_data(tracker_df, full_tracker_label, kpi)
    if did_write:
        save_tracker_excel(tracker_df, TRACKER_PATH)
    else:
        logger.info("Week existed, skip saving excel file.")

    # 无论写不写Excel，都重新渲染dashboard
    html_path = render_dashboard(kpi, current_week, HTML_OUT_PATH)
    logger.info("==== All task finished: %s ====", html_path)
    return html_path


if __name__ == "__main__":
    run()
