from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from .rule import Ruleset


class RuleEditWindow(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle("Rule Editor")
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_rule)
        layout.addWidget(self.run_button)

    def run_rule(self):
        failed_d_list = []
        rule = Ruleset(self.text_edit.toPlainText())
        for l in self.main_window.lens:
            for d in l.right:
                if rule(d) is not None:
                    failed_d_list.append(d)
        self.main_window.view_update(failed_d_list)

