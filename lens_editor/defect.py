from curses import update_lines_cols
import imghdr
from lib2to3.pgen2.token import LESS, LESSEQUAL
from multiprocessing import Event
from numbers import Complex
from operator import itemgetter
from platform import release
from webbrowser import get
import xml.etree.ElementTree as ET
from PySide6.QtCore import Qt,QPoint,QRect,QPointF
from PySide6.QtGui import QCursor,QPainter
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import (
    QGraphicsItemGroup,
    QGraphicsPixmapItem,
    QGraphicsLayoutItem,
    QGridLayout,
    QLabel,
    QToolTip,
    QWidget,
    QGraphicsItem,
    QGraphicsSimpleTextItem,
    QGraphicsScene,
    QGraphicsView,
    QPushButton,
    QMessageBox
)
from PySide6.QtGui import QPixmap, QImage, QBrush, QColor,QPen
import cv2
import lens_editor.pixmap as np
from pathlib import Path
from typing import List
from .minimap import Minimap,numpy2pixmap

class Lens:
    def __init__(self, xml_path: Path, img_path: Path):
        self.xml_path = xml_path
        self.img_path = img_path
        self.defects = self.load_defects()
        self.modified = False
        self.leftandright()

    def load_defects(self):
        self.tree = ET.parse(str(self.xml_path))
        self.img = cv2.imread(str(self.img_path))
        root = self.tree.getroot()
        return [Defect(self, obj) for obj in root.iter("object")]

    def set_modified(self, state: bool):
        self.modified = state

    def leftandright(self):
        self.left = [d for d in self.defects if d.x < 1200]
        self.right = [d for d in self.defects if d.x >= 1200]

    def save(self):
        if self.modified:
            self.tree.write(str(self.xml_path))
            self.modified = False


class Defect:
    def __init__(self, lens: Lens, obj: ET.Element):
        self.lens = lens
        self._obj = obj
        self._parse_obj(obj)
        self._crop(lens.img)
        self.mark = False

    def __repr__(self) -> str:
        return f"{self.name}: {self.xmin}, {self.ymin}, {self.xmax}, {self.ymax}"

    @property
    def name(self):
        pass

    @name.getter
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        name = self._obj.find("name")
        name.text = new_name
        self.lens.set_modified(True)
        self._name = new_name

    def _parse_obj(self, obj):
        self._name = obj.find("name").text
        self.xmin = self.x = int(obj.find("bndbox/xmin").text)
        self.ymin = self.y = int(obj.find("bndbox/ymin").text)
        self.xmax = int(obj.find("bndbox/xmax").text)
        self.ymax = int(obj.find("bndbox/ymax").text)
        self.width = self.w = self.xmax - self.xmin
        self.height = self.h = self.ymax - self.ymin
    def _crop(self, orig_img):
        self.image = orig_img[self.ymin : self.ymax, self.xmin : self.xmax].copy()

    def remove(self):
        self.lens.set_modified(True)
        self.lens.tree.getroot().remove(self._obj)

    def mark_toggle(self) -> bool:
        "return current mark state"
        self.mark = not self.mark
        return self.mark




class DefectEdit(QWidget,Lens,Defect):
    def __init__(self, defect,parent=None) -> None:
        super().__init__(parent)
        self.defect = defect
        self.defects = Lens.load_defects
        layout = QGridLayout()
        self.setLayout(layout)
        self.test_button = QPushButton('EDIT', self)                     
        self.test_button.clicked.connect(self.edit)
        label_name = QLabel("Name:")
        label_name_field = QLabel(self.defect.name)
        label_f_path = QLabel("XML Path:")
        label_f_path_field = QLabel(str(self.defect.lens.xml_path))
        label_f_path_field.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label_i_path = QLabel("Image Path:")
        label_i_path_field = QLabel(str(self.defect.lens.img_path))
        label_i_path_field.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label_coordinate = QLabel("Coordinate:")
        label_coordinate_field = QLabel(
            f"({self.defect.xmin}, {self.defect.ymin}) ({self.defect.xmax}, {self.defect.ymax})"
        )
        label_width = QLabel("Width:")
        label_width_field = QLabel(f"{self.defect.width}")
        label_height = QLabel(f"Height:")
        label_height_field = QLabel(f"{self.defect.height}")
        self.label_map = QLabel()
        self.label_map.setAlignment(Qt.AlignCenter)
        self.label_map.setPixmap(self._minimap())

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
        layout.addWidget(self.test_button,6, 1)
        layout.addWidget(self.label_map, 7, 0, 1, 2) 
   
        
    def _minimap(self) -> QPixmap:
        minimap = Minimap(self.defect,self.defects,self.width())
        return minimap.draw(self.defect,self.defects) 
    #     thick = 3
    #     color = (0, 190, 246)
    #     line_length = 50
    #     # np_origin = cv2.imread(str(self.defect.lens.image_path))
    #     np_origin = self.defect.lens.img.copy()
    #     x, x_t = self.defect.xmax, self.defect.xmax + line_length
    #     y, y_t = self.defect.ymin, self.defect.ymin - 50
    #     # cv2.line(np_origin, (x, y), (x_t, y_t), color, 3)
    #     cv2.circle(np_origin, (x, y), 25, color, thick)

    #     d_img = self.defect.image
    #     d_w, d_h = d_img.shape[:2]
    #     r_w = 100
    #     r_h = int(r_w * d_w / d_h)
    #     detail_img = cv2.resize(d_img, (r_w, r_h))
    #     tooltip = cv2.copyMakeBorder(
    #         detail_img,
    #         thick,
    #         thick,
    #         thick,
    #         thick,
    #         cv2.BORDER_CONSTANT | cv2.BORDER_ISOLATED,
    #         value=color,
    #     )
    #     np_origin[
    #         y_t : y_t + tooltip.shape[0],
    #         x_t : x_t + tooltip.shape[1],
    #     ] = tooltip
    #     # return numpy2pixmap(np_origin).scaledToWidth(self.width(), Qt.SmoothTransformation)
    #     return numpy2pixmap(np_origin).scaledToWidth(
    #         self.width(), Qt.SmoothTransformation
        # )                             
    def edit(self):
        self.Ss = complex(self.defect)
        self.Ss.show()

