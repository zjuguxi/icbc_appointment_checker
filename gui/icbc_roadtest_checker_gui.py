from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import datetime
import re

# 假设这些变量已在文件的其他地方定义
locations = {
    "Richmond claim centre (Elmbridge Way)": 273,
    "Richmond driver licensing (Lansdowne Centre mall)": 93,
    "Vancouver driver licensing (Point Grey)": 9,
    # ... 其他位置 ...
}

days_of_week = [
    ("Monday", 0), ("Tuesday", 1), ("Wednesday", 2), ("Thursday", 3),
    ("Friday", 4), ("Saturday", 5), ("Sunday", 6)
]

parts_of_day = [("Morning", 0), ("Afternoon", 1)]

check_intervals = ["0.5h", "1h", "2h", "4h", "8h", "12h", "24h"]

class BackgroundColor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # 浅灰色
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class ICBCCheckerApp(App):
    def build(self):
        Window.size = (600, 1200)
        
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
        input_grid.add_widget(Label(text="Location:", size_hint_y=None, height=44, color=(0, 0, 0, 1)))
        input_grid.add_widget(self.location_spinner)

        input_scroll.add_widget(input_grid)
        input_layout.add_widget(input_scroll)
        main_layout.add_widget(input_layout)

        # 选择区域
        selection_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))

        # Day selection
        days_layout = BoxLayout(orientation='vertical', size_hint_x=0.5)
        days_layout.add_widget(Label(text="Select Days:", size_hint_y=None, height=30, color=(0, 0, 0, 1)))
        days_grid = GridLayout(cols=1, spacing=5)
        self.day_checkboxes = {}
        for day, _ in days_of_week:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
            cb = CheckBox(size_hint_x=None, width=30)
            label = Label(text=day, size_hint_x=1, halign='left', color=(0, 0, 0, 1))
            label.bind(size=label.setter('text_size'))
            self.day_checkboxes[day] = cb
            box.add_widget(cb)
            box.add_widget(label)
            days_grid.add_widget(box)
        days_layout.add_widget(days_grid)
        selection_layout.add_widget(days_layout)

        # Time of day selection and Check Interval
        parts_and_interval_layout = BoxLayout(orientation='vertical', size_hint_x=0.5)
        
        parts_layout = BoxLayout(orientation='vertical')
        parts_layout.add_widget(Label(text="Select Time of Day:", size_hint_y=None, height=30, color=(0, 0, 0, 1)))
        parts_grid = GridLayout(cols=1, spacing=5)
        self.part_checkboxes = {}
        for part, _ in parts_of_day:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
            cb = CheckBox(size_hint_x=None, width=30)
            label = Label(text=part, size_hint_x=1, halign='left', color=(0, 0, 0, 1))
            label.bind(size=label.setter('text_size'))
            self.part_checkboxes[part] = cb
            box.add_widget(cb)
            box.add_widget(label)
            parts_grid.add_widget(box)
        parts_layout.add_widget(parts_grid)
        parts_and_interval_layout.add_widget(parts_layout)

        # Check interval selection
        interval_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=74)
        interval_layout.add_widget(Label(text="Check Interval:", size_hint_y=None, height=30, color=(0, 0, 0, 1)))
        self.interval_spinner = Spinner(
            text='Check Interval',
            values=check_intervals,
            size_hint_y=None,
            height=44
        )
        interval_layout.add_widget(self.interval_spinner)
        parts_and_interval_layout.add_widget(interval_layout)

        selection_layout.add_widget(parts_and_interval_layout)
        main_layout.add_widget(selection_layout)

        # Start/Stop button
        self.start_stop_button = Button(
            text="Start Checking",
            size_hint=(1, 0.05),
            background_color=(0.2, 0.7, 0.3, 1)
        )
        self.start_stop_button.bind(on_press=self.toggle_checking)
        main_layout.add_widget(self.start_stop_button)

        # Log area
        self.log_scroll = ScrollView(size_hint=(1, 0.05))
        self.log_label = Label(text="Logs will be displayed here.  Developed by GuXi", size_hint_y=None, text_size=(Window.width - 20, None), color=(0, 0, 0, 1))
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        self.log_scroll.add_widget(self.log_label)
        main_layout.add_widget(self.log_scroll)

        self.is_checking = False
        self.check_event = None

        return main_layout

    def add_labeled_input(self, layout, label_text, input_name, password=False):
        layout.add_widget(Label(text=label_text, size_hint_y=None, height=44, color=(0, 0, 0, 1)))
        setattr(self, input_name, TextInput(multiline=False, password=password, size_hint_y=None, height=44))
        layout.add_widget(getattr(self, input_name))

    def toggle_checking(self, instance):
        if not self.is_checking:
            try:
                self.start_checking()
                self.start_stop_button.text = "Stop Checking"
                self.start_stop_button.background_color = (0.7, 0.2, 0.2, 1)  # 红色
                self.is_checking = True
            except Exception as e:
                self.update_log(f"Error: {str(e)}")
                self.start_stop_button.background_color = (0.7, 0.2, 0.2, 1)  # 红色
        else:
            self.stop_checking()
            self.start_stop_button.text = "Start Checking"
            self.start_stop_button.background_color = (0.2, 0.7, 0.3, 1)  # 绿色
            self.is_checking = False

    def start_checking(self):
        if not self.validate_inputs():
            raise ValueError("Please fill in all required fields correctly.")

        interval_text = self.interval_spinner.text
        if interval_text.endswith('h'):
            interval = float(interval_text[:-1]) * 3600  # 将小时转换为秒
        else:
            raise ValueError(f"Invalid interval format: {interval_text}")

        self.check_event = Clock.schedule_interval(self.check_availability, interval)
        self.update_log("Checking started.")

    def stop_checking(self):
        if self.check_event:
            self.check_event.cancel()
        self.update_log("Checking stopped.")

    def check_availability(self, dt):
        # 这里应该实现实际的可用性检查逻辑
        # 这只是一个示例，你需要根据实际情况修改
        self.update_log("Checking availability...")
        
        # 模拟检查过程
        import random
        if random.random() < 0.1:  # 10% 的概率找到可用时间
            available_time = datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 30))
            self.update_log(f"Available time found: {available_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            self.update_log("No available times found.")

    def validate_inputs(self):
        required_fields = [
            self.email_input, self.email_password_input, self.username_input,
            self.password_input, self.drvr_lastname_input, self.licence_number_input,
            self.exam_class_input, self.start_date_input, self.end_date_input,
            self.start_time_input, self.end_time_input
        ]
        
        for field in required_fields:
            if not field.text.strip():
                return False
        
        # 验证日期格式
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not (date_pattern.match(self.start_date_input.text) and date_pattern.match(self.end_date_input.text)):
            return False
        
        # 验证时间格式
        time_pattern = re.compile(r'^\d{2}:\d{2}$')
        if not (time_pattern.match(self.start_time_input.text) and time_pattern.match(self.end_time_input.text)):
            return False
        
        # 验证是否选择了位置
        if self.location_spinner.text == 'Select Location':
            return False
        
        # 验证是否选择了检查间隔
        if self.interval_spinner.text == 'Check Interval':
            return False
        
        # 验证是否至少选择了一天和一个时间段
        if not any(cb.active for cb in self.day_checkboxes.values()):
            return False
        if not any(cb.active for cb in self.part_checkboxes.values()):
            return False
        
        return True

    def update_log(self, message):
        current_log = self.log_label.text
        if current_log == "Logs will be displayed here.  Developed by GuXi":
            self.log_label.text = message
        else:
            self.log_label.text = f"{message}\n{current_log}"

if __name__ == '__main__':
    ICBCCheckerApp().run()