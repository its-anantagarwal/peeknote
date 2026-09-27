import sys
from PySide6.QtWidgets import QApplication, QWidget, QTextEdit,QVBoxLayout
from PySide6.QtCore import Qt,QTimer,QPropertyAnimation
from PySide6.QtGui import QCursor

import json
import os

NOTES_FILE = "notes.json"

app = QApplication(sys.argv)

animating = False

window = QWidget()
window.setWindowFlags(Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint)
window.setWindowTitle("Peeknote")
window.resize(500,200)


text_box = QTextEdit()
text_box.setPlaceholderText("What do you need to remember?")
# text_box.setParent(window)

layout = QVBoxLayout()
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
    note = text_box.toPlainText().strip()
    if not note:
        return

    with open(NOTES_FILE, "w", encoding = "utf-8") as file:
        json.dump({"note": note}, file, indent=4)


def load_note():
    if not os.path.exists(NOTES_FILE):
        return

    with open(NOTES_FILE, "r", encoding = "utf-8") as file:
        data =json.load(file)

    text_box.setPlainText(data.get("note",""))

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


def hide_window():
    global animating
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


def check_mouse_pos():
    mouse_position = QCursor.pos()

    if mouse_position.y() <= 5 and not window.isVisible():
        show_window()
    elif window.isVisible() and not animating and mouse_position.y() > window.height() + 20:
        hide_window()

timer = QTimer()
timer.timeout.connect(check_mouse_pos)
timer.start(50)

load_note()
window.hide()
sys.exit(app.exec())