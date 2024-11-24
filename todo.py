import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkbootstrap import Style
from PIL import Image, ImageTk
import time
import json
import os
import threading

class ModernWeeklyScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Weekly Scheduler")
        self.root.geometry("900x700")
        
        # Initialize Style
        self.style = Style(theme="darkly")  # Modern theme
        self.root.configure(bg=self.style.colors.bg)

        # File and data initialization
        self.save_file = "tasks.json"
        self.days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.tasks = {day: {"frame": None, "tasks": []} for day in self.days_of_week}

        self.load_tasks()

        # UI Setup
        self.setup_ui()

        # Start alarm checking
        self.check_alarms()

    def setup_ui(self):
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Weekly Tasks Tab
        self.tasks_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tasks_tab, text="Weekly Tasks")
        self.create_weekly_view()

        # Add Task Section
        self.create_task_entry()

        # Settings Tab
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        self.create_settings_view()

    def create_weekly_view(self):
        self.week_frame = ttk.Frame(self.tasks_tab)
        self.week_frame.pack(fill="both", expand=True, padx=10, pady=10)

        for idx, day in enumerate(self.days_of_week):
            self.create_day_column(day, idx)

    def create_day_column(self, day, column_index):
        # Scrollable Frame
        frame_container = ttk.Frame(self.week_frame)
        frame_container.grid(row=0, column=column_index, sticky="nsew", padx=5, pady=5)

        day_label = ttk.Label(frame_container, text=day, font=("Helvetica", 14, "bold"))
        day_label.pack()

        canvas = tk.Canvas(frame_container, width=120, height=300, bg=self.style.colors.bg)
        canvas.pack(side=tk.LEFT, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        task_container = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=task_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.tasks[day]["frame"] = task_container
        task_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def create_task_entry(self):
        entry_frame = ttk.Frame(self.tasks_tab)
        entry_frame.pack(pady=10, padx=10, fill="x")

        self.task_entry = ttk.Entry(entry_frame, width=40)
        self.task_entry.grid(row=0, column=0, padx=5)

        self.selected_day = tk.StringVar(value=self.days_of_week[0])
        self.day_menu = ttk.OptionMenu(entry_frame, self.selected_day, *self.days_of_week)
        self.day_menu.grid(row=0, column=1, padx=5)

        self.hour_spinbox = ttk.Spinbox(entry_frame, from_=0, to=23, width=3, format="%02.0f")
        self.hour_spinbox.grid(row=0, column=2, padx=5)
        self.minute_spinbox = ttk.Spinbox(entry_frame, from_=0, to=59, width=3, format="%02.0f")
        self.minute_spinbox.grid(row=0, column=3, padx=5)

        ttk.Button(entry_frame, text="Add Task", command=self.add_task).grid(row=0, column=4, padx=5)

    def create_settings_view(self):
        settings_frame = ttk.Frame(self.settings_tab, padding=10)
        settings_frame.pack(fill="both", expand=True)

        ttk.Label(settings_frame, text="Customize Settings", font=("Helvetica", 16)).pack(pady=10)
        ttk.Button(settings_frame, text="Toggle Theme", command=self.toggle_theme).pack(pady=5)

    def add_task(self):
        task_text = self.task_entry.get().strip()
        selected_day = self.selected_day.get()
        time_text = f"{int(self.hour_spinbox.get()):02}:{int(self.minute_spinbox.get()):02}"

        if not task_text:
            messagebox.showwarning("Warning", "Please enter a task description.")
            return

        task_with_time = f"{time_text} - {task_text}"
        self.add_task_to_ui(selected_day, task_with_time)
        self.task_entry.delete(0, tk.END)

        self.save_tasks()

    def add_task_to_ui(self, day, task_with_time):
        task_frame = ttk.Frame(self.tasks[day]["frame"])
        task_frame.pack(anchor="w", pady=2)

        task_label = ttk.Label(task_frame, text=task_with_time, font=("Helvetica", 12))
        task_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(task_frame, text="Delete", command=lambda: self.delete_task(day, task_frame, task_with_time)).pack(side=tk.RIGHT, padx=5)

        self.tasks[day]["tasks"].append((task_frame, task_with_time))

    def delete_task(self, day, task_frame, task_with_time):
        task_frame.destroy()
        self.tasks[day]["tasks"] = [t for t in self.tasks[day]["tasks"] if t[1] != task_with_time]
        self.save_tasks()

    def toggle_theme(self):
        current_theme = self.style.theme_use()
        new_theme = "litera" if current_theme == "darkly" else "darkly"
        self.style.theme_use(new_theme)

    def save_tasks(self):
        data = {day: [task[1] for task in self.tasks[day]["tasks"]] for day in self.tasks}
        with open(self.save_file, "w") as file:
            json.dump(data, file)

    def load_tasks(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as file:
                data = json.load(file)
                for day, task_list in data.items():
                    for task_with_time in task_list:
                        self.add_task_to_ui(day, task_with_time)

    def check_alarms(self):
        # Simplified for brevity
        self.root.after(60000, self.check_alarms)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernWeeklyScheduler(root)
    root.mainloop()
