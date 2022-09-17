from pathlib import Path
import sys
from PySide6.QtCore import QMutex, QThreadPool, Qt

from PySide6.QtWidgets import (
    QApplication,
    QCompleter,
    QFileDialog,
    QGraphicsGridLayout,
    QGraphicsWidget,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsWidget,
)

from .thread import Worker

from .xml_parser import defect_from_xml, DefectItem


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        widget = QWidget()
        main_layout = QVBoxLayout()
        self.main_view = QGraphicsView()
        self.open_file = QPushButton("Open Folder")
        self.open_file.clicked.connect(self.btn_openfile)

        main_layout.addWidget(self.main_view)

        bottom_layout = QHBoxLayout()
        main_layout.addLayout(bottom_layout)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.filter_apply)
        bottom_layout.addWidget(self.search_bar)
        bottom_layout.addWidget(self.open_file)

        widget.setLayout(main_layout)

        self.setWindowTitle("Lens Editor")
        self.setGeometry(0, 0, 800, 600)

        # Set the central widget of the Window.
        self.setCentralWidget(widget)
        self.thread_pool = QThreadPool()
        self.mutex = QMutex()

    def filter_apply(self):
        filter_str = self.search_bar.text()
        if filter_str == "":
            self.view_update(self.defects)
            self.status_bar.showMessage(f"No Filter, Total: {len(self.defects)}")
            return
        d_list = list(filter(lambda x: x.name.startswith(filter_str), self.defects))
        self.view_update(d_list)
        self.status_bar.showMessage(f"Filter: {filter_str}, Total: {len(d_list)}")

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
        self.status_bar.showMessage(
            f"Loading files: {self.total_file}/{self.processed_file}"
        )
        self.mutex.unlock()

        if self.processed_file == self.total_file:
            self.defects = sorted(self.defects, key=lambda x: (x.name, x.width, x.height))
            self.view_update(self.defects)
            complete_candidates = list(set([d.name for d in self.defects]))
            completer = QCompleter(complete_candidates)
            self.search_bar.setCompleter(completer)
            self.status_bar.showMessage(
                f"No Filter, Category: {len(complete_candidates)},Total: {len(self.defects)}"
            )

    def view_update(self, d_list):
        g_layout = QGraphicsGridLayout()
        g_widget = QGraphicsWidget()
        scene = QGraphicsScene()
        col_size = 11
        for i, di in enumerate([DefectItem(d) for d in d_list]):
            r = int(i / col_size)
            c = i % col_size
            g_layout.addItem(di, r, c)
        g_widget.setLayout(g_layout)
        scene.addItem(g_widget)
        self.main_view.setScene(scene)
        # self.main_view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
