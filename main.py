import sys
from PySide6.QtWidgets import QApplication, QWidget, QTextEdit,QVBoxLayout
from PySide6.QtCore import Qt,QTimer
from PySide6.QtGui import QCursor

app = QApplication(sys.argv)

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

def check_mouse_pos():
    mouse_position = QCursor.pos()
    if mouse_position.y()<=5:
        window.show()
    elif window.isVisible() and mouse_position.y()>window.height()+20:
        window.hide()

timer = QTimer()
timer.timeout.connect(check_mouse_pos)
timer.start(50)

window.hide()
sys.exit(app.exec())