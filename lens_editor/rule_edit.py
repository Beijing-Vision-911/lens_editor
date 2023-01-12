import shutil
import logging
import sys

from pathlib import Path
from typing import Any, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFileDialog, QGraphicsLinearLayout,
                               QGraphicsSimpleTextItem, QGraphicsWidget,
                               QHBoxLayout, QPushButton, QTextEdit,
                               QVBoxLayout, QWidget)

from .config import Config
from .defect import Defect, DefectItem, DefectLayoutItem
from .rule import Ruleset
from .app import MainWindow


level = logging.ERROR if sys.argv[-1] != "-d" else logging.INFO
logging.basicConfig(level=level, format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)



class FilePathItem(QGraphicsSimpleTextItem):
    def __init__(self, text:str, lens:Any, color:Qt.GlobalColor, parent=None) -> None:
        super().__init__(text, parent)
        self.setBrush(color)
        self.lens = lens

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.lens.toggle_visible()
            self.lens.updateGeometry()
        return super().mousePressEvent(event)


class LensWidget(QGraphicsWidget):
    def __init__(self, xml_path:List, failed:List, color:Qt.GlobalColor, parent=None) -> None:
        super().__init__(parent)
        layout = QGraphicsLinearLayout(Qt.Vertical)
        layout.setSpacing(20)
        self.setLayout(layout)
        self.path:FilePathItem = FilePathItem(str(xml_path), self, color)
        layout_item_path = DefectLayoutItem(self.path)
        layout.addItem(layout_item_path)
        self.defects_layout = QGraphicsLinearLayout(Qt.Horizontal)
        layout.addItem(self.defects_layout)
        self.defects[DefectItem] = [DefectItem(d, msg=msg) for d, msg in failed]
        self.toggle = False
        for d in self.defects:
            d_layout_item = d.get_layout_item()
            self.defects_layout.addItem(d_layout_item)

    def toggle_visible(self) -> None:
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
    def __init__(self, main_window:MainWindow, parent=None) -> None:
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
        self.add_btn = QPushButton("Uncretain")
        self.add_btn.clicked.connect(self.add_uncretain)
        btn_layout.addWidget(self.add_btn)
        self.cfg = Config()  # type: ignore
        self.init_rule_text()

    def init_rule_text(self) -> None:
        d = 2194
        b = 1960
        d1 = 1329
        a = 1710
        ld = 1055
        lb = 815
        K1 = 1
        K3 = 2.33
        K6 = 1.67
        K7 = 1.57
        K8 = 1.5
        K9 = 1.44
        K10 = 1.4
        K12 = 1.33
        K13 = 1.31
        K14 = 1.29
        K15 = 1.27
        K18 = 1.22
        K3122 = 2194
        K3242 = 2225
        default = f"""0100 x>{d1} x<{d} L2
0100 x>{d1} x<{d} L3
0101 x>{d1} x<={a} w>7*{K7}
0101 x>{d1} x<={a} w<=7*{K7} -2
0101 x>{d1} x<={a} w<=7*{K7} -3
0101 x>{a} x<={b} w>12*{K12}
0101 x>{a} x<={b} w<=12*{K12} -2
0101 x>{a} x<={b} w<=12*{K12} -3
0102 x>{d1} x<={a} w>=20*1
0102 x>{d1} x<={a} w>9*1 w<20*1 -2
0102 x>{d1} x<={a} w>9*1 w<20*1 -3
0102 x>1710 x<=1960 w>=20*1
0102 x>1710 x<=1960 w>8*1 w<20*1 -2
0102 x>1710 x<=1960 w>8*1 w<20*1 -3
0103 x>1329 x<=1710 w>13*1
0103 x>1329 x<=1710 w<=13*1 w>11*1 -2
0103 x>1329 x<=1710 w<=13*1 w>=11*1 -3
0103 x>1710 x<=1960 w>=13*1
0103 x>1710 x<=1960 w<13*1 w>11*1 -2
0103 x>1710 x<=1960 w<13*1 w>11*1 -3 
0104 x>{d1} x<{d} -2
0104 x>{d1} x<{d} -3
1101 x>{d1} x<{d} -2
1102 x>{d1} x<{d} -0
1102 x>{d1} x<{d} -1
1102 x>{d1} x<{d} -2
1102 x>{d1} x<{d} -3
1102 x>{d1} x<{d} -4
1102 x>{d1} x<{d} w>=7*{K7}
1103 x>{d1} x<{d} w>7*{K7}
1103 x>{d1} x<{d} w<=7*{K7} -2
1104 x>{d1} x<{d}
1201 x>{a} x<={b} w>=12*{K12} -0
1201 x>{a} x<={b} w>=12*{K12} -1
1201 x>{a} x<={b} w>=12*{K12} -2
1201 x>{a} x<={b} w>=12*{K12} -3
1201 x>{a} x<={b} w>=12*{K12} -4
1201 x>{b} x<={d} w>=13*{K13} -0
1201 x>{b} x<={d} w>=13*{K13} -1
1201 x>{b} x<={d} w>=13*{K13} -2
1201 x>{b} x<={d} w>=13*{K13} -3
1201 x>{b} x<={d} w>=13*{K13} -4
1202 x>{a} x<={b} w>=9*{K9}
1202 x>{b} x<={d} w>=10*{K10}
1203 x>{a} x<={b} w>=10*{K10}
1203 x>{b} x<={d} w>=12*{K12}
1302 x>{a} x<={b} w>=18
1302 x>{a} x<={b} w>14 w<18 -0
1302 x>{a} x<={b} w>14 w<18 -1
1302 x>{a} x<={b} w>14 w<18 -2
1302 x>{a} x<={b} w>14 w<18 -3
1302 x>{b} x<={d} w>10 -0
1302 x>{b} x<={d} w>10 -1
1302 x>{b} x<={d} w>10 -2
1302 x>{b} x<={d} w>10 -3
1303 x>{d1} x<={a} w>=9
1303 x>{d1} x<={a} w>7 w<9 -2
1303 x>{d1} x<={a} w>7 w<9 -3
1303 x>{a} x<={b} w>=12
1303 x>{a} x<={b} w>7 w<12 -2
1303 x>{b} x<={d} w>=15
1303 x>{b} x<={d} w>10 w<15 -2
1402 x>{a} x<={b} -0
1402 x>{a} x<={b} -1
1402 x>{a} x<={b} -2
1402 x>{a} x<={b} -3
1402 x>{a} x<={b} -4
1403 x>{a} x<={b} w>=14*{K14}
1403 x>{a} x<={b} -2
1403 x>{a} x<={b} -3
1403 x>{b} x<={d} -2
1702 x>{d1} x<={d} -0 W>3*{K3} H>3*{K3}
1702 x>{d1} x<={d} -1 W>3*{K3} H>3*{K3}
1702 x>{d1} x<={d} -2 W>3*{K3} H>3*{K3}
1702 x>{d1} x<={d} -3 W>3*{K3} H>3*{K3}
1702 x>{d1} x<={d} -4 W>3*{K3} H>3*{K3}
2002 x>{d1} x<{d} 
2102 x>{d1} x<{d} L0
2102 x>{d1} x<{d} L1
2102 x>{d1} x<{d} L2
2102 x>{d1} x<{d} L3
2102 x>{d1} x<{d} L4
2103 x>{d1} x<={a} w>=40
2103 x>{d1} x<={a} h>=40
2103 x>{d1} x<={a} w>19 -1
2103 x>{d1} x<={a} h<40 -1
2103 x>{d1} x<={a} w>19 -2
2103 x>{d1} x<={a} h<40 -2
2103 x>{d1} x<={a} w>19 -3
2103 x>{d1} x<={a} h<40 -3
2103 x>{a} x<={b} w>=42
2103 x>{a} x<={b} h>=42
2103 x>{a} x<={b} w>=20 -1
2103 x>{a} x<={b} h<42 -1
2103 x>{a} x<={b} w>=20 -2
2103 x>{a} x<={b} h<42 -2
2103 x>{a} x<={b} w>=20 -3
2103 x>{a} x<={b} h<42 -3
2103 x>{b} x<={d} w>=40
2103 x>{b} x<={d} h>=40
2103 x>{b} x<={d} w>=24 -1
2103 x>{b} x<={d} h<40 -1
3122 x>{d1} x<={K3122}
3123 x>{d1} x<={K3122} w>=12*{K12} h>=12*{K12}
3123 x>{d1} x<={K3122} w<12*{K12} L2
3123 x>{d1} x<={K3122} h<12*{K12} L2
3132 x<{d} x<={d}
3133 x<{d} x<={d}
3242 x<{K3242}
4112 x>{d1} x<{d} L0
4112 x>{d1} x<{d} L1
4112 x>{d1} x<{d} L2
4112 x>{d1} x<{d} L3
4112 x>{d1} x<{d} L4
4113 x>{d1} x<{d} L0
4113 x>{d1} x<{d} L1
4113 x>{d1} x<{d} L2
4113 x>{d1} x<{d} L3
4113 x>{d1} x<{d} L4
"""
        default_rule = self.cfg.setup("rule", "default", default)
        if hasattr(self.main_window, "rule_set_str"):
            self.text_edit.setText(self.main_window.rule_set_str)
            return
        self.main_window.rule_set_str = default_rule
        self.text_edit.setText(default_rule)
        self.text_edit.textChanged.connect(self.on_msg_str_slot)

    def on_msg_str_slot(self) -> None:
        self.cfg.set("rule", "default", self.text_edit.toPlainText())

    def add_uncretain(self) -> None:
        self.uncretain = UncertainEditWindow(self.main_window, self.cfg)
        self.uncretain.show()

    def fold_toggle(self) -> None:
        for i in self.main_window.scene.items():
            if isinstance(i, LensWidget):
                i.toggle_visible()
                i.updateGeometry()

    def run_rule(self) -> None:
        if hasattr(self.main_window, "un_rule_set_str"):
            self.main_window.un_rule_set_str = self.uncretain.un_text_edit.toPlainText()
            un_ruleset = Ruleset(self.main_window.un_rule_set_str)
        self.main_window.rule_set_str = self.text_edit.toPlainText()
        ruleset = Ruleset(self.main_window.rule_set_str)
        self.main_window.scene.clear()
        g_layout = QGraphicsLinearLayout(Qt.Vertical)
        g_widget = QGraphicsWidget()
        g_widget.setLayout(g_layout)
        a:int = 0
        good:List[Any] = []
        li:List[Any] = []
        helist:List[Any] = []
        for l in self.main_window.lens:
            failed = [(d, msg) for d in l.defects if (msg := ruleset(d)) is not None]  # type: ignore
            if failed:
                g_layout.addItem(LensWidget(l.xml_path, failed, Qt.red))
                li.append(int(l.xml_path.stem))
                a += 1
            else:
                good.append(l)
        logger.info(f"不合格=={a}")
        logger.info(sorted(li))
        b = 0
        for g in good:
            un_failed = [
                (d, msg) for d in g.defects if (msg := un_ruleset(d)) is not None  # type: ignore
            ]
            if un_failed:
                g_layout.addItem(LensWidget(g.xml_path, un_failed, Qt.green))
                b += 1
            else:
                helist.append(int(g.xml_path.stem))
        logger.info(f"不确定=={b}")
        logger.info(f"合格=={len(helist)}")
        logger.info(sorted(helist))
        self.main_window.scene.addItem(g_widget)

    def export_btn_clicked(self) -> None:
        path: str = QFileDialog.getExistingDirectory(self, "getExistingDirectory")
        logger.info(Path(path))
        for l in self.list:
            if not (dir := Path(path) / "不合格").exists():
                dir.mkdir()
            shutil.copy(l, dir)
            shutil.copy(l, dir)
        for i in self.list1:
            if not (dir := Path(path) / "合格").exists():
                dir.mkdir()
            shutil.copy(i, dir)
            shutil.copy(i, dir)


