import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "FUR System"
extensions = ["myst_parser"]
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
html_theme = "alabaster"
