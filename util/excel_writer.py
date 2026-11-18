import pandas as pd
from openpyxl import load_workbook
from config import TRACKER_PATH
from util.logger import logger

def append_tracker_row(tracker_path, kpi_data, week_label):
    """追加一行到Tab2，增量写入Tab3明细"""
    try:
        wb = load_workbook(tracker_path)
        ws_tab2 = wb.worksheets[1]
        new_row = [
            week_label,
            kpi_data["utilization"],
            kpi_data["ytd_engs"],
            "", "",
            kpi_data["mkt_eng"],
            kpi_data["mkt_pct"],
            kpi_data["global_journey"],
            kpi_data["global_journey_pct"],
            kpi_data["prog_rate"],
            kpi_data["prog_total"],
            kpi_data["prog_completed"],
            kpi_data["named_pct"],
            kpi_data["named_total"],
            kpi_data["named_completed"],
            kpi_data["horizon_pct"],
            kpi_data["horizon_total"],
            kpi_data["horizon_completed"],
            kpi_data["opp_prog_num"],
            kpi_data["opp_prog_m"],
            kpi_data["opp_create_num"],
            kpi_data["opp_create_m"],
            kpi_data["opp_won_num"],
            kpi_data["opp_won_m"],
        ]
        ws_tab2.append(new_row)
        wb.save(tracker_path)
        logger.info(f"Append week {week_label} to Tab2 done")
        return True
    except Exception as e:
        logger.error(f"Write Tab2 failed: {str(e)}")
        raise

def get_existing_event_ids(tracker_path):
    df_tab3 = pd.read_excel(tracker_path, sheet_name=2)
    return set(df_tab3["EVENT ID"].dropna().astype(str))

def merge_eng_details(tracker_path, scorecard_path):
    df_new = pd.read_excel(scorecard_path, sheet_name="4Q Completed Engs")
    exist_ids = get_existing_event_ids(tracker_path)
    df_add = df_new[~df_new["EVENT ID"].astype(str).isin(exist_ids)]
    if len(df_add) > 0:
        with pd.ExcelWriter(tracker_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
            df_add.to_excel(writer, sheet_name=2, index=False, header=False, startrow=writer.sheets[2].max_row)
        logger.info(f"Add {len(df_add)} new eng records")
    else:
        logger.info("No new eng details to add")
    return len(df_add)
