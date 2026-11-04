import tkinter as tk
import pyautogui
import ctypes

# Building a virtual keyboard since windows one doesn't recognize pyautogui clicks
class VirtualKeyboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Virtual Keyboard")
        # Window size, can be adjusted (Width, Height, X, Y)
        self.root.geometry("760x380+100+400")
        self.root.resizable(False, False)

        # Makes so that the window stays on top of other to allow typing
        self.root.attributes("-topmost", True)

        # Flag for activating the keyboard
        self.visible = False

        # Prepares the window
        self.root.update_idletasks()

        # Using user32 to manage the window
        self.user32 = ctypes.windll.user32
        hwnd = self.root.winfo_id()
        hwnd = self.user32.GetParent(hwnd) or hwnd

        # Configures styles and makes so the window doesn't cover others when clicking
        GWL_EXSTYLE = -20 # Extended styles
        WS_EX_NOACTIVATE = 0x08000000 # Clicking does not make it active
        SWP_NOMOVE = 0x0002 # Can't alter position
        SWP_NOSIZE = 0x0001 # Can't resize
        SWP_NOZORDER = 0x0004 # Doesn't alter window order
        SWP_FRAMECHANGED = 0x0020 # Updates window configuration
        SWP_NOACTIVATE = 0x0010 # Doesn't activate the window

        # Gets and apply styles
        style = self.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        self.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE)

        # Apply settings to the window
        self.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED | SWP_NOACTIVATE)

        # Stores previously opened window before the keyboard
        self.target_hwnd = None

        # Gets buttons and hides window
        self.create_keys()
        self.root.withdraw()

    def create_keys(self):
        # Sets keyboard rows
        rows = ["1234567890", "qwertyuiop", "asdfghjkl", "zxcvbnm"]

        for row in rows:
            # Creating rows with 3 px spacing
            frame = tk.Frame(self.root)
            frame.pack(pady=3)

            # Creating the letter buttons
            for char in row:
                # Creates buttons inside the row
                button = tk.Button(
                    frame,
                    # Setting the value to the letter
                    text=char,
                    width=5,
                    height=2,
                    takefocus=0,
                    # Calls function to type the char in the key
                    command=lambda key=char: self.type_key(key)
                )
                # Places buttons with 2 px spacing
                button.pack(side=tk.LEFT, padx=2)

        # Creating space for special keys
        special = tk.Frame(self.root)
        special.pack(pady=5)

        # Spacebar
        tk.Button(
            special, text="Space", width=15, height=2,
            takefocus=0,
            command=lambda: self.press_key("space")
        ).pack(side=tk.LEFT, padx=3)

        # Backspace
        tk.Button(
            special, text="Backspace", width=10, height=2,
            takefocus=0,
            command=lambda: self.press_key("backspace")
        ).pack(side=tk.LEFT, padx=3)

        # Enter
        tk.Button(
            special, text="Enter", width=10, height=2,
            takefocus=0,
            command=lambda: self.press_key("enter")
        ).pack(side=tk.LEFT, padx=3)

        # Close
        tk.Button(
            special, text="Close", width=10, height=2,
            takefocus=0,
            command=self.hide
        ).pack(side=tk.LEFT, padx=3)

    # Toggles on and off window
    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    # Shows the keyboard over the window to type
    def show(self):
        # Gets the last interacted window
        self.target_hwnd = self.user32.GetForegroundWindow()
        self.root.deiconify()
        # Makes the keyboard appear over the other window
        self.root.lift()
        self.visible = True

    # Hides the window
    def hide(self):
        self.root.withdraw()
        self.visible = False

    # Constantly updating the window
    def update(self):
        self.root.update()

    # Closes the window on program ending
    def close(self):
        self.root.destroy()

    # Types the pressed key on the stored window
    def type_key(self, key):
        if self.target_hwnd:
            # Makes the stored window the focus so it can type
            self.user32.SetForegroundWindow(self.target_hwnd)
        # Types the key
        pyautogui.write(key)

    # The same as above but for pressing special buttons (Space, Backspace, etc)
    def press_key(self, key):
        if self.target_hwnd:
            self.user32.SetForegroundWindow(self.target_hwnd)
        pyautogui.press(key)