class UncertainEditWindow(QWidget):
    def __init__(self, main_window:MainWindow, cfg:Any, parent=None) -> None:
        super().__init__(parent)
        self.move(450, 150)
        self.main_window = main_window
        self.cfg = cfg
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle("Uncertain Ruleset")
        self.un_text_edit = QTextEdit()
        layout.addWidget(self.un_text_edit)
        self.init_un_rule_text()

    def init_un_rule_text(self) -> None:
        d = 2194
        d1 = 1329
        a = 1710
        b = 1960
        K1 = 1
        K3 = 2.33
        K6 = 1.67
        K7 = 1.57
        K8 = 1.5
        K9 = 1.44
        K10 = 1.4
        K12 = 1.33
        K13 = 1.31
        K14 = 1.29
        K15 = 1.27
        K18 = 1.22
        uncertain_default = f"""0100 x>{d1} x<{d} L1
0101 x>{d1} x<={a} w<=7*{K7} -1
0101 x>{a} x<{d} w<=12*{K7} -1
0102 x>1329 x<=1710 w>9*1 w<20*1 -0
0102 x>1329 x<=1710 w>9*1 w<20*1 -1
0102 x>1710 x<=1960 w>8*1 w<20*1 -0
0102 x>1710 x<=1960 w>8*1 w<20*1 -1
0103 x>1329 x<=1710 w<=13*1 w>11*1 -0
0103 x>1329 x<=1710 w<=13*1 w>11*1 -1
0103 x>1710 x<=1960 w<13*1 w>11*1 -0
0103 x>1710 x<=1960 w<13*1 w>11*1 -1
1101 x>{d1} x<{d} -3
1103 x>{d1} x<{d} w==7*{K7} w==6*{K6}
1103 x>{d1} x<{d} w<=7*{K7} -3
1201 x>{a} x<={b} w<12*{K12} -0
1201 x>{a} x<={b} w<12*{K12} -1
1201 x>{a} x<={b} w<12*{K12} -2
1201 x>{a} x<={b} w<12*{K12} -3
1201 x>{a} x<={b} w<12*{K12} -4
1201 x>{b} x<={d} w<13*{K13} -0
1201 x>{b} x<={d} w<13*{K13} -1
1201 x>{b} x<={d} w<13*{K13} -2
1201 x>{b} x<={d} w<13*{K13} -3
1201 x>{b} x<={d} w<13*{K13} -4
1202 x>{a} x<={b} w<9*{K9} -0
1202 x>{a} x<={b} w<9*{K9} -1
1202 x>{a} x<={b} w<9*{K9} -2
1202 x>{a} x<={b} w<9*{K9} -3
1202 x>{a} x<={b} w<9*{K9} -4
1202 x>{b} x<={d} w<10*{K10} -0
1202 x>{b} x<={d} w<10*{K10} -1
1202 x>{b} x<={d} w<10*{K10} -2
1202 x>{b} x<={d} w<10*{K10} -3
1202 x>{b} x<={d} w<10*{K10} -4
1203 x>{a} x<={b} w<10*{K10} -1
1203 x>{a} x<={b} w<10*{K10} -2
1203 x>{a} x<={b} w<10*{K10} -3
1203 x>{b} x<={d} w<12*{K12} -1
1203 x>{b} x<={d} w<12*{K12} -2
1203 x>{b} x<={d} w<12*{K12} -3
1303 x>{d1} x<={a} w>7 w<9 -1
1303 x>{a} x<={b} w>7 w<12 -3
1303 x>{b} x<={d} w>10 w<15 -3
1403 x>{b} x<={d} -3
1403 x>{a} x<={b} w>=12*{K12} w<14*{K14}
1502 x>119 x<=815
1702 x>{d1} x<{d}
2001 x>{d1} x<={d} L0
2001 x>{d1} x<={d} L1
2001 x>{d1} x<={d} L2
2001 x>{d1} x<={d} L3
2001 x>{d1} x<={d} L4
2101 x>{d1} x<{d} L0
2101 x>{d1} x<{d} L1
2101 x>{d1} x<{d} L2
2101 x>{d1} x<{d} L3
2101 x>{d1} x<{d} L4
2102 x>{d1} x<{d}
2103 x>{d1} x<={a} w>19 -0
2103 x>{d1} x<={a} h<40 -0
2103 x>{a} x<={b} w>=20 -0
2103 x>{a} x<={b} h<42 -0
2103 x>{b} x<={d} w>=24 -0
2103 x>{b} x<={d} h<40 -0
2103 x>{b} x<={d} w>=24 -2
2103 x>{b} x<={d} h<40 -2
2103 x>{b} x<={d} w>=24 -3
2103 x>{b} x<={d} h<40 -3
2512 x>119 x<=1085
2612 x>119 x<=1085
4112 x>{d1} x<{d}
"""
        un_default_rule = self.cfg.setup("rule", "uncertain_default", uncertain_default)
        if hasattr(self.main_window, "un_rule_set_str"):
            self.un_text_edit.setText(self.main_window.un_rule_set_str)
            return
        self.main_window.un_rule_set_str = un_default_rule
        self.un_text_edit.setText(un_default_rule)
        self.un_text_edit.textChanged.connect(self.un_text_slot)

    def un_text_slot(self) -> None:
        self.cfg.set("rule", "uncertain_default", self.un_text_edit.toPlainText())
