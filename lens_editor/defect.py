import xml.etree.ElementTree as ET
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGraphicsPixmapItem,
    QGraphicsLayoutItem,
    QGridLayout,
    QLabel,
    QWidget,
    QGraphicsItem,
)
from PySide6.QtGui import QPixmap, QImage
import cv2
from pathlib import Path
from itertools import groupby
from typing import List


class Defect:
    def __init__(self, file_path: Path, tree, obj, img):
        self.file_path: Path = file_path
        self.tree = tree
        self._obj = obj
        self._parse_obj(obj)
        self._crop(img)
        # modify state of xml file, set to true after changes have benn saved
        self.modified = False
        # mark state
        self.mark = False

    def __repr__(self) -> str:
        return f"Defect[{self.name}: {self.xmin}, {self.ymin}, {self.xmax}, {self.ymax}]"

    @property
    def name(self):
        pass

    @name.getter
    def name(self):
        return self._obj.find("name").text

    @name.setter
    def name(self, new_name):
        name = self._obj.find("name")
        name.text = new_name
        self.modified = True

    def _parse_obj(self, obj):
        self.xmin = self.x = int(obj.find("bndbox/xmin").text)
        self.ymin = self.y = int(obj.find("bndbox/ymin").text)
        self.xmax = int(obj.find("bndbox/xmax").text)
        self.ymax = int(obj.find("bndbox/ymax").text)
        self.width = self.w = self.xmax - self.xmin
        self.height = self.h = self.ymax - self.ymin

    def _crop(self, orig_img):
        self.image = orig_img[self.ymin : self.ymax, self.xmin : self.xmax].copy()
        self.image_path = (
            self.file_path.parents[1] / "img" / (self.file_path.stem + ".jpeg")
        )

    def remove(self)-> None:
        self.modified = True
        self.tree.getroot().remove(self._obj)

    def mark_toggle(self) -> bool:
        "return current mark state"
        self.mark = not self.mark
        return self.mark


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
        label_f_path = QLabel("XML Path:")
        label_f_path_field = QLabel(str(self.defect.file_path))
        label_f_path_field.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label_i_path = QLabel("Image Path:")
        label_i_path_field = QLabel(str(self.defect.image_path))
        label_i_path_field.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label_coordinate = QLabel("Coordinate:")
        label_coordinate_field = QLabel(
            f"({self.defect.xmin}, {self.defect.ymin}) ({self.defect.xmax}, {self.defect.ymax})"
        )
        label_width = QLabel("Width:")
        label_width_field = QLabel(f"{self.defect.width}")
        label_height = QLabel(f"Height:")
        label_height_field = QLabel(f"{self.defect.height}")
        label_map = QLabel()
        label_map.setAlignment(Qt.AlignCenter)
        label_map.setPixmap(self._minimap())

        layout.addWidget(label_name, 0, 0)
        layout.addWidget(label_name_field, 0, 1)
        layout.addWidget(label_f_path, 1, 0)
        layout.addWidget(label_f_path_field, 1, 1)
        layout.addWidget(label_i_path, 2, 0)
        layout.addWidget(label_i_path_field, 2, 1)
        layout.addWidget(label_coordinate, 3, 0)
        layout.addWidget(label_coordinate_field, 3, 1)
        layout.addWidget(label_width, 4, 0)
        layout.addWidget(label_width_field, 4, 1)
        layout.addWidget(label_height, 5, 0)
        layout.addWidget(label_height_field, 5, 1)
        layout.addWidget(label_map, 6, 0, 1, 2)

    def _minimap(self) -> QPixmap:
        thick = 3
        color = (0, 190, 246)
        line_length = 50
        np_origin = cv2.imread(str(self.defect.image_path))
        x, x_t = self.defect.xmax, self.defect.xmax + line_length
        y, y_t = self.defect.ymin, self.defect.ymin - 50
        # cv2.line(np_origin, (x, y), (x_t, y_t), color, 3)
        cv2.circle(np_origin, (x, y), 25, color, thick)

        # d_img = self.defect.image
        # d_w, d_h = d_img.shape[:2]
        # r_w = 100
        # r_h = int(r_w * d_w / d_h)
        # detail_img = cv2.resize(d_img, (r_w, r_h))
        # tooltip = cv2.copyMakeBorder(
        #     detail_img,
        #     thick,
        #     thick,
        #     thick,
        #     thick,
        #     cv2.BORDER_CONSTANT | cv2.BORDER_ISOLATED,
        #     value=color,
        # )
        # np_origin[
        #     y_t : y_t + tooltip.shape[0],
        #     x_t : x_t + tooltip.shape[1],
        # ] = tooltip
        # return numpy2pixmap(img).scaledToWidth(self.width(), Qt.SmoothTransformation)
        return numpy2pixmap(np_origin).scaledToWidth(
            self.width(), Qt.SmoothTransformation
        )


class DefectNodeItem(QGraphicsPixmapItem):
    def __init__(self, node: Defect):
        super().__init__()
        self.defect: Defect = node
        self.setPixmap(
            numpy2pixmap(node.image).scaledToWidth(60, Qt.SmoothTransformation)
        )
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def mouseDoubleClickEvent(self, _) -> None:
        self.defect_edit = DefectEdit(self.defect)
        self.defect_edit.show()

    def mark_toggle(self) -> bool:
        return self.defect.mark_toggle()

    def rename(self, name):
        self.defect.name = name


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
    return [Defect(f_name, tree, obj, img) for obj in root.iter("object")]


def defect_to_xml(d_list: List[Defect]) -> int:
    modified_list = [d for d in d_list if d.modified]
    for p, g in groupby(modified_list, key=lambda x: x.file_path):
        g_list = list(g)
        tree = g_list[0].tree
        tree.write(str(p), encoding="utf-8", xml_declaration=True)
        for d in g_list:
            d.modified = False
    return len(modified_list)
