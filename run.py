import json

from room_csp import Container
from room_csp.ui import setup_and_run_ui

# =========================================================================dd==
#   PROGRAM INITIALIZATION, DATA LOADING
# =========================================================================dd==

# load initial data
with open("input.json", "r") as fd:
    data = json.load(fd)

# initialize data container
Container.initialize(data)

setup_and_run_ui()
