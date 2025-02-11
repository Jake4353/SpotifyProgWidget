from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QFont
from PyQt6.QtCore import Qt, QRectF
from win32mica import ApplyMica, MicaTheme, MicaStyle

class Event:
    def __init__(self, name, start_hour, end_hour, color=QColor(50, 100, 255, 150), border_color=QColor(0, 0, 0), secondary_text=""):
        self.name = name
        self.start_hour = self.convert_time_to_float(start_hour)
        self.end_hour = self.convert_time_to_float(end_hour)
        self.color = color
        self.border_color = border_color
        self.secondary_text = secondary_text
        self.column = 0
        self.total_columns = 1

    @staticmethod
    def convert_time_to_float(time_str):
        dt = datetime.strptime(time_str, "%I:%M %p")  
        return dt.hour + dt.minute / 60  

class TimelineGraph(QWidget):
    def __init__(self, events, h_padding=10):
        super().__init__()
        ApplyMica(self.winId(), MicaTheme.DARK, MicaStyle.DEFAULT)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.events = events
        self.h_padding = h_padding
        self.setMinimumSize(600, 400)

    def calculate_event_layout(self):
        time_slots = {}  
        
        # Scan for every half-hour interval
        time_step = 0.5  # Increments by 30 minutes
        current_time = 8.0  # Start at 8 AM
        end_time = 17.0  # End at 5 PM

        while current_time <= end_time:
            time_slots[current_time] = [
                ev for ev in self.events if ev.start_hour <= current_time < ev.end_hour
            ]
            current_time += time_step

        # Determine max overlapping events at any point
        max_columns = max(len(events) for events in time_slots.values())

        # Assign columns dynamically
        assigned_columns = {}
        for time, active_events in time_slots.items():
            available_columns = set(range(max_columns))  # Track used columns

            for ev in active_events:
                if ev not in assigned_columns:
                    # Find first available column
                    ev.column = next(i for i in available_columns if i not in [assigned_columns.get(e) for e in active_events])
                    assigned_columns[ev] = ev.column
                else:
                    ev.column = assigned_columns[ev]

        # Set total columns for proper spacing
        for ev in self.events:
            ev.total_columns = max_columns

    def paintEvent(self, event):
        self.calculate_event_layout()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Define colors and styles
        bg_color = QColor(255,255,255,0)
        grid_color = QColor(150, 150, 150)
        text_color = QColor(250, 250, 250)

        painter.fillRect(self.rect(), bg_color)

        margin = 50
        timeline_top = margin
        timeline_height = self.height() - 2 * margin
        timeline_width = self.width() - 2 * margin
        hour_step = timeline_height / 9  # 8AM-8PM range

        pen = QPen(grid_color)
        pen.setWidth(1)
        painter.setPen(pen)
        font = QFont("Arial", 10)
        painter.setFont(font)

        for i in range(10):
            y = int(timeline_top + i * hour_step)
            painter.drawLine(margin, y, self.width() - margin, y)

            hour_label = f"{8 + i}:00"
            painter.setPen(text_color)
            painter.drawText(10, y - 5, hour_label)
            painter.setPen(grid_color)

            if i < 12:
                dotted_pen = QPen(grid_color, 1, Qt.PenStyle.DotLine)
                painter.setPen(dotted_pen)
                half_y = int(y + hour_step / 2)
                painter.drawLine(margin, half_y, self.width() - margin, half_y)
                painter.setPen(grid_color)

        # Draw events
        v_padding = 5
        for ev in self.events:
            y_start = int(timeline_top + (ev.start_hour - 8) * hour_step) + v_padding
            y_end = int(timeline_top + (ev.end_hour - 8) * hour_step) - v_padding
            event_height = max(10, y_end - y_start)  # Ensure a minimum height

            # Adjust width and spacing for overlapping events
            column_width = (timeline_width - 10) / ev.total_columns
            x_start = int(margin + ev.column * column_width + self.h_padding)
            event_width = int(column_width - self.h_padding * 2)

            # Fill event rectangle
            painter.fillRect(QRectF(x_start, y_start, event_width, event_height), ev.color)
            
            # Draw event border
            border_pen = QPen(ev.border_color)
            border_pen.setWidth(2)
            painter.setPen(border_pen)
            painter.drawRect(QRectF(x_start, y_start, event_width, event_height))
            
            # Draw event text
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(x_start + 5, y_start + 15, ev.name)
            
            # Draw secondary text
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(x_start + 5, y_start + 30, ev.secondary_text)

        painter.end()




from compasspy.client import Compass
import time
from datetime import datetime
import re
#NOTE - Init Client

client = Compass()
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


events=[Event(i["title"],i["start"],i['finish'],QColor(200, 50, 50, 150),QColor(255,0,0),f"") for i in timetable]

app = QApplication([])
window = TimelineGraph(events, h_padding=3)
window.show()
app.exec()