class complex(QGraphicsView):
    def __init__(self,defect,parent=None):
        super(complex, self).__init__(parent)
        self.scene1 = QGraphicsScene()
        self.item = QGraphicsPixmapItem()
        self.defect = defect
        self.resize(1300,1400)
        self.singleOffset = QPoint(0,0)
        self.isLeftPressed = bool(False)                                       # 图片被点住(鼠标左键)标志位
        self.isImgLabelArea = bool(True)
        self.edit1()
    def edit1(self):
        self.rectitemsize_y = self.defect.xmax-self.defect.xmin
        self.rectitemsize_x = self.defect.ymax-self.defect.ymin
        self.xxx = 1
        self.rect_key_y = 0
        self.rect_key_x = 0
        self.rect_key = QPoint(0,0)
        d_img = self.defect.image
        d_w, d_h = d_img.shape[:2]
        r_w = 100
        r_h = int(r_w * d_w / d_h)
        self.pixmap1 = numpy2pixmap(self.defect.lens.img.copy()) #,(r_w*15,r_h*15
        self.item.setPixmap(self.pixmap1)
        self.scene1.addItem(self.item)
        self.setScene(self.scene1)
        self.fitInView(self.defect.xmax-50,self.defect.ymin-50,200,200)
        self.rect_item = QtWidgets.QGraphicsRectItem()
        self.rect_item.setRect(self.defect.xmin+self.rect_key_x,self.defect.ymin+self.rect_key_y,self.defect.xmax-self.defect.xmin,self.defect.ymax-self.defect.ymin)
        self.rect_item.setFlag(QGraphicsItem.ItemIsFocusable, False)
        self.scene1.addItem(self.rect_item) 
        
    def wheelEvent(self, event):
       if (event.angleDelta().y() > 0):
            self.scale(1.5, 1.5)
       elif (event.angleDelta().y() < 0):
            self.scale(1 / 1.5, 1 / 1.5)
                                                
    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_S:                   #=s时，保存矩形坐标至xml
            return self.keyPressEvent2(QKeyEvent)
        if QKeyEvent.key() == Qt.Key_Up : 
            self.rect_item.moveBy(0,-5)
            self.rect_key_y += -5
            self.rect_key+= QPoint(0,-5)

        if QKeyEvent.key()== Qt.Key_Down:
            self.rect_item.moveBy(0,5)
            self.rect_key+= QPoint(0,5)
            self.rect_key_y += 5

        if QKeyEvent.key()== Qt.Key_Left:
            self.rect_item.moveBy(-5,0)
            self.rect_key+= QPoint(-5,0)
            self.rect_key_x += -5

        if QKeyEvent.key()== Qt.Key_Right:
            self.rect_item.moveBy(5,0)
            self.rect_key+= QPoint(5,0)
            self.rect_key_x += 5

    def keyPressEvent2(self, QKeyEvent):
        # self.left=self.mapToScene(self.mapFromParent(QCursor.pos())).x()
        # self.right=self.mapToScene(self.mapFromParent(QCursor.pos())).y()    #  坐标点
        # print(self.defect.xmin+self.rect_key_x)
        # print(self.defect.xmin+self.rectitemsize_x)
        # print(self.defect.ymin+self.rect_key_y)
        # print(self.defect.ymin+self.rectitemsize_y)
        
        xmin = self.defect._obj.find("bndbox/xmin")
        xmin.text =f'{self.defect.xmin+self.rect_key_x}'

        xmax = self.defect._obj.find("bndbox/xmax")
        xmax.text = f'{self.defect.xmin+self.rectitemsize_x}'

        ymin = self.defect._obj.find("bndbox/ymin")
        ymin.text = f'{self.defect.ymin+self.rect_key_y}'

        ymax = self.defect._obj.find("bndbox/ymax")
        ymax.text = f'{self.defect.ymin+self.rectitemsize_y}'

        self.defect.lens.tree.write(str(self.defect.lens.xml_path))
        print("Successful")

        
        

    def mouseMoveEvent(self,event):
        if event.modifiers()==Qt.ControlModifier:
            return self.mouseMoveEvent2(event)

        if self.isLeftPressed:   
            self.label_x1 = QCursor.pos().x()
            self.label_y1 = QCursor.pos().y()
            self.new_label_x = self.label_x1 -self.label_x
            self.new_label_y = self.label_y1 -self.label_y
            self.label_x = self.label_x1
            self.label_y = self.label_y1
            self.singe = QPoint(self.new_label_x,self.new_label_y)
            self.singleOffset = self.singe +self.singleOffset
            self.item.setPos(self.singleOffset)
            self.rect_item.setPos(self.singleOffset+self.rect_key)
    def mouseMoveEvent2(self, event):
        self.rect_x1 = QCursor.pos().x()
        self.rect_y1 = QCursor.pos().y()
        self.new_rect_x1 = self.rect_x1-self.label_x            #计算出的新偏移量x
        self.new_rect_y1 = self.rect_y1-self.label_y                 #计算出的新偏移量y    
        self.rectitemsize_x= self.new_rect_x1
        self.rectitemsize_y= self.new_rect_y1
        self.rect_item.setRect(self.defect.xmin,self.defect.ymin,self.rectitemsize_x,self.rectitemsize_y)
        self.rect_item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        

                  
    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:                            # 左键按下
            self.isLeftPressed = True;                                         # 左键按下(图片被点住),置Ture
            self.label_x=QCursor.pos().x()         #跟踪鼠标，这俩都是
            self.label_y=QCursor.pos().y()     
            self.left=self.mapToScene(self.mapFromParent(QCursor.pos())).x()
            self.right=self.mapToScene(self.mapFromParent(QCursor.pos())).y()                          
        elif event.buttons () == QtCore.Qt.RightButton:                        # 右键按下
            pass
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:  
            pass                      
        elif event.button() == Qt.RightButton:                                                                   
            pass


