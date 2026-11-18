from jinja2 import Environment, FileSystemLoader
import os
from config import TEMPLATE_PATH, HTML_OUT_PATH, BASE_DIR
from util.logger import logger

def render_dashboard(kpi_data, week_label):
    env = Environment(loader=FileSystemLoader(os.path.dirname(TEMPLATE_PATH)))
    template = env.get_template(os.path.basename(TEMPLATE_PATH))
    html = template.render(
        week_label=week_label,
        data=kpi_data
    )
    with open(HTML_OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    logger.info("Dashboard html rendered, color line removed, clean title")
    return HTML_OUT_PATH
