"""
KPI automation config.
All column indices below are 0-based and verified against the real files
(Weekly Performance Scorecard.xlsx / Studio Internal_Goal Tracking.xlsx).
Do NOT hardcode other column numbers elsewhere.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------
# Files
# ----------------------------------------------------------------------------
SCORECARD_PATH = os.path.join(BASE_DIR, "Weekly Performance Scorecard.xlsx")
TRACKER_PATH = os.path.join(BASE_DIR, "Studio Internal_Goal Tracking.xlsx")
HTML_OUT_PATH = os.path.join(BASE_DIR, "dashboard.html")
TEMPLATE_NAME = "dashboard.html"

# ----------------------------------------------------------------------------
# Sheets (trailing spaces matter)
# ----------------------------------------------------------------------------
SHEET_OVERALL_KPI = "Overall KPI Summary "       # live week snapshot (Data as of 8th Nov 2026)
SHEET_HORIZON_PEN = "Horizon Accts Penetration " # horizon penetration, updated every 2 weeks
SHEET_CUMULATIVE = "Cumulative-breakdown"        # weekly history, one row per studio per week

# Studio label used in both files
STUDIO_NAME = "Shanghai"
# Horizon penetration is reported by country, Shanghai studio belongs to China
HORIZON_REGION = "China"

# ----------------------------------------------------------------------------
# Overall KPI Summary - column indices (0-based), row = Shanghai
# Verified: 2026 engs=92, marketing originated=27 (29.35%)
# ----------------------------------------------------------------------------
KPI_COL = {
    "eng_ytd": 2,             # 2026 Completed Engagements (Wk 1-45)
    "mkt_eng": 5,             # Completed Engagements - Marketing Originated
    "mkt_pct": 6,             # % of Total (marketing originated / total engs)
    "gj_num": 7,              # of Global Journeys
    "gj_pct": 8,              # % of Total (global journeys)
    "prog4q_pct": 41,         # Rolling 4 Quarter Progression Rate (All Client Engs)
    "prog4q_eng": 42,
    "prog4q_done": 43,
    "prog_ytd_pct": 44,       # YTD Progression rate (All Client Engs)  <- card metric
    "prog_ytd_eng": 45,
    "prog_ytd_done": 46,
    "named_pct": 47,          # YTD Progression rate (Named Account Client Engs)
    "named_eng": 48,
    "named_done": 49,
    "horizon_pct": 50,        # YTD Progression rate (Horizon Account Client Engs)
    "horizon_eng": 51,
    "horizon_done": 52,
    "opp_prog_num": 57,       # # Opps Progressed
    "opp_prog_m": 58,         # $M Opps Progressed
    "opp_create_num": 59,     # # Opps Created
    "opp_create_m": 60,       # $M Opps Created
    "opp_won_num": 61,        # # Opps Won
    "opp_won_m": 62,          # $M Opps Won
}

# Horizon Accts Penetration - column indices (0-based), row = China
HORIZON_COL = {
    "total_100mi": 7,         # Total # Horizon Accounts within 100 miles
    "engaged_100mi": 8,       # # Horizon Accounts Engaged within 100 miles
    "pct_100mi": 9,           # % Horizon Engaged within 100 miles
}

# ----------------------------------------------------------------------------
# Cumulative-breakdown - column indices (0-based)
# Header block occupies rows 0..3, real data starts at row 4
# ----------------------------------------------------------------------------
CUM_COL = {
    "label": 1,        # "Shanghai - 11.8"
    "util": 2,         # Utilization
    "eng": 3,          # 2026 YTD Engs
    "mkt_eng": 6,      # Marketing Originated (count)
    "mkt_pct": 7,      # % of Marketing Org Engs (mostly "/" before wk 9)
    "prog_ytd": 29,    # YTD Progression rate (All Client Engs) - sparsely filled
    "prog_named": 32,  # YTD Progression rate (Named Account Client Engs) - complete
    "prg_m": 43,       # $M Opps Progressed
    "cre_m": 45,       # $M Opps Created
    "won_m": 47,       # $M Opps Won
}
CUM_DATA_START_ROW = 4

# ----------------------------------------------------------------------------
# Targets
# ----------------------------------------------------------------------------
KPI_TARGETS = {
    "utilization": 0.75,
    "marketing_origin_pct": 0.30,
    "progression_rate": 0.40,
    "horizon_penetration": 0.35,
}
# Horizon account base (used only for the card note "目标 35% (approx 4.2)")
HORIZON_TOTAL_ACCOUNTS = 12

# Pipeline $M targets are DYNAMIC: target = base factor * YTD engagements.
# 2025 YE Beijing baseline per engagement, +6% uplift.
# Check for wk 11.8 (92 engs): 13.73M / 6.25M / 13.57M -> the 13.7 / 6.2 / 13.6 on the cards.
BASE_FACTOR = {
    "progressed": 0.1408 * 1.06,   # 0.149248
    "created": 0.0641 * 1.06,      # 0.067946
    "won": 0.1391 * 1.06,          # 0.147446
}

# Display precision
UTILIZATION_PRECISION = 2

# --------------------------
# 写回逻辑全部交给 excel_writer.py 自动查重，不再使用手动开关
# --------------------------
# WEEK_LABEL 每次更新周修改这里，例如 "11.8", "11.15"
WEEK_LABEL = "11.8"
