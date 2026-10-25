import time

import cv2
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
vision = mp.tasks.vision

# Pairs of landmark ids joined by a line when drawing the hand skeleton.
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),          # index
    (5, 9), (9, 10), (10, 11), (11, 12),     # middle
    (9, 13), (13, 14), (14, 15), (15, 16),   # ring
    (13, 17), (17, 18), (18, 19), (19, 20),  # pinky
    (0, 17),                                 # base of the palm
]


class HandTracker:


    def __init__(self, model_path, max_hands=1, detection_conf=0.7, tracking_conf=0.5):
        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_conf,
            min_hand_presence_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._last_ts = -1

    def find_hand(self, frame_bgr):

        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)   # MediaPipe expects RGB
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        # VIDEO mode needs a timestamp (ms) that always goes up.
        ts = max(int(time.monotonic() * 1000), self._last_ts + 1)
        self._last_ts = ts
        result = self._landmarker.detect_for_video(image, ts)
        if not result.hand_landmarks:
            return None
        h, w = frame_bgr.shape[:2]
        return [(int(lm.x * w), int(lm.y * h)) for lm in result.hand_landmarks[0]]

    @staticmethod
    def draw(frame, points):

        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, points[a], points[b], (255, 255, 255), 2)
        for point in points:
            cv2.circle(frame, point, 4, (0, 0, 255), cv2.FILLED)

    def close(self):
        self._landmarker.close()