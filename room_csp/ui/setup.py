import sys

from PyQt5 import QtWidgets

from room_csp.ui.windows.main_window import MainWindow


def setup_and_run_ui():
    app = QtWidgets.QApplication(sys.argv)

    # initialize and display MainWindow
    main = MainWindow()
    main.show()

    app.exec_()
