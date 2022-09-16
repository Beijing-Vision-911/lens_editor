import xml.etree.ElementTree as ET
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGraphicsPixmapItem,
    QGraphicsLayoutItem,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QPixmap, QImage
import cv2
import numpy as np
from pathlib import Path


class Defect:
    def __init__(self, file_path: Path, root, obj, img):
        self.file_path: Path = file_path
        self._root = root
        self._obj = obj
        self._parse_obj(obj)
        self._crop(img)
        self.changed = False

    def __repr__(self) -> str:
        return f"{self.name}: {self.xmin}, {self.ymin}, {self.xmax}, {self.ymax}"

    @property
    def name(self):
        pass

    @name.getter
    def name(self):
        return self._obj.find("name").text

    @name.setter
    def name(self, new_name):
        self._obj.set("name", new_name)
        self.changed = True

    def _parse_obj(self, obj):
        self.xmin = int(obj.find("bndbox/xmin").text)
        self.ymin = int(obj.find("bndbox/ymin").text)
        self.xmax = int(obj.find("bndbox/xmax").text)
        self.ymax = int(obj.find("bndbox/ymax").text)

    def _crop(self, orig_img):
        self.image = orig_img[self.ymin : self.ymax, self.xmin : self.xmax].copy()
        img_path = self.file_path.parents[1] / "img" / (self.file_path.stem + ".jpeg")
        if not img_path.exists():
            self.image = None
            return
        img = cv2.imread(str(img_path))
        self.image = img[self.ymin : self.ymax, self.xmin : self.xmax].copy()

    def remove(self):
        self.changed = True
        self._root.remove(self._obj)


def numpy2pixmap(np_img) -> QPixmap:
    height, width, channel = np_img.shape
    qimg = QImage(
        np_img.data, width, height, width * channel, QImage.Format_RGB888
    ).rgbSwapped()
    return QPixmap(qimg)


class DefectEdit(QWidget):
    def __init__(self, defect, parent=None) -> None:
        super().__init__(parent)
        self.defect = defect
        layout = QGridLayout()
        self.setLayout(layout)
        label_name = QLabel("Name:")
        label_name_field = QLabel(self.defect.name)
        label_f_path = QLabel("Path:")
        label_f_path_field = QLabel(str(self.defect.file_path))
        label_coordinate = QLabel("Coordinate:")
        label_coordinate_field = QLabel(
            f"({self.defect.xmin}, {self.defect.ymin}) ({self.defect.xmax}, {self.defect.ymax})"
        )
        label_defect = QLabel()
        label_defect.setAlignment(Qt.AlignCenter)
        label_defect.setPixmap(
            numpy2pixmap(self.defect.image).scaledToWidth(200, Qt.SmoothTransformation)
        )

        layout.addWidget(label_name, 0, 0)
        layout.addWidget(label_name_field, 0, 1)
        layout.addWidget(label_f_path, 1, 0)
        layout.addWidget(label_f_path_field, 1, 1)
        layout.addWidget(label_coordinate, 2, 0)
        layout.addWidget(label_coordinate_field, 2, 1)
        layout.addWidget(label_defect, 3, 0, 1, 2)

        # self. = QLabel()
        # layout.addWidget(self.label)
        # self.label.setText(self.defect.name)


class DefectNodeItem(QGraphicsPixmapItem):
    def __init__(self, node: Defect):
        super().__init__()
        self.node: Defect = node
        self.setPixmap(numpy2pixmap(node.image).scaledToWidth(60, Qt.SmoothTransformation))

    def mouseDoubleClickEvent(self, _) -> None:
        self.defect_edit = DefectEdit(self.node)
        self.defect_edit.show()


class DefectItem(QGraphicsLayoutItem):
    def __init__(self, node, parent=None, isLayout=False):
        super().__init__(parent, isLayout)
        self.node_item = DefectNodeItem(node)
        self.setGraphicsItem(self.node_item)

    def sizeHint(self, which, const):
        return self.node_item.boundingRect().size()

    def setGeometry(self, rect):
        return self.node_item.setPos(rect.topLeft())


def defect_from_xml(f_name):
    tree = ET.parse(f_name)
    root = tree.getroot()
    img_path = f_name.parents[1] / "img" / (f_name.stem + ".jpeg")
    if not img_path.exists():
        raise Exception(f"No corresponding image file for {f_name}")
    img = cv2.imread(str(img_path))
    return [Defect(f_name, root, obj, img) for obj in root.iter("object")]
