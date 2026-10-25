from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Camera
CAMERA_INDEX = 0            # 0 = built-in webcam; try 1 for a USB camera
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Hand tracking
MODEL_PATH = BASE_DIR / "assets" / "models" / "hand_landmarker.task"
MAX_HANDS = 1
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.5
MODE_STABLE_FRAMES = 3      # a gesture must hold this many frames before the mode switches

# Drawing (OpenCV colours are BGR)
PALETTE = [
    ("Blue", (255, 128, 0)),
    ("Green", (0, 200, 0)),
    ("Red", (0, 0, 255)),
    ("Yellow", (0, 255, 255)),
]
BRUSH_THICKNESS = 8
ERASER_THICKNESS = 60
SMOOTHING = 0.5             # 0 = raw fingertip; closer to 1 = smoother 

# Toolbar
TOOLBAR_HEIGHT = 100
ACTION_COOLDOWN_S = 1.0     # stops Clear / Save firing on every frame

# Output
OUTPUT_DIR = BASE_DIR / "output"