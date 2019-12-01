

def pyqt_enable_exceptions():
    import sys

    sys._excepthook = sys.excepthook

    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = exception_hook


def pyqt_debug_trace():
    import pdb
    import sys

    from PyQt5.QtCore import pyqtRemoveInputHook

    pyqtRemoveInputHook()
    pdb.set_trace()

    # set up the debugger
    debugger = pdb.Pdb()
    debugger.reset()

    # custom next to get outside of function scope
    debugger.do_next(None)  # run the next command

    users_frame = sys._getframe().f_back  # frame where the user invoked `pyqt_set_trace()`
    debugger.interaction(users_frame, None)
