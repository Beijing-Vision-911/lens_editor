from PySide6.QtWidgets import QGraphicsView
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt


class View(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing, False)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setRubberBandSelectionMode(Qt.IntersectsItemBoundingRect)
        # gl = QOpenGLWidget()
        # format = QSurfaceFormat()
        # format.setSamples(1)
        # gl.setFormat(format)
        # self.setViewport(gl)
