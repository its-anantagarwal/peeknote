import sys
from PySide6.QtWidgets import QApplication, QWidget, QTextEdit,QVBoxLayout
from PySide6.QtCore import Qt,QTimer,QPropertyAnimation
from PySide6.QtGui import QCursor,QShortcut,QKeySequence
import json
import os

from shortcut import GlobalShortcut

NOTES_FILE = "notes.json"

app = QApplication(sys.argv)

animating = False
shortcut_open = False

window = QWidget()
window.setWindowFlags(Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint)
window.setWindowTitle("Peeknote")
window.resize(500,200)


text_box = QTextEdit()
text_box.setPlaceholderText("What do you need to remember?")
text_box.setStyleSheet("""
    QTextEdit{
        background-color:#1e1e1e;
        color:white;
        border:2px solid #3a3a3a;
        boreder-radius:12px;
        font-size: 16px;
    }

    QTextEdit:focus{
        border:2px solid #6c63ff;
    }
""")

layout = QVBoxLayout()
layout.setContentsMargins(12,12,12,12)
layout.addWidget(text_box)
window.setLayout(layout)

def keyPressEvent(event):
    if event.key()==Qt.Key.Key_Escape: window.close()

window.keyPressEvent = keyPressEvent

screen = app.primaryScreen()
screen_geometry = screen.geometry()
screen_width = screen_geometry.width()
window_x = (screen_width-window.width())//2
window.move(window_x,0)


def save_note():
    note = text_box.toPlainText()
    if not note:
        return
    notes = []
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            notes = data.get("notes", [])
            notes.append(note)
    with open(NOTES_FILE, "w", encoding = "utf-8") as file:
        json.dump({"notes": notes}, file, indent=4)


def load_note():
    if not os.path.exists(NOTES_FILE):
        return

    with open(NOTES_FILE, "r", encoding = "utf-8") as file:
        data =json.load(file)
    notes = data.get("notes",[])
    if notes:
        text_box.setPlainText(notes[-1])
    

def show_window():

    global animating

    if animating:
        return
    animating = True

    screen = app.primaryScreen()
    screen_geometry = screen.geometry()

    x = (screen_geometry.width() - window.width()) // 2
    height = window.height()

    start_geometry = window.geometry()
    start_geometry.setRect(
        x,
        -height,
        window.width(),
        height
    )

    end_geometry = window.geometry()
    end_geometry.setRect(
        x,
        0,
        window.width(),
        height
    )

    window.setGeometry(start_geometry)
    window.show()
    text_box.setFocus()

    animation = QPropertyAnimation(window, b"geometry")
    animation.setDuration(300)
    animation.setStartValue(start_geometry)
    animation.setEndValue(end_geometry)

    def finished():
        global animating
        window.setGeometry(end_geometry)
        animating = False

    animation.finished.connect(finished)
    animation.start()
    window.animation = animation


def open_from_shortcut():
    global shortcut_open
    if window.isVisible():
        hide_window()
        return
    shortcut_open = True
    show_window()

global_shortcut = GlobalShortcut()
global_shortcut.activated.connect(open_from_shortcut)


def hide_window():
    global animating
    global shortcut_open
    shortcut_open = False

    if animating:
        return
    animating = True

    screen = app.primaryScreen()
    screen_geometry = screen.geometry()
    x = (screen_geometry.width() - window.width()) // 2
    height = window.height()

    start_geometry = window.geometry()

    end_geometry = window.geometry()
    end_geometry.setRect(
        x,
        -height,
        window.width(),
        height
    )

    animation = QPropertyAnimation(window, b"geometry")
    animation.setDuration(300)
    animation.setStartValue(start_geometry)
    animation.setEndValue(end_geometry)

    def finished():
        global animating
        window.hide()
        window.setGeometry(end_geometry)
        animating = False

    animation.finished.connect(finished)
    animation.start()
    window.animation = animation

    save_note()


def check_mouse():
    global shortcut_open
    mouse_position = QCursor.pos()
    popup_rect = window.geometry()

    screen = app.primaryScreen()
    screen_geometry = screen.geometry()
    popup_width = window.width()
    trigger_left = (screen_geometry.width()-popup_width)//2
    trigger_right = trigger_left+popup_width

    mouse_in_trigger_zone = trigger_left<=mouse_position.x()<=trigger_right and mouse_position.y()<=5

    if mouse_in_trigger_zone and not window.isVisible():
        shortcut_open = False
        show_window()
    elif window.isVisible() and popup_rect.contains(mouse_position):
        shortcut_open = False
    elif window.isVisible() and not animating and not popup_rect.contains(mouse_position) and not shortcut_open:
        hide_window()

timer = QTimer()
timer.timeout.connect(check_mouse)
timer.start(50)

load_note()
window.hide()
sys.exit(app.exec())