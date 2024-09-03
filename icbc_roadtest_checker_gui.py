from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

# Location mapping
locations = {
    "Richmond claim centre (Elmbridge Way)": 273,
    "Richmond driver licensing (Lansdowne Centre mall)": 93,
    "Vancouver driver licensing (Point Grey)": 9,
    "Vancouver claim centre (Kingsway)": 275,
    "Burnaby claim centre (Wayburne Drive)": 274,
    "Surrey driver licensing": 11,
    "Newton claim centre (68 Avenue)": 271,
    "Surrey claim centre (152A St.)": 269,
    "North Vancouver driver licensing": 8
}

# Days of week mapping
days_of_week = [
    ("Monday", 0), ("Tuesday", 1), ("Wednesday", 2), ("Thursday", 3),
    ("Friday", 4), ("Saturday", 5), ("Sunday", 6)
]

# Time of day options
parts_of_day = [("Morning", 0), ("Afternoon", 1)]

# Check intervals
check_intervals = ["0.5h", "1h", "2h", "4h", "8h", "12h", "24h"]

class BackgroundColor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # very light gray
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class ICBCCheckerApp(App):
    def build(self):
        # 增加窗口的初始大小
        Window.size = (800, 600)
        
        main_layout = BackgroundColor(orientation='vertical', padding=10, spacing=10)

        # 输入字段区域
        input_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.6))
        input_scroll = ScrollView(size_hint=(1, 1))
        input_grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        input_grid.bind(minimum_height=input_grid.setter('height'))

        # 添加输入字段
        self.add_labeled_input(input_grid, "Email:", "email_input")
        self.add_labeled_input(input_grid, "Email Password:", "email_password_input", password=True)
        self.add_labeled_input(input_grid, "Username:", "username_input")
        self.add_labeled_input(input_grid, "Password:", "password_input", password=True)
        self.add_labeled_input(input_grid, "Driver's Last Name:", "drvr_lastname_input")
        self.add_labeled_input(input_grid, "License Number:", "licence_number_input")
        self.add_labeled_input(input_grid, "Keyword:", "keyword_input")
        self.add_labeled_input(input_grid, "Exam Class:", "exam_class_input")
        self.add_labeled_input(input_grid, "Start Date (YYYY-MM-DD):", "start_date_input")
        self.add_labeled_input(input_grid, "End Date (YYYY-MM-DD):", "end_date_input")
        self.add_labeled_input(input_grid, "Start Time (HH:MM):", "start_time_input")
        self.add_labeled_input(input_grid, "End Time (HH:MM):", "end_time_input")

        # Location selection dropdown
        self.location_spinner = Spinner(
            text='Select Location',
            values=list(locations.keys()),
            size_hint_y=None,
            height=44
        )
        input_grid.add_widget(Label(text="Location:", size_hint_y=None, height=44, color=(0,0,0,1)))
        input_grid.add_widget(self.location_spinner)

        # Check interval selection
        self.interval_spinner = Spinner(
            text='Check Interval',
            values=check_intervals,
            size_hint_y=None,
            height=44
        )
        input_grid.add_widget(Label(text="Check Interval:", size_hint_y=None, height=44, color=(0,0,0,1)))
        input_grid.add_widget(self.interval_spinner)

        input_scroll.add_widget(input_grid)
        input_layout.add_widget(input_scroll)
        main_layout.add_widget(input_layout)

        # 选择区域
        selection_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=10)

        # Day selection
        days_layout = GridLayout(cols=1, size_hint_x=0.5, spacing=5)
        days_layout.add_widget(Label(text="Select Days:", size_hint_y=None, height=30, color=(0,0,0,1)))
        self.day_checkboxes = {}
        for day, _ in days_of_week:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
            cb = CheckBox(size_hint_x=None, width=30)
            label = Label(text=day, color=(0,0,0,1), size_hint_x=1, halign='left')
            label.bind(size=label.setter('text_size'))
            self.day_checkboxes[day] = cb
            box.add_widget(cb)
            box.add_widget(label)
            days_layout.add_widget(box)
        selection_layout.add_widget(days_layout)

        # Time of day selection
        parts_layout = GridLayout(cols=1, size_hint_x=0.5, spacing=5)
        parts_layout.add_widget(Label(text="Select Time of Day:", size_hint_y=None, height=30, color=(0,0,0,1)))
        self.part_checkboxes = {}
        for part, _ in parts_of_day:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
            cb = CheckBox(size_hint_x=None, width=30)
            label = Label(text=part, color=(0,0,0,1), size_hint_x=1, halign='left')
            label.bind(size=label.setter('text_size'))
            self.part_checkboxes[part] = cb
            box.add_widget(cb)
            box.add_widget(label)
            parts_layout.add_widget(box)
        selection_layout.add_widget(parts_layout)

        main_layout.add_widget(selection_layout)

        # Start/Stop button
        self.start_stop_button = Button(
            text="Start Checking",
            size_hint=(1, 0.1),
            background_color=(0.2, 0.7, 0.3, 1)
        )
        self.start_stop_button.bind(on_press=self.toggle_checking)
        main_layout.add_widget(self.start_stop_button)

        # Log area
        self.log_scroll = ScrollView(size_hint=(1, 0.1))
        self.log_label = Label(text="Logs will be displayed here.", size_hint_y=None, text_size=(Window.width - 20, None), color=(0,0,0,1))
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        self.log_scroll.add_widget(self.log_label)
        main_layout.add_widget(self.log_scroll)

        self.is_checking = False
        self.check_event = None

        return main_layout

    def add_labeled_input(self, layout, label_text, input_name, password=False):
        layout.add_widget(Label(text=label_text, size_hint_y=None, height=44, color=(0,0,0,1)))
        setattr(self, input_name, TextInput(multiline=False, password=password, size_hint_y=None, height=44))
        layout.add_widget(getattr(self, input_name))

    def toggle_checking(self, instance):
        if self.is_checking:
            self.stop_checking()
        else:
            self.start_checking()

    def start_checking(self):
        try:
            interval_text = self.interval_spinner.text
            if interval_text.endswith('h'):
                interval = float(interval_text[:-1]) * 3600  # Convert hours to seconds
            else:
                raise ValueError(f"Invalid interval format: {interval_text}")
            
            # 继续处理...
            
        except ValueError as e:
            print(f"Error: {e}")
            # 可以在这里添加用户提示或其他错误处理逻辑

    def stop_checking(self):
        self.is_checking = False
        self.start_stop_button.text = "Start Checking"
        self.start_stop_button.background_color = (0.2, 0.7, 0.3, 1)  # Green
        if self.check_event:
            self.check_event.cancel()
        self.log("Stopped checking for available appointments.")

    def check_appointments(self, dt=None):
        # Get user inputs
        email = self.email_input.text
        email_password = self.email_password_input.text
        selected_location = self.location_spinner.text
        username = self.username_input.text
        password = self.password_input.text
        drvr_lastname = self.drvr_lastname_input.text
        licence_number = self.licence_number_input.text
        keyword = self.keyword_input.text
        exam_class = self.exam_class_input.text
        start_date = self.start_date_input.text
        end_date = self.end_date_input.text
        start_time = self.start_time_input.text
        end_time = self.end_time_input.text

        selected_days = [day for day, cb in self.day_checkboxes.items() if cb.active]
        selected_parts = [part for part, cb in self.part_checkboxes.items() if cb.active]

        # Check logic (implement actual checking logic here)
        self.log(f"Checking available appointments at {selected_location}...")
        self.log(f"Date range: {start_date} to {end_date}")
        self.log(f"Time range: {start_time} to {end_time}")
        self.log(f"Selected days: {', '.join(selected_days)}")
        self.log(f"Selected time of day: {', '.join(selected_parts)}")

        # Simulated check results
        simulated_results = [
            "Appointment 1: 2023-06-15 - 10:00",
            "Appointment 2: 2023-06-16 - 14:30",
            "Appointment 3: 2023-06-17 - 11:15"
        ]

        for result in simulated_results:
            self.log(result)

    def log(self, message):
        self.log_label.text += f"\n{message}"
        self.log_scroll.scroll_y = 0  # Scroll to bottom

if __name__ == '__main__':
    ICBCCheckerApp().run()