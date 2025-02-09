from compasspy.client import Compass
import time
from datetime import datetime
import re
#NOTE - Init Client

client = Compass('prefix', 'cookie')
client.login()

def get_teacher_name(teachers, code):
    for teacher in teachers:
        if teacher.displayCode == code:
            return teacher.n  # Full name
    return None

def get_teacher_code(teachers,backup=None):
    for i in [teacher.displayCode for teacher in teachers]:
        if i in backup:
            if bool(re.search(rf'(^|\W){re.escape(i)}(\W|$)', backup)):
                return get_teacher_name(teachers,i)

    return None

locations = [['12SC', '12SC'], ['APA', 'APA'], ['APC', 'APC'], ['APPC', 'APPC'], ['AR01', 'AR1'], ['AR02', 'AR2'], ['CA01', 'CA1'], ['CA03', 'CA3'], ['CAPA', 'CAPAT'], ['CHPL', 'CHPL'], ['DAN1', 'DAN1'], ['FT01', 'FT1'], ['FT02', 'FT2'], ['GH', 'GH'], ['GT', 'GT'], ['LHTF', 'LHYTLTF'], ['LHTM', 'LHYTLTM'], ['LH01', 'LH1'], ['LH02', 'LH2'], ['LH03', 'LH3'], ['LH04', 'LH4'], ['LH05', 'LH5'], ['LH06', 'LH6'], ['LH07', 'LH7'], ['LHBO', 'LHBO'], ['LIB1', 'LIB1'], ['LIB2', 'LIB2'], ['LIB3', 'LIB3'], ['LIBS', 'LIBST11'], ['LIBS', 'LIBST12'], ['MC01', 'MC1'], ['MC02', 'MC2'], ['MC03', 'MC3'], ['MC04', 'MC4'], ['MC05', 'MC5'], ['MC06', 'MC6'], ['MC07', 'MC7'], ['MC08', 'MC8'], ['MC09', 'MC9'], ['MCBO', 'MCBO'], ['MEET', 'MEET'], ['METF', 'METTLTF'], ['METM', 'METTLTM'], ['MET01', 'MET1'], ['MET02', 'MET2'], ['MET03', 'MET3'], ['MET04', 'MET4'], ['MET05', 'MET5'], ['MET06', 'MET6'], ['MET07', 'MET7'], ['MET08', 'MET8'], ['MET09', 'MET9'], ['MTSR', 'METSR'], ['MT10', 'MT10'], ['MT11', 'MT11'], ['MT12', 'MT12'], ['MT13', 'MT13'], ['MT14', 'MT14'], ['MU01', 'MU1'], ['MU02', 'MU2'], ['MU03', 'MU3'], ['OFCA', 'OFFCAMP'], ['OLC1', 'OLC1'], ['OLC2', 'OLC2'], ['OLC3', 'OLC3'], ['OLC4', 'OLC4'], ['OLC5', 'OLC5'], ['OLC6', 'OLC6'], ['PSTA', 'PAST'], ['PILB', 'PILAB'], ['PRIN', 'PRIN'], ['PWL1', 'PWL1'], ['PWL2', 'PWL2'], ['QDTF', 'QDTLTF'], ['QDTM', 'QDTLTM'], ['SH01', 'SH1'], ['SH02', 'SH2'], ['SH03', 'SH3'], ['SH04', 'SH4'], ['SL01', 'SL'], ['TM01', 'TM1'], ['TPT1', 'TPass'], ['TTC1', 'TTC01'], ['TTC2', 'TTC02'], ['TTC3', 'TTC03'], ['TTC4', 'TTCO4'], ['TW01', 'TW1'], ['TW02', 'TW2'], ['TX01', 'TX1'], ['TX02', 'TX2'], ['UNA', 'UNASSIGNED'], ['VHO', 'VHO'], ['VIL2', 'VIL2']]


timetableRaw = client.getTimetable("7/02/2025")
teacherlist= client.getStaff()
rooms = client.getLocations()
timetableUnsorted = []
for i in timetableRaw['d']['data']:
    timetableUnsorted.append({
        "Running":True if i['runningStatus'] == 1 else False,
        "title": re.search(r"\((.*?)\)", i["topAndBottomLine"]).group(1) if re.search(r"\((.*?)\)", i["topAndBottomLine"]) else i["topAndBottomLine"],
        "TopLineInfo": i['topAndBottomLine'],
        "short_title": i["topTitleLine"],
        "start": i["start"].split(" - ")[1],
        "finish": i['finish'].split(" - ")[1],
        "all_day?": i["allDay"],
        "teacher": get_teacher_code(teacherlist,i["topAndBottomLine"]),
        "room": next((room.n for room in rooms if re.search(rf'(^|\W){re.escape(room.n)}(\W|$)', i["topAndBottomLine"])), "NA")
    })
