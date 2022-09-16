import xml.etree.ElementTree as ET
from PySide6.QtWidgets import QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QImage
import cv2
import numpy as np
from pathlib import Path


class Defect:
    def __init__(self, file_path: Path, root, obj):
        self.file_path :Path = file_path
        self._root = root
        self._obj = obj
        self._parse_obj(obj)
        self.image = None

    @property
    def name(self):
        pass

    @name.getter
    def name(self):
        return self._obj.find('name').text

    @name.setter
    def name(self, new_name):
        self._obj.set('name', new_name)


    def _parse_obj(self, obj):
        self.xmin = int(obj.find('bndbox/xmin').text)
        self.ymin = int(obj.find('bndbox/ymin').text)
        self.xmax = int(obj.find('bndbox/xmax').text)
        self.ymax = int(obj.find('bndbox/xmax').text)

    def _crop_image(self):
        img_path = self.file_path.parents[1] / "img" / (self.file_path.stem + ".jpeg")
        if not img_path.exists():
            self.image = None
            return 
        img = cv2.imread(str(img_path))
        self.image = img[self.xmin:self.xmax, self.ymin:self.ymax].copy()
            
        

    def remove(self):
        self._root.remove(self._obj)
        


class DefectItem(QGraphicsPixmapItem):
    "display on UI, when double clicked show details window"
    def __init__(self, node: Defect, parent=None):
        super().__init__(parent)
        self.node = node
        self.setPixmap(self._numpy2pixmap(self.node.image))

    @staticmethod
    def _numpy2pixmap(np_img) -> QPixmap:
        height, width, channel = np_img.shape
        qimg = QImage(np_img.data, width, height, channel*3, QImage.Format_RGB888)
        return QPixmap(qimg)
        
        
        
    



xml_file_path = "/home/peterzky/Downloads/20220809_aug2/UNQ/xml/20220730_UNQ_109.xml"

t = ET.parse(xml_file_path)
r = t.getroot()           
defects = [ Defect(Path(xml_file_path), r, o) for o in r.iter('object')]    

