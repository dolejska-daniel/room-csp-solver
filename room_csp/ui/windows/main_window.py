from PyQt5.uic import loadUiType

qt_creator_file = "ui/main_window.ui"
Ui_MainWindow, QMainWindow = loadUiType(qt_creator_file)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle("ESC Room CSP Solver")
