from pathlib import Path
from re import S
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
    QInputDialog,
)

from PySide6.QtGui import QPixmapCache, QShortcut, QKeySequence

from .view import View

from .search import FilterParser, QuickSearchSlot

from .thread import Worker

from .defect import defect_from_xml, DefectItem, defect_to_xml

from functools import partial

from typing import List

from itertools import groupby 
class MainWindow(QMainWindow):
    def __init__(self, initial_path=""):
        super().__init__()
        widget : QWidget = QWidget()
        main_layout : QVBoxLayout = QVBoxLayout()
        self.scene : QGraphicsScene = QGraphicsScene()
        self.main_view = View(self.scene)
        QPixmapCache.setCacheLimit(1024 * 1024 * 10)

        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        main_layout.addWidget(self.main_view)

        bottom_layout : QHBoxLayout = QHBoxLayout()
        main_layout.addLayout(bottom_layout)
        self.status_bar : QStatusBar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.search_bar : QLineEdit = QLineEdit()
        self.search_bar.returnPressed.connect(
            lambda: self.filter_apply(self.search_bar.text())
        )
        bottom_layout.addWidget(self.search_bar)

        self.mark_btn : QPushButton = QPushButton("Mark(a)")
        self.mark_btn.clicked.connect(self.mark_btn_clicked)
        bottom_layout.addWidget(self.mark_btn)

        self.save_btn : QPushButton = QPushButton("Save(s)")
        self.save_btn.clicked.connect(self.save_btn_clicked)
        bottom_layout.addWidget(self.save_btn)

        self.rename_btn : QPushButton = QPushButton("Rename(r)")
        self.rename_btn.clicked.connect(self.rename_btn_clicked)
        bottom_layout.addWidget(self.rename_btn)

        self.open_file : QPushButton = QPushButton("Open(o)")
        self.open_file.clicked.connect(self.btn_openfile)
        bottom_layout.addWidget(self.open_file)

        widget.setLayout(main_layout)
        self.setWindowTitle("Lens Editor")
        self.setGeometry(0, 0, 800, 600)
        self.setCentralWidget(widget)

        self.thread_pool : QThreadPool = QThreadPool()
        self.mutex : QMutex = QMutex()
        self.filter_parser : FilterParser = FilterParser()

        self.shortcuts()

        if initial_path:
            self._load_files(initial_path)

    def shortcuts(self) -> None:
        QShortcut(QKeySequence("o"), self, self.btn_openfile)
        QShortcut(QKeySequence("s"), self, self.save_btn_clicked)
        QShortcut(QKeySequence("a"), self, self.mark_btn_clicked)
        QShortcut(QKeySequence("r"), self, self.rename_btn_clicked)

        self.search_slot : QuickSearchSlot = QuickSearchSlot()

        slot_apply = lambda i: self.filter_apply(self.search_slot.get_slot(i), True)
        slot_set = lambda i: self.search_slot.set_slot(i, self.search_bar.text())
        for i in map(str, range(1, 9)):
            QShortcut(i, self, partial(slot_apply, i))
            QShortcut(QKeySequence(f"Ctrl+{i}"), self, partial(slot_set, i))

    def rename_btn_clicked(self) -> None:
        if not hasattr(self, "scene"):
            return
        items = self.scene.selectedItems()
        if len(items) == 0:
            self.status_bar.showMessage("No item selected")
            return
        new_label, ok = QInputDialog.getText(self, "Rename", "New Label:")
        if not ok:
            return

        for i in items:
            i.rename(new_label)

    def save_btn_clicked(self) -> None:
        mod_files_num = defect_to_xml(self.defects)
        self.status_bar.showMessage(f"Saved {mod_files_num} changes")

    def mark_btn_clicked(self) -> None:
        if not hasattr(self, "scene"):
            return
        items = self.scene.selectedItems()
        mark_state = [i.mark_toggle() for i in items]
        marked = len([x for x in mark_state if x])
        unmarked = len([x for x in mark_state if not x])
        message = ""
        if marked > 0:
            message += f"Marked {marked} items. "
        if unmarked > 0:
            message += f"Unmarked {unmarked} items."

        self.status_bar.showMessage(message)

    def filter_apply(self, query, search_bar_update=False) -> None:
        d_list = self.filter_parser.parse(query, self.defects)
        self.view_update(d_list)
        self.status_bar.showMessage(
            f"Filter: {self.search_bar.text()}, Total: {len(d_list)}"
        )
        if search_bar_update:
            self.search_bar.setText(query)

    def _load_files(self, path: str) -> None:
        xml_files = [x for x in Path(path).glob("**/*.xml") if x.is_file()]

        def find_jpeg(xml_file):
            if (jpeg_file := xml_file.with_suffix(".jpeg")).is_file():
                return jpeg_file
            if (
                jpeg_file := xml_file.parents[1] / "img" / f"{xml_file.stem}.jpeg"
            ).is_file():
                return jpeg_file
            print(f"Cannot find jpeg for {xml_file}")
            return None

        parms = [(x, find_jpeg(x)) for x in xml_files if find_jpeg(x)]
        self.defects = []
        self.total_file = len(parms)
        self.processed_file = 0
        for f, j in parms:
            w = Worker(defect_from_xml, f, j)
            w.signals.result.connect(self.worker_done)
            self.thread_pool.start(w)

    def btn_openfile(self) -> None:
        file_path = QFileDialog.getExistingDirectory()
        self._load_files(file_path)

    def worker_done(self, d_list) ->None:
        self.mutex.lock()
        self.defects += d_list
        self.processed_file += 1
        self.status_bar.showMessage(
            f"Loading files: {self.total_file}/{self.processed_file}"
        )
        self.mutex.unlock()

        if self.processed_file == self.total_file:
            self.defects : sorted = sorted(
                self.defects, key=lambda x: (x.name, x.width, x.height)
            )
            self.view_update(self.defects)
            complete_candidates : list = list(set([d.name for d in self.defects]))
            completer : QCompleter = QCompleter(complete_candidates)
            self.search_bar.setCompleter(completer)
            self.status_bar.showMessage(
                f"No Filter, Category: {len(complete_candidates)},Total: {len(self.defects)}"
            )

    def view_update(self, d_list) -> None:
        g_layout : QGraphicsGridLayout = QGraphicsGridLayout()
        g_layout.setContentsMargins(10, 10, 10, 10)
        g_layout.setSpacing(25)
        g_widget : QGraphicsGridLayout= QGraphicsWidget()
        self.scene.clear()
        # dynamic column size, dependents on window width
        col_size = int(self.frameGeometry().width() / 80)
        
        s= [list(g) for k,g in groupby(d_list,key = lambda d:d.name)]
        for j,cls in enumerate(s):
            for i, di in enumerate([DefectItem(d).get_layout_item() for d in s[j]]):
                print(i, di)
                r = int(i / col_size)
                c = i % col_size
                g_layout.addItem(di, r + j*len(s), c)
                
        g_widget.setLayout(g_layout)
        self.scene.addItem(g_widget)
        self.main_view.centerOn(self.scene.itemsBoundingRect().center())

    
def main():
    app = QApplication(sys.argv)
    initial_path = sys.argv[1] if len(sys.argv) > 1 else ""
    window = MainWindow(initial_path)
    window.show()
    app.exec()