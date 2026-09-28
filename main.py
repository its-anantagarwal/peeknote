import sys
from PySide6.QtWidgets import QApplication, QWidget, QTextEdit,QVBoxLayout,QLabel,QPushButton,QListWidget,QHBoxLayout,QStackedWidget,QListWidgetItem,QMessageBox
from PySide6.QtCore import Qt,QTimer,QPropertyAnimation
from PySide6.QtGui import QCursor,QShortcut,QKeySequence
from datetime import datetime
import json
import os

from shortcut import GlobalShortcut

app_data_folder = os.path.join(
    os.environ["APPDATA"],
    "PeekNote"
)

os.makedirs(app_data_folder, exist_ok=True)

NOTES_FILE = os.path.join(
    app_data_folder,
    "notes.json"
)

app = QApplication(sys.argv)

animating = False
shortcut_open = False
last_saved_note = ""
current_note_id = None

save_status_timer = QTimer()
save_status_timer.setSingleShot(True)

window = QWidget()
# window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
window.setStyleSheet("""
    QWidget{
        background-color:#121212;
    }
""")
window.setWindowFlags(Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint)
window.setWindowTitle("Peek Note")
window.resize(500,200)


text_box = QTextEdit()
text_box.setPlaceholderText("What do you need to remember?")
text_box.setStyleSheet("""
    QTextEdit{
        background-color: #1e1e1e;
        color:white;
        border:2px solid #3a3a3a;
        border-radius:12px;
        padding:12px;
        font-size: 16px;
    }

    QTextEdit:focus{
        border:2px solid #6c63ff;
    }
""")

title = QLabel("Peek Note")
title.setStyleSheet("""
    QLabel{
        color:white;
        font-size:14px;
        font-weight:bold;
        padding-left:4px;
    }
""")

counter = QLabel("0 characters")
counter.setStyleSheet("""
    QLabel{
        color:#888888;
        font-size:11px;
        padding-left:4px;
    }
""")

editor_page = QWidget()
editor_layout = QVBoxLayout()
editor_layout.setContentsMargins(0,0,0,0)
editor_layout.setSpacing(4)

editor_layout.addWidget(text_box)
info_row = QHBoxLayout()
info_row.setContentsMargins(0,0,0,0)
info_row.setSpacing(8)
info_row.addWidget(counter,1)

save_status = QLabel("")
save_status.setStyleSheet("""
    QLabel{
        color:#888888;
        font-size:11px;
    }
""")

info_row.addWidget(save_status)
info_row.addStretch()
editor_layout.addLayout(info_row)

editor_page.setLayout(editor_layout)
history_page = QWidget()
history_layout = QVBoxLayout()
history_layout.setContentsMargins(0,0,0,0)
history_layout.setSpacing(8)
history_list = QListWidget()
history_list.setStyleSheet("""
    QListWidget{
        background-color:#1e1e1e;
        color:white;
        border:2px solid #3a3a3a;
        border-radius:10px;
        padding:5px;
        font-size:14px;
    }
    QListWidget::item{
        padding:10px;
    }
    QListWidget::item:selected{
        background-color:#6c63ff;
        color:white;
    }
""")

delete_button = QPushButton("Delete note")
delete_button.setStyleSheet("""
    QPushButton{
        background-color:#2a2a2a;
        color:white;
        border:1px solid #444444;
        border-radius: 6px;
        padding:8px;
    }
    QPushButton:hover{
        background-color:#3a3a3a;
    }
""")
history_layout.addWidget(history_list)
history_layout.addWidget(delete_button)
history_page.setLayout(history_layout)
pages = QStackedWidget()
pages.addWidget(editor_page)
pages.addWidget(history_page)
layout = QVBoxLayout()
layout.setContentsMargins(12,12,12,12)
layout.setSpacing(8)
header = QHBoxLayout()
header.addWidget(title)
new_button = QPushButton("+")
new_button.setFixedWidth(35)
save_button = QPushButton("Save")
save_button.setFixedWidth(50)
history_button = QPushButton("History")
history_button.setFixedWidth(70)

quit_button = QPushButton("Quit")
quit_button.setFixedWidth(50)
header.addWidget(new_button)
header.addWidget(save_button)
header.addWidget(history_button)
header.addWidget(quit_button)
layout.addLayout(header)
layout.addWidget(pages)
window.setLayout(layout)

quit_button.clicked.connect(app.quit)

def load_history():
    history_list.clear()
    if not os.path.exists(NOTES_FILE):
        return
    try:
        with open (NOTES_FILE, "r", encoding="utf-8") as file:
            data=json.load(file)
    except(json.JSONDecodeError, OSError):
        return

    notes = data.get("notes", [])
    for note in reversed(notes):
        created = note.get("created")
        if created:
            try:
                created_time = datetime.fromisoformat(created)
                formatted_time=created_time.strftime("%d %b %Y %I:%M %p")
            except ValueError:
                formatted_time = "Unknown"
        else:
            formatted_time = "Unknown"

        item = QListWidgetItem(f"{note['text']}\nCreated: {formatted_time}")
        item.setData(Qt.ItemDataRole.UserRole, note["id"])
        history_list.addItem(item)


