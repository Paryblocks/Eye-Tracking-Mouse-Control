import tkinter as tk
import pyautogui
import ctypes

class VirtualKeyboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Teclado Virtual")
        self.root.geometry("760x300+100+500")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.visible = False

        self.root.update_idletasks()

        self.user32 = ctypes.windll.user32

        hwnd = self.root.winfo_id()
        hwnd = self.user32.GetParent(hwnd) or hwnd

        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOZORDER = 0x0004
        SWP_FRAMECHANGED = 0x0020
        SWP_NOACTIVATE = 0x0010

        style = self.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

        self.user32.SetWindowLongW(
            hwnd,
            GWL_EXSTYLE,
            style | WS_EX_NOACTIVATE
        )

        self.user32.SetWindowPos(
            hwnd, 0, 0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER |
            SWP_FRAMECHANGED | SWP_NOACTIVATE
        )

        self.target_hwnd = None

        self.create_keys()
        self.root.withdraw()

    def create_keys(self):
        rows = [
            "1234567890",
            "qwertyuiop",
            "asdfghjkl",
            "zxcvbnm"
        ]

        for row_index, row in enumerate(rows):
            frame = tk.Frame(self.root)
            frame.pack(pady=3)

            for char in row:
                button = tk.Button(
                    frame,
                    text=char,
                    width=5,
                    height=2,
                    takefocus=0,
                    command=lambda key=char: self.type_key(key)
                )
                button.pack(side=tk.LEFT, padx=2)

        special = tk.Frame(self.root)
        special.pack(pady=5)

        tk.Button(
            special, text="Espaço", width=15, height=2,
            takefocus=0,
            command=lambda: self.press_key("space")
        ).pack(side=tk.LEFT, padx=3)

        tk.Button(
            special, text="Apagar", width=10, height=2,
            takefocus=0,
            command=lambda: self.press_key("backspace")
        ).pack(side=tk.LEFT, padx=3)

        tk.Button(
            special, text="Enter", width=10, height=2,
            takefocus=0,
            command=lambda: self.press_key("enter")
        ).pack(side=tk.LEFT, padx=3)

        tk.Button(
            special, text="Fechar", width=10, height=2,
            takefocus=0,
            command=self.hide
        ).pack(side=tk.LEFT, padx=3)

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def show(self):
        self.target_hwnd = self.user32.GetForegroundWindow()

        self.root.deiconify()
        self.root.lift()
        self.visible = True

    def hide(self):
        self.root.withdraw()
        self.visible = False

    def update(self):
        self.root.update()

    def close(self):
        self.root.destroy()

    def type_key(self, key):
        if self.target_hwnd:
            self.user32.SetForegroundWindow(self.target_hwnd)

        pyautogui.write(key)

    def press_key(self, key):
        if self.target_hwnd:
            self.user32.SetForegroundWindow(self.target_hwnd)

        pyautogui.press(key)