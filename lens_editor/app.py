from pathlib import Path
import sys
from PySide6.QtCore import QMutex, QThreadPool

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGraphicsGridLayout,
    QGraphicsWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsWidget,
)

from lens_editor.thread import Worker

from .xml_parser import defect_from_xml, DefectItem


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        widget = QWidget()
        layout = QVBoxLayout()
        self.main_view = QGraphicsView()
        self.open_file = QPushButton("Open Folder")
        self.open_file.clicked.connect(self.btn_openfile)

        layout.addWidget(self.main_view)
        layout.addWidget(self.open_file)
        widget.setLayout(layout)

        self.setWindowTitle("Lens Editor")
        self.setGeometry(0, 0, 800, 600)

        # Set the central widget of the Window.
        self.setCentralWidget(widget)
        self.thread_pool = QThreadPool()
        self.mutex = QMutex()

    def btn_openfile(self):
        self.defects = []
        file_path = Path(QFileDialog.getExistingDirectory())
        xml_files = [x for x in file_path.rglob("*.xml")]
        self.total_file = len(xml_files)
        self.processed_file = 0
        for f in xml_files:
            w = Worker(defect_from_xml, f)
            w.signals.result.connect(self.view_append)
            self.thread_pool.start(w)

    def view_append(self, d_list):
        self.mutex.lock()
        self.defects += d_list
        self.processed_file += 1
        print(self.total_file, "/", self.processed_file)
        self.mutex.unlock()

        if self.processed_file == self.total_file:
            self.view_create(self.defects)

    def view_create(self, d_list):
        g_layout = QGraphicsGridLayout()
        g_widget = QGraphicsWidget()
        scene = QGraphicsScene()
        for i, di in enumerate([DefectItem(x) for x in d_list]):
            r = int(i / 6)
            c = i % 6
            g_layout.addItem(di, r, c)
        g_widget.setLayout(g_layout)
        scene.addItem(g_widget)
        self.main_view.setScene(scene)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
