from pynput import keyboard
from PySide6.QtCore import QObject,Signal

class GlobalShortcut(QObject):
    activated = Signal()
    def __init__(self):
        super().__init__()
        self.listener =keyboard.GlobalHotKeys({"<ctrl>+<space>":self.activated.emit})
        self.listener.start()