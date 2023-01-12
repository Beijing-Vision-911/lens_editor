from typing import Any,List
import cv2   #type:ignore
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

from lens_editor.defect import Defect


def numpy2pixmap(np_img:np.ndarray) -> QPixmap:
    np_img = np.ascontiguousarray(np_img)
    bytes_per_line:int = np_img.shape[1] * 3 if len(np_img.shape) == 3 else np_img.shape[1]
    picture_format = (
        QImage.Format_BGR888 if len(np_img.shape) == 3 else QImage.Format_Grayscale8
    )
    qimg:QImage = QImage(
        np_img.data,
        np_img.shape[1],
        np_img.shape[0],
        bytes_per_line,
        picture_format,
    )
    return QPixmap(qimg)


class Minimap:
    def __init__(self, defect:Defect, defects:List[Defect], width:int, show_all:bool=False) -> None:
        self.defect = defect
        self.defects = defects
        self.width = width
        self.background: np.ndarray = self.defect.lens.img.copy()
        if not show_all:
            self.draw(self.defect, self.defects)
            return
        self.draw_all(self.defects)
    # 这个功能没有实现
    def draw_all(self, defects) -> None:
        self.defects = defects
        # for d in self.defects:
            # self.draw(d)

    def draw(self, defect, defects) -> QPixmap:
        self.defects = defects
        self.defect = defect
        thick = 3
        color = (0, 190, 246)
        d_img = self.defect.image
        d_w, d_h = d_img.shape[:2]
        r_w = 100
        r_h: int = int(r_w * d_w / d_h)
        detail_img = cv2.resize(d_img, (r_w, r_h))
        tooltip = cv2.copyMakeBorder(
            detail_img,
            thick,
            thick,
            thick,
            thick,
            cv2.BORDER_CONSTANT | cv2.BORDER_ISOLATED,
            value=color,
        )
        x_t: int = self.defect.xmax + 50
        y_t: int = self.defect.ymin - 50
        x: int = self.defect.xmax
        y: int = self.defect.ymin
        cv2.circle(
            self.background, (defect.xmin, defect.ymin), 20, (255, 0, 255)
        )  # x,y用来画圈，x_t,y_t,用来画缩略图
        cv2.circle(self.background, (x, y), 25, 255, 0, 0, 3)
        if x_t >= 1200 and y_t <= 1200:
            x_t = self.defect.xmax - 150
            y_t = self.defect.ymin + 40
            self.background[
                y_t : y_t + tooltip.shape[0],
                x_t : x_t + tooltip.shape[1],
            ] = tooltip
        elif x_t < 1200 and y_t < 1200:
            x_t = self.defect.xmax + 50
            y_t = self.defect.ymin + 20
            self.background[
                y_t : y_t + tooltip.shape[0],
                x_t : x_t + tooltip.shape[1],
            ] = tooltip
        elif x_t < 1200 and y_t > 1200:
            x_t = self.defect.xmax + 10
            y_t = self.defect.ymin - 10 - r_h
            self.background[
                y_t : y_t + tooltip.shape[0],
                x_t : x_t + tooltip.shape[1],
            ] = tooltip
        elif x_t >= 1200 and y_t >= 1200:
            x_t = self.defect.xmax - (2 * r_w)
            y_t = self.defect.ymin - r_h - 30
            self.background[
                y_t : y_t + tooltip.shape[0],
                x_t : x_t + tooltip.shape[1],
            ] = tooltip

        return numpy2pixmap(self.background).scaledToWidth(
            self.width, Qt.SmoothTransformation
        )

    def get_pixmap(self) -> QPixmap:
        return numpy2pixmap(self.background).scaledToWidth(
            self.width, Qt.SmoothTransformation
        )
