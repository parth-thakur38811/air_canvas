from enum import Enum

# Landmark ids from MediaPipe's 21-point hand model.
FINGER_TIPS = (8, 12, 16, 20)   # index, middle, ring, pinky
FINGER_PIPS = (6, 10, 14, 18)   # the middle knuckle of each of those fingers


class Mode(Enum):
    IDLE = "Idle"
    DRAW = "Draw"
    SELECT = "Select"
    ERASE = "Erase"


def fingers_up(points):

    return [points[tip][1] < points[pip][1] for tip, pip in zip(FINGER_TIPS, FINGER_PIPS)]


def detect_mode(fingers):
    index, middle, ring, pinky = fingers
    if index and middle and ring and pinky:
        return Mode.ERASE
    if index and middle and not ring and not pinky:
        return Mode.SELECT
    if index and not middle and not ring and not pinky:
        return Mode.DRAW
    return Mode.IDLE


class ModeFilter:


    def __init__(self, stable_frames=3):
        self.stable_frames = stable_frames
        self.current = Mode.IDLE
        self._candidate = Mode.IDLE
        self._count = 0

    def update(self, mode):
        if mode == self._candidate:
            self._count += 1
        else:
            self._candidate, self._count = mode, 1
        if mode != self.current:
            self.current = mode if self._count >= self.stable_frames else Mode.IDLE
        return self.current