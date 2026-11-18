import pandas as pd
from util.logger import logger
from config import CUM_COL


def append_week_data(tracker_df: pd.DataFrame, full_week_label: str, kpi_row: dict):
    """
    全自动查重追加周数据
    full_week_label: 完整标签例如 "Shanghai - 11.8" (和Cumulative-breakdown label列一致)
    返回 (df_out, did_write)
    did_write=True：新增写入；did_write=False：已存在跳过
    """
    label_col_idx = CUM_COL["label"]
    # 检查label列是否存在
    if tracker_df.shape[1] <= label_col_idx:
        logger.warning("tracker dataframe label column missing, force append new row")
        new_row = pd.DataFrame([kpi_row])
        df_out = pd.concat([tracker_df, new_row], ignore_index=True)
        return df_out, True

    # 取出全部已存在标签
    exist_labels = tracker_df.iloc[:, label_col_idx].astype(str).str.strip().tolist()
    if full_week_label.strip() in exist_labels:
        logger.info(f"Week label [{full_week_label}] already exists, skip write‑back.")
        return tracker_df, False

    new_row = pd.DataFrame([kpi_row])
    df_out = pd.concat([tracker_df, new_row], ignore_index=True)
    logger.info(f"Success append new week [{full_week_label}] to Cumulative‑breakdown.")
    return df_out, True


def save_tracker_excel(df, file_path):
    """保存回Excel，openpyxl引擎"""
    try:
        with pd.ExcelWriter(file_path, engine="openpyxl", mode="w") as writer:
            df.to_excel(writer, sheet_name="Cumulative-breakdown", index=False)
        logger.info("Tracker excel saved complete.")
        return True
    except Exception as e:
        logger.error(f"Save tracker failed: {e}")
        return False
