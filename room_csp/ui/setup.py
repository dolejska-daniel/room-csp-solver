import sys

from PyQt5 import QtWidgets

from room_csp.ui.windows.main_window import MainWindow


def setup_and_run_ui():
    try:
        app = QtWidgets.QApplication(sys.argv)

        # initialize and display MainWindow
        main = MainWindow()
        main.show()

        app.exec_()
    except Exception as e:
        print(repr(e), file=sys.stderr)
        import traceback
        traceback.print_exc()

        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(
            None, "Application failed to initialize",
            "Application could not be started - an exception occured during its initialization."
            "\nConsole output may contain additional information.",
            QMessageBox.Ok
        )

        exit(1)
