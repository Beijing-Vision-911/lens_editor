import sys

from PySide6.QtWidgets import (
    QApplication,
    QGraphicsWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsLinearLayout,
    QGraphicsWidget,
)

from .xml_parser import defects, DefectItem


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        widget = QWidget()
        layout = QVBoxLayout()
        self.main_view = QGraphicsView()
        self.open_file = QPushButton("Open Folder")
        layout.addWidget(self.main_view)
        layout.addWidget(self.open_file)
        widget.setLayout(layout)

        self.setWindowTitle("Lens Editor")
        self.view_create()

        # Set the central widget of the Window.
        self.setCentralWidget(widget)

        # self.open_file.clicked.connect(self.view_create)

    def view_create(self):
        # g_layout = QGraphicsLinearLayout()
        # g_widget = QGraphicsWidget()
        scene = QGraphicsScene()
        for d in defects:
            d._crop_image()
        for di in [DefectItem(x) for x in defects]:
            scene.addItem(di)
        self.main_view.setScene(scene)
        


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()



