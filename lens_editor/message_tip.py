from PySide6.QtCore import QRect, Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QPushButton


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(150, 54)
        Dialog.setStyleSheet("background: transparent;")
        self.pushButton = QPushButton(Dialog)
        self.pushButton.setGeometry(QRect(0, 0, 151, 51))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.Weight(75)
        self.pushButton.setFont(font)
        self.pushButton.setFocusPolicy(Qt.NoFocus)
        self.pushButton.setContextMenuPolicy(Qt.NoContextMenu)
        self.pushButton.setAutoFillBackground(False)
        self.pushButton.setText("保存成功")
        self.pushButton.setStyleSheet(
            "background-color:rgb(255, 255, 255); border-style:none; padding:8px; border-radius:25px;"
        )


class TipUi(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.timer = QTimer()
        self.setWindowFlags(
            Qt.CustomizeWindowHint
            | Qt.FramelessWindowHint
            | Qt.Tool
            | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_QuitOnClose, True)

        self.windosAlpha = 0
        self.timer.timeout.connect(self.hide_windows)
        self.timer.start(10)

    def hide_windows(self):
        self.windosAlpha += 1
        if self.windosAlpha >= 30:
            self.close()