import json

from room_csp import Container
from room_csp.ui import setup_and_run_ui
from room_csp.utils import pyqt_enable_exceptions

# =========================================================================dd==
#   PROGRAM INITIALIZATION, DATA LOADING
# =========================================================================dd==

# load initial data
with open("test/init.json", "r") as fd:
    data = json.load(fd)

# initialize data container
Container.initialize(data)

pyqt_enable_exceptions()
setup_and_run_ui()
