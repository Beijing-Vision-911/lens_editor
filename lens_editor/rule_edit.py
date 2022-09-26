from PySide6.QtWidgets import (
    QGraphicsSimpleTextItem,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QGraphicsWidget,
    QGraphicsLinearLayout,
)

from PySide6.QtCore import Qt


from .defect import DefectLayoutItem, DefectItem
from .rule import Ruleset


class FilePathItem(QGraphicsSimpleTextItem):
    def __init__(self, text, lens, parent=None):
        super().__init__(text, parent)
        self.setBrush(Qt.red)
        self.lens = lens

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.lens.toggle_visible()
            self.lens.updateGeometry()
        return super().mousePressEvent(event)


class LensWidget(QGraphicsWidget):
    def __init__(self, xml_path, failed, parent=None):
        super().__init__(parent)
        layout = QGraphicsLinearLayout(Qt.Vertical)
        layout.setSpacing(20)
        self.setLayout(layout)
        self.path = FilePathItem(str(xml_path), self)
        layout_item_path = DefectLayoutItem(self.path)
        layout.addItem(layout_item_path)
        self.defects_layout = QGraphicsLinearLayout(Qt.Horizontal)
        layout.addItem(self.defects_layout)
        self.defects = [DefectItem(d, msg=msg) for d, msg in failed]
        self.toggle = False
        for d in self.defects:
            d_layout_item = d.get_layout_item()
            self.defects_layout.addItem(d_layout_item)

    def toggle_visible(self):
        self.toggle = not self.toggle
        if self.toggle:
            for d in self.defects:
                d.setVisible(False)
            self.layout().removeAt(1)
        else:
            for d in self.defects:
                d.setVisible(True)
            self.layout().addItem(self.defects_layout)


class RuleEditWindow(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle("Ruleset")
        self.text_edit = QTextEdit()
        btn_layout = QHBoxLayout()
        layout.addWidget(self.text_edit)
        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)
        layout.addWidget(btn_widget)
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_rule)
        btn_layout.addWidget(self.run_button)
        self.fold_btn = QPushButton("Fold")
        btn_layout.addWidget(self.fold_btn)
        self.fold_btn.clicked.connect(self.fold_toggle)
        self.init_rule_text()

    def init_rule_text(self):
        default = ""
        if hasattr(self.main_window, "rule_set_str"):
            self.text_edit.setText(self.main_window.rule_set_str)
            return
        self.main_window.rule_set_str = default
        self.text_edit.setText(default)

    def fold_toggle(self):
        for i in self.main_window.scene.items():
            if isinstance(i, LensWidget):
                i.toggle_visible()
                i.updateGeometry()

    def run_rule(self):
        self.main_window.rule_set_str = self.text_edit.toPlainText()
        ruleset = Ruleset(self.main_window.rule_set_str)
        self.main_window.scene.clear()
        g_layout = QGraphicsLinearLayout(Qt.Vertical)
        g_widget = QGraphicsWidget()
        g_widget.setLayout(g_layout)
        for l in self.main_window.lens:
            failed = [(d, msg) for d in l.right if (msg := ruleset(d)) is not None]
            if failed:
                g_layout.addItem(LensWidget(l.xml_path, failed))

        self.main_window.scene.addItem(g_widget)