def open_selected_note(item):
    global current_note_id
    global last_saved_note
    note_id = item.data(Qt.ItemDataRole.UserRole)
    if not os.path.exists(NOTES_FILE):
        return

    with open(NOTES_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
    notes = data.get("notes",[])
    for note in notes:
        if note["id"]==note_id:
            current_note_id=note["id"]
            last_saved_note=note["text"]
            text_box.setPlainText(note["text"])
            break
    
    pages.setCurrentWidget(editor_page)
    text_box.setFocus()


def delete_selected_note():
    global current_note_id
    global last_saved_note
    selected_item = history_list.currentItem()
    if selected_item is None:
        return

    note_id = selected_item.data(Qt.ItemDataRole.UserRole)

    if note_id is None:
        return
    if not os.path.exists(NOTES_FILE):
        return

    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except(json.JSONDecodeError, OSError):
        return

    notes = data.get("notes")
    if not isinstance(notes, list):
        return

    selected_note=None

    for note in notes:
        if note["id"]==note_id:
            selected_note=note
            break

    if selected_note is None:
        return

    note_text = selected_note.get("text", "")
    reply = QMessageBox.question(
        window,
        "Delete Note",
        f"Are you sure you want to delete this note?\n\n{note_text}",
        QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )

    if reply!=QMessageBox.StandardButton.Yes:
        return

    notes=[note for note in notes if note.get("id")!=note_id]


    with open(NOTES_FILE, "w", encoding="utf-8") as file:
        json.dump({"notes":notes}, file, indent=4)

    if current_note_id==note_id:
        current_note_id = None
        last_saved_note=""
        text_box.clear()
    load_history()

delete_button.clicked.connect(delete_selected_note)

def show_history():
    pages.setCurrentWidget(history_page)
    history_button.setText("Back")
    load_history()


def back_to_editor():
    pages.setCurrentWidget(editor_page)
    history_button.setText("History")
    text_box.setFocus()

def new_note():
    global current_note_id
    global last_saved_note

    save_note()

    current_note_id = None
    last_saved_note = ""

    text_box.clear()
    pages.setCurrentWidget(editor_page)
    text_box.setFocus()

def toggle_history():
    if pages.currentWidget()==history_page:
        back_to_editor()
    else:
        show_history()

history_button.clicked.connect(toggle_history)
new_button.clicked.connect(new_note)
history_list.itemDoubleClicked.connect(open_selected_note)

def update_counter():
    count = len(text_box.toPlainText())
    counter.setText(f"{count} characters")

text_box.textChanged.connect(update_counter)

def keyPressEvent(event):
    if event.key()==Qt.Key.Key_Escape:
        hide_window()

window.keyPressEvent = keyPressEvent

screen = app.primaryScreen()
screen_geometry = screen.geometry()
screen_width = screen_geometry.width()
window_x = (screen_width-window.width())//2
window.move(window_x,0)


def show_save_feedback():
    save_status.setText("Saved ✓")
    save_status_timer.start(1500)

def clear_save_feedback():
    save_status.setText("")

save_status_timer.timeout.connect(clear_save_feedback)

def save_note():
    global last_saved_note
    global current_note_id
    note = text_box.toPlainText()
    notes = []
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                notes = data.get("notes", [])
        except(json.JSONDecodeError, OSError):
            notes=[]

    if not note:
        if current_note_id is not None:
            notes=[item for item in notes if item ["id"] != current_note_id]
            with open(NOTES_FILE, "w", encoding="utf-8") as file:
                json.dump({"notes": notes}, file, indent=4)

            current_note_id = None

        last_saved_note=""
        return

    if current_note_id is not None:
        for item in notes:
            if item["id"]==current_note_id:
                item["text"]=note
                break
    else:
        new_id = max((item["id"] for item in notes), default=0)+1
        notes.append({
            "id":new_id,
            "text":note,
            "created":datetime.now().isoformat()
        })
        current_note_id = new_id

    with open(NOTES_FILE, "w", encoding = "utf-8") as file:
        json.dump({"notes": notes}, file, indent=4)
    last_saved_note = note
    show_save_feedback()

save_button.clicked.connect(save_note)

def load_note():
    global last_saved_note
    global current_note_id
    if not os.path.exists(NOTES_FILE):
        return

    try:
        with open(NOTES_FILE, "r", encoding = "utf-8") as file:
            data =json.load(file)
    except(json.JSONDecodeError, OSError):
        return
    notes = data.get("notes",[])
    if notes:
        latest_note = notes[-1]
        text_box.setPlainText(latest_note["text"])
        last_saved_note = latest_note["text"]
        current_note_id=latest_note["id"]

    update_counter()
    

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

    save_note()
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