timetable = sorted(
    timetableUnsorted,
    key=lambda d: time.strptime(d["start"], "%I:%M %p"),
)

# Print the sorted timetable
for entry in timetable:
    formatted_start = time.strftime("%I:%M %p", time.strptime(entry["start"], "%I:%M %p"))
    entry["start"] = formatted_start



def parse_time(time_str):
    return datetime.strptime(time_str, '%I:%M %p')

def get_current_and_next_classes(data, current_time):
    active_classes = [
        item for item in data if item['Running'] and parse_time(item['start']) <= current_time < parse_time(item['finish'])
    ]
    
    future_classes = [
        item for item in data if parse_time(item['start']) > current_time
    ]
    
    if active_classes:
        most_recent_class = max(active_classes, key=lambda x: parse_time(x['start']))
        current_class = most_recent_class

    else:
        current_class = None
    
    if future_classes:
        next_class = min(future_classes, key=lambda x: parse_time(x['start']))
    else:
        next_class = None
    
    return current_class, next_class

user_time_str = '2:30 PM'
user_time = parse_time(user_time_str)

current_class, next_class = get_current_and_next_classes(timetable, user_time)
print(f"Current class: {current_class}")
print(f"Next class: {next_class}")


import sys
from PyQt6.QtCore import Qt, QThread, pyqtSignal,QTimer
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QApplication, QMainWindow,QToolTip
import win32gui
import win32con
from PyQt6.uic import loadUi

from qfluentwidgets import setTheme, Theme, PushButton, ToolTipPosition
from qfluentwidgets.components.material import AcrylicToolTipFilter
from PyQt5.QtGui import QDesktopServices

class FetchThread(QThread): 
    data_fetched = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.running = True  # Flag to control the loop

    def run(self):
        while self.running:
            try:
                self.data_fetched.emit(True)
                self.msleep(100)
            except Exception as e:
                print(f"Error in fetch thread: {e}")
                self.data_fetched.emit(False)

    def stop(self):
        self.running = False


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        loadUi(r'compassproto.ui', self)
        
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.move(6, 1036)


        self.TopLabel.setText(current_class['title'])
        self.Bottom_Label.setText(f"{current_class['teacher']} | {current_class['start']} - {current_class['finish']}")
        self.icon_test.setText(current_class['room'])
        print(self.frame.width())
        # self.setFixedSize(47, 1000)

        self.setToolTip("Hello")
        self.installEventFilter(AcrylicToolTipFilter(self.frame, 0, ToolTipPosition.TOP))

        self.fetch_thread = FetchThread()
        self.fetch_thread.data_fetched.connect(self.keep_on_top)
        self.fetch_thread.start()
        print("Fetch thread started")

        # Connect QApplication instance exit to stop thread
        QApplication.instance().aboutToQuit.connect(self.fetch_thread.stop)

        # Timer to track cursor position
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_cursor_position)
        self.timer.start(100)  # Check every 100ms

        self.mouse_inside = False  # Track if the cursor is inside the window

    def check_cursor_position(self):
        """Continuously check if the cursor is inside the main window."""
        cursor_pos = self.mapFromGlobal(QCursor.pos()) 
        rect = self.rect()

        if rect.contains(cursor_pos):
            if not self.mouse_inside:
                self.mouse_inside = True
                self.on_mouse_enter()
        else:
            if self.mouse_inside:
                self.mouse_inside = False
                self.on_mouse_leave()

    def on_mouse_enter(self):
        """Triggers when the mouse enters the main window (including child widgets)."""
        self.frame.setStyleSheet("QWidget#frame{background-color: rgba(255,255,255,150);border-radius:4;border: 1px solid rgba(0, 0, 0, 0.073);border-bottom: 1px solid rgba(0, 0, 0, 0.183);}")
        # Show tooltip at current cursor position
        print("Mouse Entered Window")

    def on_mouse_leave(self):
        """Triggers when the mouse leaves the main window (even if over child widgets)."""
        self.frame.setStyleSheet("QWidget#frame{background-color: rgba(0,0,0,0);border-radius:4;}")

        print("Mouse Left Window")

    def keep_on_top(self):
        try:
            hwnd = int(self.winId())
            if not self.is_window_on_top(hwnd):
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
        except Exception as e:
            print(f"Error keeping window on top: {e}")

    def is_window_on_top(self, hwnd):
        """Check if the window is already on top"""
        topmost = win32gui.GetWindowPlacement(hwnd)[1]
        return topmost == win32con.HWND_TOPMOST


app = QApplication(sys.argv)
demo = Window()
demo.show()
sys.exit(app.exec())