from PyQt5.QtCore import QThread, pyqtSignal

from room_csp.logic import RoomAssignmentProblem


class SolverThread(QThread):
    status_changed = pyqtSignal(str)
    solution_found = pyqtSignal(dict)
    solution_not_found = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def __del__(self):
        self.wait()

    def run(self) -> None:
        problem = RoomAssignmentProblem()

        try:
            self.status_changed.emit("Solving...")
            solution = problem.getSolution()
            self.status_changed.emit("Solving done!")
            if solution is None:
                self.solution_not_found.emit()

            else:
                self.solution_found.emit(solution)

        except Exception:
            import traceback
            traceback.print_exc()
