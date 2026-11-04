import pyautogui

# Deactivating the failsafe for free mouse use
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

class MouseController:
    def __init__(self, keyboard = None):
        self.keyboard = keyboard

        self.EAR_THRESHOLD = 0.40 # Adjustable threshold for blink
        self.EAR_TOLERANCE = 0.02 # Since there are small changes to EAR each frame
        self.CONSECUTIVE_FRAMES_CLICK = 4 # Frames to "click"
        self.CONSECUTIVE_FRAMES_HOLD = 13 # Frames to "hold"

        # Condition flags
        self.closed_time_l = 0
        self.closed_time_r = 0
        self.holding_click = False
        self.right_triggered = False

        # Estimated values to be adjusted
        self.x_min, self.x_neutral, self.x_max = 0.40, 0.50, 0.65
        self.y_min, self.y_neutral, self.y_max = 0.35, 0.46, 0.50

        # Dead zone values
        self.x_dead_zone = 0.25
        self.y_dead_zone = 0.25

        # Mouse speed values
        self.max_speed = 30

    # Min-Max normalization function
    def normalize(self, value, min_value, max_value):
        if max_value <= min_value:
            return 0.5
        normalized = (value - min_value) / (max_value - min_value)
        return max(0.0, min(1.0, normalized))

    # Calculates speed based on how distant the eyes are from the center
    def calculate_speed(self, delta, dead_zone):
        distance = abs(delta)

        if distance <= dead_zone:
            return 0

        # Removes the dead zone from the effective distance
        effective_distance = distance - dead_zone

        # Normalizes the remaining distance
        intensity = effective_distance / (0.5 - dead_zone)

        # Limits the intensity
        intensity = max(0.0, min(1.0, intensity))

        # Calculates proportional speed
        speed = intensity * self.max_speed

        return speed if delta > 0 else -speed

    def process_commands(self, left_eye, right_eye, gaze_x, gaze_y):
        # Checking for a one eye blink
        left_closed = right_eye > left_eye - self.EAR_TOLERANCE < self.EAR_THRESHOLD or right_eye > left_eye + self.EAR_TOLERANCE< self.EAR_THRESHOLD
        right_closed = left_eye > right_eye - self.EAR_TOLERANCE < self.EAR_THRESHOLD or left_eye > right_eye + self.EAR_TOLERANCE < self.EAR_THRESHOLD

        # Click and Hold Logic
        if left_closed:
            self.closed_time_l += 1

            # If eye is closed for sufficient time, hold
            if self.closed_time_l >= self.CONSECUTIVE_FRAMES_HOLD and not self.holding_click:
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
            elif self.CONSECUTIVE_FRAMES_CLICK <= self.closed_time_l:
                # If it wasn't closed for long enough to hold but enough to click, does so
                pyautogui.click(button="left")
                print("Left click")
            # Resets closed time
            self.closed_time_l = 0

        # Opens virtual keyboard
        if right_closed:
            self.closed_time_r += 1
            # Checks if it is not already open and blink was intentional
            if self.closed_time_r >= self.CONSECUTIVE_FRAMES_CLICK and not self.right_triggered:
                if self.keyboard is not None:
                    # Opens Python virtual keyboard
                    self.keyboard.toggle()
                print("Virtual keyboard toggled")
                self.right_triggered = True
        else:
            # Resets time and closes
            self.closed_time_r = 0
            self.right_triggered = False

        # Mouse movement logic
        if gaze_x is not None and gaze_y is not None and not right_closed and not left_closed:
            # Normalizes both values
            x_norm = self.normalize(gaze_x, self.x_min, self.x_max)
            y_norm = self.normalize(gaze_y, self.y_min, self.y_max)

            # Calculating displacement, inverting X
            delta_x = self.x_neutral - x_norm
            delta_y = y_norm - self.y_neutral

            # Implementing dead zones
            if abs(delta_x) < self.x_dead_zone:
                delta_x = 0
            if abs(delta_y) < self.y_dead_zone:
                delta_y = 0

            # Verifying changes and moving the mouse
            move_x = self.calculate_speed(delta_x, self.x_dead_zone)
            move_y = self.calculate_speed(delta_y, self.y_dead_zone)

            if move_x != 0 or move_y != 0:
                pyautogui.move(round(move_x), round(move_y))