# studio-kpi-auto-scorecard
Innovation Studio GCG Weekly KPI automation

## Features
- Auto parse Weekly Performance Scorecard from Excel
- Utilization auto extract, 2 decimal percentage format
- Append weekly KPI row to Goal Tracking Tab2
- Increment merge engagement details to Tab3 (by EVENT ID, no duplicate)
- Render static HTML dashboard
- Removed KPI red/blue line
- Clean title without口径 description
- Horizon Account rule: total=12 accounts, target=12 * 35% = 4.2

## Environment
```bash
python -m venv .venv
# activate venv
pip install -r requirements.txt
