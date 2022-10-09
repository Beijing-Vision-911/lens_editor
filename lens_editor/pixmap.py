import numpy as np
from PySide6.QtGui import QPixmap, QImage
def numpy2pixmap(np_img):
    np_img = np.ascontiguousarray(np_img)
    bytes_per_line = np_img.shape[1] * 3 if len(np_img.shape) == 3 else np_img.shape[1]
    picture_format = (
        QImage.Format_BGR888 if len(np_img.shape) == 3 else QImage.Format_Grayscale8
    )
    qimg = QImage(
        np_img.data,
        np_img.shape[1],
        np_img.shape[0],
        bytes_per_line,
        picture_format,
    )
    return QPixmap(qimg)