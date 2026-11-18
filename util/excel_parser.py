import pandas as pd
from config import *
from util.logger import logger

def parse_scorecard(file_path):
    """解析每周Scorecard，提取所有指标"""
    try:
        # Utilization: Beijing + Shanghai YTD Completed
        df_util = pd.read_excel(file_path, sheet_name=SHEET_UTILIZATION, header=None)
        utilization_val = df_util.iloc[6, 20]  # row7, U col
        utilization_val = round(float(utilization_val), UTILIZATION_PRECISION)

        # Overall KPI Summary, Shanghai row (row7)
        df_overall = pd.read_excel(file_path, sheet_name=SHEET_OVERALL_KPI, header=None)
        row_sh = 6
        ytd_engs = int(df_overall.iloc[row_sh, 2])
        mkt_eng = int(df_overall.iloc[row_sh, 5])
        mkt_pct = float(df_overall.iloc[row_sh, 6])
        global_journey = int(df_overall.iloc[row_sh, 7])
        global_journey_pct = float(df_overall.iloc[row_sh, 8])

        prog_rate = float(df_overall.iloc[row_sh, 40])
        prog_total = int(df_overall.iloc[row_sh, 41])
        prog_completed = int(df_overall.iloc[row_sh, 42])

        named_pct = float(df_overall.iloc[row_sh, 43])
        named_total = int(df_overall.iloc[row_sh, 44])
        named_completed = int(df_overall.iloc[row_sh, 45])

        horizon_pct = float(df_overall.iloc[row_sh, 46])
        horizon_total = int(df_overall.iloc[row_sh, 47])
        horizon_completed = int(df_overall.iloc[row_sh, 48])

        opp_prog_num = int(df_overall.iloc[row_sh, 55])
        opp_prog_m = float(df_overall.iloc[row_sh, 56])
        opp_create_num = int(df_overall.iloc[row_sh, 57])
        opp_create_m = float(df_overall.iloc[row_sh, 58])
        opp_won_num = int(df_overall.iloc[row_sh, 59])
        opp_won_m = float(df_overall.iloc[row_sh, 60])

        # Horizon within 100 miles
        df_horizon = pd.read_excel(file_path, sheet_name=SHEET_HORIZON_PEN, header=None)
        horizon_total_100mile = int(df_horizon.iloc[7, 7])
        horizon_covered_100mile = int(df_horizon.iloc[7, 8])
        horizon_penetration_100mile = float(df_horizon.iloc[7, 9])

        # Dynamic pipeline target
        target_prog_m = round(ytd_engs * BASE_FACTOR["progressed"], 2)
        target_create_m = round(ytd_engs * BASE_FACTOR["created"], 2)
        target_won_m = round(ytd_engs * BASE_FACTOR["won"], 2)

        result = {
            "utilization": utilization_val,
            "ytd_engs": ytd_engs,
            "mkt_eng": mkt_eng,
            "mkt_pct": mkt_pct,
            "global_journey": global_journey,
            "global_journey_pct": global_journey_pct,
            "prog_rate": prog_rate,
            "prog_total": prog_total,
            "prog_completed": prog_completed,
            "named_pct": named_pct,
            "named_total": named_total,
            "named_completed": named_completed,
            "horizon_pct": horizon_pct,
            "horizon_total": horizon_total,
            "horizon_completed": horizon_completed,
            "horizon_100_total": horizon_total_100mile,
            "horizon_100_covered": horizon_covered_100mile,
            "horizon_100_pct": horizon_penetration_100mile,
            "opp_prog_num": opp_prog_num,
            "opp_prog_m": opp_prog_m,
            "opp_create_num": opp_create_num,
            "opp_create_m": opp_create_m,
            "opp_won_num": opp_won_num,
            "opp_won_m": opp_won_m,
            "target_prog_m": target_prog_m,
            "target_create_m": target_create_m,
            "target_won_m": target_won_m,
            "horizon_target": KPI_TARGETS["horizon_account"],
        }
        logger.info("Scorecard parse success")
        return result
    except Exception as e:
        logger.error(f"Parse failed: {str(e)}")
        raise
