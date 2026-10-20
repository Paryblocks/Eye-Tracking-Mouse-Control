import pyautogui

# Deactivating the failsafe for free mouse use
pyautogui.FAILSAFE = False

class MouseController:
    def __init__(self):
        self.EAR_THRESHOLD = 0.39 # Adjustable threshold for blink
        self.CONSECUTIVE_FRAMES_CLICK = 3 # Frames to "click"
        self.CONSECUTIVE_FRAMES_HOLD = 10 # Frames to "hold"

        # Condition flags
        self.closed_time = 0
        self.holding_click = False

        # Getting screen size
        self.screen_width, self.screen_height = pyautogui.size()

        # Filter for smoother movement
        self.smoother = 5
        self.history_x = []
        self.history_y = []

    def process_commands(self, left_eye, right_eye, points):
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


            # Applying the filter for smoother mouse movement
            self.history_x.append(x_screen)
            self.history_y.append(y_screen)
            if len(self.history_x) > self.smoother:
                self.history_x.pop(0)
                self.history_y.pop(0)

            x_smooth = sum(self.history_x) / len(self.history_x)
            y_smooth = sum(self.history_y) / len(self.history_y)

            # Moves the cursor
            pyautogui.moveTo(x_smooth, y_smooth)