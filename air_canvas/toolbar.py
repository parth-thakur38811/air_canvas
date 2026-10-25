from dataclasses import dataclass

import cv2

FONT = cv2.FONT_HERSHEY_SIMPLEX


@dataclass
class Button:
    label: str
    x1: int
    x2: int
    color: tuple | None = None  


class Toolbar:


    def __init__(self, width, height, palette):
        self.height = height
        items = list(palette) + [("Eraser", None), ("Clear", None), ("Save", None)]
        slot = width // len(items)
        self.buttons = [
            Button(label, i * slot + 8, (i + 1) * slot - 8, color)
            for i, (label, color) in enumerate(items)
        ]
        self.selected = palette[0][0]

    def hit(self, point):
        x, y = point
        if y > self.height:
            return None
        for button in self.buttons:
            if button.x1 <= x <= button.x2:
                return button.label
        return None

    def selected_color(self):
        for button in self.buttons:
            if button.label == self.selected:
                return button.color
        return None

    def draw(self, frame):
        cv2.rectangle(frame, (0, 0), (frame.shape[1], self.height), (40, 40, 40), cv2.FILLED)
        for b in self.buttons:
            top_left, bottom_right = (b.x1, 10), (b.x2, self.height - 10)
            cv2.rectangle(frame, top_left, bottom_right, b.color or (90, 90, 90), cv2.FILLED)
            if b.label == self.selected:
                cv2.rectangle(frame, top_left, bottom_right, (255, 255, 255), 4)
            text_color = (0, 0, 0) if b.color else (255, 255, 255)
            (tw, th), _ = cv2.getTextSize(b.label, FONT, 0.7, 2)
            org = ((b.x1 + b.x2 - tw) // 2, (self.height + th) // 2)
            cv2.putText(frame, b.label, org, FONT, 0.7, text_color, 2)