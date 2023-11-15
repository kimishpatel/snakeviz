import json
import os.path
import re
from pstats import Stats

from termcolor import colored
from tornado import template

from .stats import json_stats, table_rows

snakeviz_dir = os.path.dirname(os.path.abspath(__file__))
snakeviz_templates_dir = os.path.join(snakeviz_dir, "templates")

RESTR = r'(?<!] \+ ")/static/'
REPLACE_WITH = "https://cdn.rawgit.com/jiffyclub/snakeviz/v0.4.2/snakeviz/static/"


def from_pstat_to_static_html(stats: Stats, html_filename: str):
    """
    Parses pstats data and populates viz.html template stored under templates dir.
    This utility allows to export html file without kicking off webserver.

    Note that it relies js scripts stored at rawgit cdn. This is not super
    reliable, however it does allow one to not have to rely on webserver and
    local rendering. On the other hand, for local rendering please follow
    the main snakeviz tutorial

    Args:
        stats: Stats generated from cProfile data
        html_filename: Output filename in which populated template is rendered
    """
    if not isinstance(html_filename, str):
        raise ValueError("A valid file name must be provided.")

    viz_html_loader = template.Loader(snakeviz_templates_dir)
    html_bytes_renderer = viz_html_loader.load("viz.html")
    file_split = html_filename.split(".")
    if len(file_split) < 2:
        raise ValueError(
            f"\033[0;32;40m Provided filename \033[0;31;47m {html_filename} \033[0;32;40m does not contain . separator."
        )
    profile_name = file_split[0]
    html_bytes = html_bytes_renderer.generate(
        profile_name=profile_name,
        table_rows=table_rows(stats),
        callees=json_stats(stats),
    )
    html_string = html_bytes.decode("utf-8")
    html_string = re.sub(RESTR, REPLACE_WITH, html_string)
    with open(html_filename, "w") as f:
        f.write(html_string)
