from datetime import datetime
from pathlib import Path

import cv2
import numpy as np


class Canvas:

    def __init__(self, width, height):
        self.image = np.zeros((height, width, 3), dtype=np.uint8)

    def line(self, p1, p2, color, thickness):
        cv2.line(self.image, p1, p2, color, thickness)

    def erase(self, p1, p2, thickness):
        cv2.line(self.image, p1, p2, (0, 0, 0), thickness)

    def clear(self):
        self.image[:] = 0

    def overlay(self, frame):

        painted = self.image.any(axis=2)
        frame[painted] = self.image[painted]
        return frame

    def save(self, folder):

        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        out = np.full_like(self.image, 255)
        painted = self.image.any(axis=2)
        out[painted] = self.image[painted]
        path = folder / f"drawing_{datetime.now():%Y%m%d_%H%M%S}.png"
        cv2.imwrite(str(path), out)
        return path