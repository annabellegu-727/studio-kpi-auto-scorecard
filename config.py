"""
KPI 自动化配置
更新规则：
1. 移除KPI红蓝标线
2. Horizon Account：总账户12个，达标率35% → 目标 = 12 * 0.35 = 4.2
3. 看板标题去掉口径文字
4. Utilization 保留2位小数，百分比展示，自动从scorecard读取，非人工输入
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File Path
SCORECARD_PATH = os.path.join(BASE_DIR, "Weekly Performance Scorecard.xlsx")
TRACKER_PATH = os.path.join(BASE_DIR, "Studio Internal_Goal Tracking.xlsx")
HTML_OUT_PATH = os.path.join(BASE_DIR, "dashboard.html")
TEMPLATE_PATH = os.path.join(BASE_DIR, "template", "dashboard.html")

# Sheet Names (注意末尾空格，和原始文件对齐)
SHEET_UTILIZATION = "Engagements Utilization"
SHEET_OVERALL_KPI = "Overall KPI Summary "
SHEET_HORIZON_PEN = "Horizon Accts Penetration "
SHEET_COMPLETED_ENG = "4Q Completed Engs"
SHEET_PIPELINE_BASE = "Pipeline Impact"

# KPI Targets
KPI_TARGETS = {
    "utilization": 0.75,
    "marketing_origin_pct": 0.30,
    "progression_rate": 0.40,
    "horizon_account": 12 * 0.35,  # 12 accounts, 35% penetration
    "opps_progressed_m": None,
    "opps_created_m": None,
    "opps_won_m": None,
}

# Pipeline base factor (2025 YE Beijing / 471, +6% uplift)
BASE_FACTOR = {
    "progressed": 0.1408 * 1.06,
    "created": 0.0641 * 1.06,
    "won": 0.1391 * 1.06,
}

# Utilization decimal precision
UTILIZATION_PRECISION = 2
