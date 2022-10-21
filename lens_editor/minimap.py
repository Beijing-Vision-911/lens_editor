import cv2
from enum import Enum
from .xml_parser import Defect
from typing import Tuple


class Orientation(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class Minimap:
    def __init__(self, defect: Defect):
        self.defect = defect
        self.image = cv2.imread(str(defect.image_path))
        self.margin = 50

    def get_orientation(self) -> Tuple[Orientation, Orientation]:
        
        if self.defect.xmin > 1200:
            h = Orientation.LEFT
        else:
            h = Orientation.RIGHT

        if self.defect.ymin > 1200:
            v = Orientation.UP
        else:
            v = Orientation.DOWN
        return (h, v)

    def draw(self):
        h, v = self.get_orientation()
        if h == Orientation.LEFT:
            x = self.defect.xmin - self.margin - self.defect.width
        else:
            x = self.defect.xmin + self.margin

        if v == Orientation.UP:
            y = self.defect.ymin - self.margin - self.defect.height
        else:
            y = self.defect.ymin + self.margin