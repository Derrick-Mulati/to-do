import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
from datetime import datetime, timedelta
import os

# Google Calendar API imports
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WEEKLY SCHEDULER")

        # Google Calendar API setup
        self.creds = None
        self.setup_google_calendar()

        # Create a frame to hold the grid of days
        self.week_frame = tk.Frame(self.root)
        self.week_frame.pack(pady=10)

        # Dictionary to hold tasks for each day
        self.tasks_by_day = {}

        # Define days of the week
        days_of_the_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Create columns for each day
        for i, day in enumerate(days_of_the_week):
            self.create_day_column(day, i)

        # Entry widget to add tasks
        self.task_entry = tk.Entry(self.root, font=("Helvetica", 12), width=42)
        self.task_entry.pack(pady=10)

        # Dropdown menu to select the day for the task
        self.selected_day = tk.StringVar(self.root)
        self.selected_day.set(days_of_the_week[0])  # Default value
        self.day_menu = tk.OptionMenu(self.root, self.selected_day, *days_of_the_week)
        self.day_menu.pack(pady=5)

        # Frame for the time selection (clock interface)
        time_frame = tk.Frame(self.root)
        time_frame.pack(pady=5)

        self.hour_spinbox = tk.Spinbox(time_frame, from_=0, to=23, width=3, font=("Helvetica", 12), format="%02.0f")
        self.hour_spinbox.pack(side=tk.LEFT, padx=5)
        tk.Label(time_frame, text=":", font=("Helvetica", 12)).pack(side=tk.LEFT)
        self.minute_spinbox = tk.Spinbox(time_frame, from_=0, to=59, width=3, font=("Helvetica", 12), format="%02.0f")
        self.minute_spinbox.pack(side=tk.LEFT, padx=5)

        # Buttons to add and delete tasks
        add_button = tk.Button(self.root, text="Add Task", font=("Helvetica", 12), command=self.add_task)
        add_button.pack(pady=5)

        # Load dustbin icon and resize it
        original_icon = Image.open("dustbin.png")  # Make sure the file path is correct
        resized_icon = original_icon.resize((16, 16), Image.LANCZOS)
        self.dustbin_icon = ImageTk.PhotoImage(resized_icon)

        # Start checking for alarms
        self.check_alarms()

    def setup_google_calendar(self):
        """Setup Google Calendar API and authenticate user."""
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        self.service = build('calendar', 'v3', credentials=self.creds)

    def create_day_column(self, day, column_index):
        day_frame = tk.Frame(self.week_frame)
        day_frame.grid(row=0, column=column_index, padx=10, pady=5, sticky="nsew")

        day_label = tk.Label(day_frame, text=day, font=("Helvetica", 14, "bold"))
        day_label.pack()

        task_container = tk.Frame(day_frame)
        task_container.pack()

        self.tasks_by_day[day] = {
            "frame": task_container,
            "tasks": []
        }

    def add_task(self):
        task_text = self.task_entry.get()
        selected_day = self.selected_day.get()

        if task_text:
            time_text = f"{int(self.hour_spinbox.get()):02}:{int(self.minute_spinbox.get()):02}"
            task_with_time = f"{task_text} - {time_text}"
            var = tk.BooleanVar()
            
            # Create task frame to hold the task text and delete button
            task_frame = tk.Frame(self.tasks_by_day[selected_day]["frame"])
            task_frame.pack(anchor="w", pady=2)

            # Task checkbutton with dynamic color change
            task = tk.Checkbutton(task_frame, text=task_with_time, variable=var, font=("Helvetica", 12), 
                                  fg="red", command=lambda: self.update_task_color(task, var))
            task.pack(side=tk.LEFT, anchor="w")

            # Delete button with resized dustbin icon
            delete_button = tk.Button(task_frame, image=self.dustbin_icon, command=lambda: self.delete_task(selected_day, task_frame, task, var))
            delete_button.pack(side=tk.RIGHT, padx=5)

            # Store task information
            self.tasks_by_day[selected_day]["tasks"].append((task_frame, task, var, time_text))

            self.add_to_google_calendar(task_text, selected_day, time_text)  # Add to Google Calendar

            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "You must enter a task.")

    def add_to_google_calendar(self, task_text, selected_day, time_text):
        """Add the task to Google Calendar."""
        day_to_date = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6
        }
        now = datetime.now()
        target_day = (day_to_date[selected_day] - now.weekday()) % 7
        task_date = now + timedelta(days=target_day)
        task_time = datetime.strptime(time_text, "%H:%M").time()
        event_start = datetime.combine(task_date, task_time)
        event_end = event_start + timedelta(hours=1)  # Assuming a 1-hour task duration

        event = {
            'summary': task_text,
            'start': {
                'dateTime': event_start.isoformat(),
                'timeZone': 'UTC',  # Adjust this to your timezone
            },
            'end': {
                'dateTime': event_end.isoformat(),
                'timeZone': 'UTC',
            },
        }
        event = self.service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")

    def update_task_color(self, task, var):
        if var.get():
            task.config(fg="green")
        else:
            task.config(fg="red")

    def delete_task(self, selected_day, task_frame, task, var):
        # Remove the task frame and delete it from the list
        task_frame.pack_forget()
        task_frame.destroy()
        self.tasks_by_day[selected_day]["tasks"].remove((task_frame, task, var, var.get()))

    def check_alarms(self):
        current_time = time.strftime("%H:%M")
        current_day = time.strftime("%A")
        tasks = self.tasks_by_day.get(current_day, {}).get("tasks", [])

        for task_frame, task, var, task_time in tasks:
            if task_time == current_time:
                messagebox.showinfo("Task Reminder", f"Time to do: {task.cget('text')}")
                # Optionally, mark the task as completed or delete it after the reminder

        # Check again after 60 seconds
        self.root.after(60000, self.check_alarms)

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
