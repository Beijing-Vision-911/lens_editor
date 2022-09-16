import xml.etree.ElementTree as ET
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsLayoutItem
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
        self._root.remove(self._obj)


def numpy2pixmap(np_img) -> QPixmap:
    height, width, channel = np_img.shape
    qimg = QImage(
        np_img.data, width, height, width * channel, QImage.Format_RGB888
    ).rgbSwapped()
    return QPixmap(qimg)


class DefectNodeItem(QGraphicsPixmapItem):
    def __init__(self, node: Defect):
        super().__init__()
        self.node: Defect = node
        self.setPixmap(numpy2pixmap(node.image))

    def mouseDoubleClickEvent(self, event) -> None:
        print(self.node, self.node.file_path)
        return 


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
    


