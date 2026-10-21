import pyautogui

# Deactivating the failsafe for free mouse use
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

class MouseController:
    def __init__(self):
        self.EAR_THRESHOLD = 0.5 # Adjustable threshold for blink
        self.CONSECUTIVE_FRAMES_CLICK = 4 # Frames to "click"
        self.CONSECUTIVE_FRAMES_HOLD = 10 #0Frames to "hold"

        # Condition flags
        self.closed_time = 0
        self.holding_click = False

        # Getting screen size
        self.screen_width, self.screen_height = pyautogui.size()

        # Estimated min-max values to be adjusted
        self.x_min, self.x_max = 0.40, 0.65
        self.y_min, self.y_max = 0.34, 0.49

        # Filter to avoid jitter
        self.prev_screen_x, self.prev_screen_y = self.screen_width // 2, self.screen_height // 2
        self.smoothing = 0.25

    # Min-Max normalization function
    def normalize(self, value, min_value, max_value):
        if max_value <= min_value:
            return 0.5
        normalized = (value - min_value) / (max_value - min_value)
        return max(0.0, min(1.0, normalized))

    def process_commands(self, left_eye, right_eye, points, gaze_x, gaze_y):
        # Click and Hold Logic
        if left_eye < self.EAR_THRESHOLD:
            self.closed_time += 1

            # If eye is closed for sufficient time, hold
            if self.closed_time >= self.CONSECUTIVE_FRAMES_HOLD and not self.holding_click:
                pyautogui.mouseDown(button="left")
                self.holding_click = True
                print("Holding left click")
        else:
            # When eye opens, check what happened
            if self.holding_click:
                # If it was holding click, release it
                pyautogui.mouseUp(button="left")
                self.holding_click = False
                print("Releasing left click")
            elif self.CONSECUTIVE_FRAMES_CLICK <= self.closed_time < self.CONSECUTIVE_FRAMES_HOLD:
                # If it wasn't closed for long enough to hold but enough to click, does so
                pyautogui.click(button="left")
                print("Left click")
            # Resets closed time
            self.closed_time = 0

        # Mouse movement logic
        if gaze_x is not None and gaze_y is not None:
            # Normalizes both values
            x_norm = self.normalize(gaze_x, self.x_min, self.x_max)
            y_norm = self.normalize(gaze_y, self.y_min, self.y_max)

            x_norm = 1.0 - x_norm

            # Maps the screen to the values
            screen_x = x_norm * (self.screen_width - 1)
            screen_y = y_norm * (self.screen_height - 1)

            # Smoothing to reduce jitter
            smooth_x = self.prev_screen_x + (screen_x - self.prev_screen_x) * self.smoothing
            smooth_y = self.prev_screen_y + (screen_y - self.prev_screen_y) * self.smoothing

            # Moves the cursor
            pyautogui.moveTo(smooth_x, smooth_y)

            # Saves current position for next cycle
            self.prev_screen_x, self.prev_screen_y = smooth_x, smooth_y