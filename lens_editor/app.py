from distutils.command.config import config
import logging
from argparse import ArgumentParser, Namespace
import cv2
from itertools import chain
from pathlib import Path
import sys
from venv import create
from PySide6.QtCore import QMutex, QThreadPool, Qt
import PySide6.QtGui 
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
    QLabel,
    QMessageBox
)

from PySide6.QtGui import QPixmapCache, QShortcut, QKeySequence
from .view import View

from .search import FilterParser, QuickSearchSlot

from .thread import Worker

from .config import root_config,Config
from .defect import DefectItem, Lens
from .rule_edit import RuleEditWindow

from functools import partial

from typing import List


class MainWindow(QMainWindow):
    def __init__(self, initial_path=""):
        super().__init__()
        
        widget = QWidget()
        main_layout = QVBoxLayout()
        self.scene = QGraphicsScene()
        self.main_view = View(self.scene)
        QPixmapCache.setCacheLimit(1024 * 1024 * 10)

        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        main_layout.addWidget(self.main_view)

        bottom_layout = QHBoxLayout()
        main_layout.addLayout(bottom_layout)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(
            lambda: self.filter_apply(self.search_bar.text())
        )
        bottom_layout.addWidget(self.search_bar)

        self.rule_edit_btn = QPushButton("Rule")
        self.rule_edit_btn.clicked.connect(self.rule_edit_btn_clicked)
        bottom_layout.addWidget(self.rule_edit_btn)

        self.mark_btn = QPushButton("Mark(a)")
        self.mark_btn.clicked.connect(self.mark_btn_clicked)
        bottom_layout.addWidget(self.mark_btn)

        self.save_btn = QPushButton("Save(s)")
        self.save_btn.clicked.connect(self.save_btn_clicked)
        bottom_layout.addWidget(self.save_btn)

        self.rename_btn = QPushButton("Rename(r)")
        self.rename_btn.clicked.connect(self.rename_btn_clicked)
        bottom_layout.addWidget(self.rename_btn)

        self.open_file = QPushButton("Open(o)")
        self.open_file.clicked.connect(self.btn_openfile)
        bottom_layout.addWidget(self.open_file)

        self.convert_btn = QPushButton("Convert(c)")
        bottom_layout.addWidget(self.convert_btn)

        self.nver_btn = QPushButton("Nver(c)")
        bottom_layout.addWidget(self.nver_btn)
        self.nver_btn.clicked.connect(self.savepixmap)

        widget.setLayout(main_layout)
        self.setWindowTitle("Lens Editor")
        self.setGeometry(0, 0, 800, 600)
        self.setCentralWidget(widget)

        self.thread_pool = QThreadPool()
        self.mutex = QMutex()
        self.filter_parser = FilterParser()
    
        self.shortcuts()

        if initial_path:
            self._load_files(initial_path)

    def shortcuts(self):
        QShortcut(QKeySequence("o"), self, self.btn_openfile)
        QShortcut(QKeySequence("s"), self, self.save_btn_clicked)
        QShortcut(QKeySequence("a"), self, self.mark_btn_clicked)
        QShortcut(QKeySequence("r"), self, self.rename_btn_clicked)
        # QShortcut(QKeySequence("c"), self, self.convert_btn_clicked)
        self.search_slot = QuickSearchSlot()

        slot_apply = lambda i: self.filter_apply(self.search_slot.get_slot(i), True)
        slot_set = lambda i: self.search_slot.set_slot(i, self.search_bar.text())
        for i in map(str, range(1, 9)):
            QShortcut(i, self, partial(slot_apply, i))
            QShortcut(QKeySequence(f"Ctrl+{i}"), self, partial(slot_set, i))

    def rule_edit_btn_clicked(self):
        self.rule_window = RuleEditWindow(main_window=self)
        self.convert_btn.clicked.connect(self.rule_window.convert_btn_clicked)
        self.rule_window.show()

    def rename_btn_clicked(self):
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

    def save_btn_clicked(self):
        mod_files_num = len([i for i in self.lens if i.modified])
        for i in self.lens:
            i.save()
        self.status_bar.showMessage(f"Saved {mod_files_num} changes")

    def mark_btn_clicked(self):
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
    def nver_edit(self):
        editss = RuleEditWindow()
        self.nver_btn.clicked.connect(self.rule_window.nver_btn_clicked)
        
    def filter_apply(self, query, search_bar_update=False):
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

        self.lens = []
        self.total_file = len(parms)
        self.processed_file = 0  
        for f, j in parms:
            w = Worker(Lens, f, j)
            w.signals.result.connect(self.worker_done)
            self.thread_pool.start(w)

    def btn_openfile(self):
        file_path = QFileDialog.getExistingDirectory()
        self._load_files(file_path)

    def worker_done(self, lz):
        self.mutex.lock()
        self.lens.append(lz)
        self.processed_file += 1
        self.status_bar.showMessage(
            f"Loading files: {self.total_file}/{self.processed_file}"
        )
        self.mutex.unlock()

        if self.processed_file == self.total_file:
            self.defects = sorted(
                chain(*[l.defects for l in self.lens]),
                key=lambda x: (x.name, x.width, x.height),
            )
            self.view_update(self.defects)
            complete_candidates = list(set([d.name for d in self.defects]))
            completer = QCompleter(complete_candidates)
            self.search_bar.setCompleter(completer)
            self.status_bar.showMessage(
                f"No Filter, Category: {len(complete_candidates)},Total: {len(self.defects)}"
            )

    def view_update(self, d_list):
        g_layout = QGraphicsGridLayout()
        g_layout.setContentsMargins(10, 10, 10, 10)
        g_layout.setSpacing(25)
        g_widget = QGraphicsWidget()
        self.scene.clear()
        # dynamic column size, dependents on window width
        col_size = int(self.frameGeometry().width() / 80)
        for i, di in enumerate([DefectItem(d).get_layout_item() for d in d_list]):
            r = int(i / col_size)
            c = i % col_size
            g_layout.addItem(di, r, c)
        g_widget.setLayout(g_layout)
        self.scene.addItem(g_widget)
        self.main_view.centerOn(self.scene.itemsBoundingRect().center())

    def closeEvent(self, event: PySide6.QtGui.QCloseEvent) -> None:   
        reply = QMessageBox.question(self,'提示','是否关闭所有窗口',
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
            sys.exit(0)
        else:
            event.ignore()
        # return super().closeEvent(event)
    def savepixmap(self):
        for d in self.defects:
            self.name = d.name
            self.image = d.image
            self._name =d.lens.xml_path.stem
            print(self.name)
            cv2.imwrite(f"/home/user/桌面/a/{self._name}_{self.name}.jpeg",self.image)


def main():
    root_config("~/.tes")
    app = QApplication(sys.argv)
    initial_path = sys.argv[1] if len(sys.argv) > 1 else ""
    window = MainWindow(initial_path)
    window.show()
    app.exec()