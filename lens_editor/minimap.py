# from ast import main
# from os import scandir
# from pyexpat.model import XML_CTYPE_CHOICE
# from telnetlib import SB
# # from turtle import back
# from typing_extensions import Self
# from webbrowser import BackgroundBrowser
# from xml.etree.ElementPath import xpath_tokenizer
from os import get_blocking
from socket import SO_BINDTODEVICE
import cv2
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QBrush, QColor
# from enum import Enum
# from typing import Tuple
import numpy as np

# from lens_editor.rule_edit import RuleEditWindow
# class Orientation(Enum):
#     UP = 0
#     DOWN = 1
#     LEFT = 2
#     RIGHT = 3


# class Minimap:
#     def __init__(self, defect: Defect):
#         self.defect = defect
#         self.image = cv2.imread(str(defect.image_path))
#         self.margin = 50

#     def get_orientation(self) -> Tuple[Orientation, Orientation]:
        
#         if self.defect.xmin > 1200:
#             h = Orientation.LEFT
#         else:
#             h = Orientation.RIGHT

#         if self.defect.ymin > 1200:
#             v = Orientation.UP
#         else:
#             v = Orientation.DOWN
#         return (h, v)

#     def draw(self):
#         h, v = self.get_orientation()
#         if h == Orientation.LEFT:
#             x = self.defect.xmin - self.margin - self.defect.width
#         else:
#             x = self.defect.xmin + self.margin

#         if v == Orientation.UP:
#             y = self.defect.ymin - self.margin - self.defect.height
#         else:
#             y = self.defect.ymin + self.margin

"""
minimap = Minimap(defect)
pixmap = minimap.get_pixmap()
"""

def numpy2pixmap(np_img) -> QPixmap:
    height, width, channel = np_img.shape
    qimg = QImage(
        np_img.data, width, height, width * channel, QImage.Format_RGB888
    ).rgbSwapped()
    return QPixmap(qimg)
    
class Minimap():
    def __init__(self,defect,defects,width,show_all=False):
        self.defect = defect
        self.defects = defects
        self.width = width
        self.background :np.adarry = self.defect.lens.img.copy()
        if not show_all:
            self.draw(self.defect,self.defects)  
            return 
        self.draw_all(self.defects)

    def draw_all(self,defects):
        self.defects = defects
        for d in self.defects:
            self.draw(d)

    def draw(self,defect,defects):
        self.defects = defects
        self.defect = defect
        thick = 3
        color = (0, 190, 246)
        d_img = self.defect.image
        d_w, d_h = d_img.shape[:2]
        r_w = 100
        r_h = int(r_w * d_w / d_h)
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
        x_t =self.defect.xmax + 50
        y_t = self.defect.ymin - 50
        x = self.defect.xmax
        y = self.defect.ymin   
        # for d in self.defect:
        cv2.circle(self.background,(defect.xmin, defect.ymin),20, (255,0,255))   #x,y用来画圈，x_t,y_t,用来画缩略图
        cv2.circle(self.background, (x, y), 25, 255,0,0, 3) 
        if x_t >=1200 and y_t<=1200:
            x_t = self.defect.xmax  -150
            y_t = self.defect.ymin +40
            self.background[
                y_t : y_t + tooltip.shape[0],
                x_t : x_t + tooltip.shape[1],
            ] = tooltip
        elif x_t<1200 and y_t<1200:
            x_t = self.defect.xmax  +50
            y_t = self.defect.ymin +20
            self.background[
                y_t : y_t + tooltip.shape[0],
                x_t : x_t + tooltip.shape[1],
            ] = tooltip
        elif x_t<1200 and y_t>1200:
            x_t = self.defect.xmax  +10
            y_t = self.defect.ymin  -10-r_h
            self.background[
                y_t : y_t + tooltip.shape[0],
                x_t : x_t + tooltip.shape[1],
            ] = tooltip
        elif x_t>=1200 and y_t>=1200:
            x_t = self.defect.xmax -(2*r_w)
            y_t = self.defect.ymin -r_h-30
            self.background[
                y_t : y_t + tooltip.shape[0],
                x_t : x_t + tooltip.shape[1],
            ] = tooltip
            
        return numpy2pixmap(self.background).scaledToWidth(self.width, Qt.SmoothTransformation)
          

        #         cv2.circle(self.background,(defect.xmin, defect.ymin),20, (255,0,255)) 
        #         cv2.circle(self.background, (x, y), 25, 255,0,0, 3)
        #         return self.get_pixmap()



    def get_pixmap(self) -> QPixmap:
        return numpy2pixmap(self.background).scaledToWidth(self.width, Qt.SmoothTransformation)
    
   

            
            
            


        