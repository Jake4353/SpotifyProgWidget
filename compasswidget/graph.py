from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QFont
from PyQt6.QtCore import Qt, QRectF

class Event:
    def __init__(self, name, start_hour, end_hour, color=QColor(50, 100, 255, 150), border_color=QColor(0, 0, 0), secondary_text=""):
        self.name = name
        self.start_hour = float(start_hour)
        self.end_hour = float(end_hour)
        self.color = color
        self.border_color = border_color
        self.secondary_text = secondary_text
        self.column = 0
        self.total_columns = 1

class TimelineGraph(QWidget):
    def __init__(self, events, h_padding=10):
        super().__init__()
        self.events = events
        self.h_padding = h_padding
        self.setMinimumSize(600, 400)
        self.setStyleSheet("background-color: rgb(30, 30, 30);")

    def calculate_event_layout(self):
        """ Assigns each event to a separate column based on time overlaps dynamically. """
        time_slots = {}  # Dictionary mapping time slots to active events
        
        # Scan for every half-hour interval
        time_step = 0.5  # Increments by 30 minutes
        current_time = 8.0  # Start at 8 AM
        end_time = 20.0  # End at 8 PM

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
        bg_color = QColor(30, 30, 30)
        grid_color = QColor(150, 150, 150)
        text_color = QColor(220, 220, 220)

        painter.fillRect(self.rect(), bg_color)

        # Calculate layout
        margin = 50
        timeline_top = margin
        timeline_height = self.height() - 2 * margin
        timeline_width = self.width() - 2 * margin
        hour_step = timeline_height / 12  # 8AM-8PM range

        # Draw hour grid lines
        pen = QPen(grid_color)
        pen.setWidth(1)
        painter.setPen(pen)
        font = QFont("Arial", 10)
        painter.setFont(font)

        for i in range(13):
            y = int(timeline_top + i * hour_step)
            painter.drawLine(margin, y, self.width() - margin, y)

            hour_label = f"{8 + i}:00"
            painter.setPen(text_color)
            painter.drawText(10, y + 5, hour_label)
            painter.setPen(grid_color)

            if i < 12:
                dotted_pen = QPen(grid_color, 1, Qt.PenStyle.DotLine)
                painter.setPen(dotted_pen)
                half_y = int(y + hour_step / 2)
                painter.drawLine(margin, half_y, self.width() - margin, half_y)
                painter.setPen(grid_color)

        # Draw events
        v_padding = 5  # Add vertical padding between events
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

# Sample events with custom colors and borders
events = [
    Event("Math", 9, 10.5, QColor(200, 50, 50, 150), QColor(255, 0, 0), "Room 101"),
    Event("English", 10, 11.5, QColor(50, 200, 50, 150), QColor(0, 255, 0), "Room 202"),
    Event("History", 10, 11.5, QColor(50, 50, 200, 150), QColor(0, 0, 255), "Room 303"),
    Event("Science", 12, 13, QColor(255, 165, 0, 150), QColor(255, 140, 0), "Lab A"),
    Event("Physics", 12, 14, QColor(128, 0, 128, 150), QColor(255, 0, 255), "Lab B"),
    Event("Art", 14, 15, QColor(255, 20, 147, 150), QColor(255, 105, 180), "Studio 5")
]

# Run the application
app = QApplication([])
window = TimelineGraph(events, h_padding=10)
window.show()
app.exec()
