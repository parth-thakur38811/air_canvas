import time

import cv2

import config
from air_canvas.camera import open_camera
from air_canvas.canvas import Canvas
from air_canvas.gestures import Mode, ModeFilter, detect_mode, fingers_up
from air_canvas.hand_tracker import HandTracker
from air_canvas.toolbar import Toolbar

WINDOW = "Air Canvas"
INDEX_TIP = 8
PALM_CENTRE = 9   # middle-finger knuckle: a steady point to erase with


def smooth(prev, new, factor):
    """Blend the new point with the last one to steady a shaky fingertip."""
    if prev is None:
        return new
    return (int(prev[0] * factor + new[0] * (1 - factor)),
            int(prev[1] * factor + new[1] * (1 - factor)))


def main():
    cap = open_camera(config.CAMERA_INDEX, config.FRAME_WIDTH, config.FRAME_HEIGHT)
    ok, frame = cap.read()
    if not ok:
        raise RuntimeError("The camera opened but sent no frame.")
    height, width = frame.shape[:2]   # the size the camera really gives

    tracker = HandTracker(config.MODEL_PATH, config.MAX_HANDS,
                          config.DETECTION_CONFIDENCE, config.TRACKING_CONFIDENCE)
    canvas = Canvas(width, height)
    toolbar = Toolbar(width, config.TOOLBAR_HEIGHT, config.PALETTE)
    mode_filter = ModeFilter(config.MODE_STABLE_FRAMES)

    prev = None          # last pen position; None means the pen is lifted
    last_mode = Mode.IDLE
    last_action = 0.0    # when Clear / Save last fired, for the cooldown

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)   # mirror view: move right, the line goes right

        points = tracker.find_hand(frame)
        mode = mode_filter.update(detect_mode(fingers_up(points)) if points else Mode.IDLE)
        if points is None or mode != last_mode:
            prev = None              # lift the pen when the hand is lost or the mode changes
        last_mode = mode
        cursor = None                # (point, radius) to show where the pen is

        if points and mode == Mode.SELECT:
            tip = points[INDEX_TIP]
            cursor = (tip, 12)
            label = toolbar.hit(tip)
            if label in ("Clear", "Save"):
                if time.monotonic() - last_action > config.ACTION_COOLDOWN_S:
                    last_action = time.monotonic()
                    if label == "Clear":
                        canvas.clear()
                    else:
                        print("Saved", canvas.save(config.OUTPUT_DIR))
            elif label:
                toolbar.selected = label

        elif points and mode == Mode.DRAW:
            point = smooth(prev, points[INDEX_TIP], config.SMOOTHING)
            if point[1] > config.TOOLBAR_HEIGHT:     # never paint over the toolbar
                if prev is not None:
                    if toolbar.selected == "Eraser":
                        canvas.erase(prev, point, config.ERASER_THICKNESS)
                    else:
                        canvas.line(prev, point, toolbar.selected_color(), config.BRUSH_THICKNESS)
                prev = point
            else:
                prev = None
            radius = config.ERASER_THICKNESS // 2 if toolbar.selected == "Eraser" else 6
            cursor = (point, radius)

        elif points and mode == Mode.ERASE:
            point = smooth(prev, points[PALM_CENTRE], config.SMOOTHING)
            if prev is not None:
                canvas.erase(prev, point, config.ERASER_THICKNESS)
            prev = point
            cursor = (point, config.ERASER_THICKNESS // 2)

        frame = canvas.overlay(frame)
        toolbar.draw(frame)
        if points:
            tracker.draw(frame, points)
        if cursor:
            cv2.circle(frame, cursor[0], cursor[1], (255, 255, 255), 2)
        cv2.putText(frame, f"Mode: {mode.value}", (10, height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.imshow(WINDOW, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
            break
        if key == ord("c"):
            canvas.clear()
        if key == ord("s"):
            print("Saved", canvas.save(config.OUTPUT_DIR))

    tracker.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()