class DefectLayoutItem(QGraphicsLayoutItem):
    def __init__(self, group, parent=None) -> None:
        super().__init__(parent)
        self.group = group
        self.setGraphicsItem(self.group)

    def sizeHint(self, which, const):
        return self.group.boundingRect().size()

    def setGeometry(self, rect):
        return self.group.setPos(rect.topLeft())


class DefectItem(QGraphicsItemGroup):
    def __init__(self, defect: Defect, msg="", parent=None) -> None:
        super().__init__(parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.defect: Defect = defect
        self.label = QGraphicsSimpleTextItem(defect.name)
        self.img = QGraphicsPixmapItem()
        self.img.setPixmap(
            numpy2pixmap(defect.image).scaledToWidth(50, Qt.SmoothTransformation)
        )
        self.addToGroup(self.label)
        self.label.setY(-13)
        self.label.setX(12)
        self.addToGroup(self.img)
        self._rect = self.childrenBoundingRect()
        self._label_color = QColor("black")
        self.msg = msg

    def paint(self, painter, option, widget=None):
        painter.drawRect(self._rect)

    def boundingRect(self):
        return self._rect

    def get_layout_item(self) -> DefectLayoutItem:
        return DefectLayoutItem(self)

    def mousePressEvent(self, event) -> None:
        tooltip = f"""{self.msg}
x: {self.defect.xmin}
y: {self.defect.ymin}
h: {self.defect.height}
w: {self.defect.width}"""
        if event.button() == Qt.RightButton:
            QToolTip.showText(event.screenPos(), tooltip)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.defect_edit = DefectEdit(self.defect)
            DefectEdit(self.defect)
            self.defect_edit.show()

    def mark_toggle(self) -> bool:
        if state := self.defect.mark_toggle():
            self.label.setBrush(QBrush(QColor("green")))
        else:
            self.label.setBrush(self._label_color)
        return state

    def rename(self, name):
        self.defect.name = name
        self.label.setText(name)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            if value:
                self.label.setBrush(QBrush(QColor("green")))
            else:
                self.label.setBrush(QBrush(QColor("black")))
        return super().itemChange(change, value)