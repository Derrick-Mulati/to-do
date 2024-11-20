import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import time
import json
import os

class WeeklyScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Weekly Scheduler")
        self.dark_mode = False

        # Set default save file
        self.save_file = "tasks.json"
        self.days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.tasks = {day: [] for day in self.days_of_week}  # Initialize tasks storage

        # Load saved tasks
        self.load_tasks()

        # UI Setup
        self.setup_ui()

        # Start alarm check
        self.check_alarms()

    def setup_ui(self):
        # Main frame for the weekly grid
        self.week_frame = tk.Frame(self.root)
        self.week_frame.pack(pady=10)

        for idx, day in enumerate(self.days_of_week):
            self.create_day_column(day, idx)

        # Task entry area
        self.task_entry = tk.Entry(self.root, font=("Helvetica", 12), width=42)
        self.task_entry.pack(pady=5)

        # Day selection dropdown
        self.selected_day = tk.StringVar(value=self.days_of_week[0])
        self.day_menu = ttk.OptionMenu(self.root, self.selected_day, *self.days_of_week)
        self.day_menu.pack(pady=5)

        # Time selection
        time_frame = tk.Frame(self.root)
        time_frame.pack(pady=5)

        self.hour_spinbox = tk.Spinbox(time_frame, from_=0, to=23, width=3, font=("Helvetica", 12), format="%02.0f")
        self.hour_spinbox.pack(side=tk.LEFT, padx=5)
        self.minute_spinbox = tk.Spinbox(time_frame, from_=0, to=59, width=3, font=("Helvetica", 12), format="%02.0f")
        self.minute_spinbox.pack(side=tk.LEFT, padx=5)

        # Buttons
        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)
        tk.Button(action_frame, text="Add Task", font=("Helvetica", 12), command=self.add_task).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Clear Tasks", font=("Helvetica", 12), command=self.clear_all_tasks).pack(side=tk.LEFT, padx=5)

        # Dark Mode Toggle
        self.toggle_button = tk.Button(self.root, text="Dark Mode", font=("Helvetica", 12), command=self.toggle_dark_mode)
        self.toggle_button.pack(pady=5)

        # Apply default mode
        self.apply_mode()

    def create_day_column(self, day, column_index):
        day_frame = tk.Frame(self.week_frame)
        day_frame.grid(row=0, column=column_index, padx=5, pady=5, sticky="nsew")

        day_label = tk.Label(day_frame, text=day, font=("Helvetica", 14, "bold"))
        day_label.pack()

        task_container = tk.Frame(day_frame)
        task_container.pack()

        self.tasks[day] = {"frame": task_container, "tasks": []}

    def add_task(self):
        task_text = self.task_entry.get().strip()
        selected_day = self.selected_day.get()
        time_text = f"{int(self.hour_spinbox.get()):02}:{int(self.minute_spinbox.get()):02}"

        if task_text:
            task_with_time = f"{time_text} - {task_text}"
            task_frame = tk.Frame(self.tasks[selected_day]["frame"])
            task_frame.pack(anchor="w", pady=2)

            task_label = tk.Label(task_frame, text=task_with_time, font=("Helvetica", 12))
            task_label.pack(side=tk.LEFT, anchor="w")

            tk.Button(task_frame, text="Delete", font=("Helvetica", 10), command=lambda: self.delete_task(selected_day, task_frame, task_with_time)).pack(side=tk.RIGHT)

            self.tasks[selected_day]["tasks"].append((task_frame, task_with_time))
            self.task_entry.delete(0, tk.END)

            self.save_tasks()
        else:
            messagebox.showwarning("Warning", "Please enter a task.")

    def delete_task(self, day, task_frame, task_with_time):
        task_frame.pack_forget()
        task_frame.destroy()
        self.tasks[day]["tasks"] = [t for t in self.tasks[day]["tasks"] if t[1] != task_with_time]
        self.save_tasks()

    def clear_all_tasks(self):
        for day in self.tasks:
            for task_frame, _ in self.tasks[day]["tasks"]:
                task_frame.destroy()
            self.tasks[day]["tasks"] = []
        self.save_tasks()

    def check_alarms(self):
        current_time = time.strftime("%H:%M")
        current_day = time.strftime("%A")

        for task_frame, task_with_time in self.tasks.get(current_day, {}).get("tasks", []):
            task_time = task_with_time.split(" - ")[0]
            if task_time == current_time:
                messagebox.showinfo("Task Reminder", f"It's time for: {task_with_time.split(' - ')[1]}")

        self.root.after(60000, self.check_alarms)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_mode()

    def apply_mode(self):
        bg_color = "#333" if self.dark_mode else "#fff"
        fg_color = "#fff" if self.dark_mode else "#000"

        self.root.config(bg=bg_color)
        self.week_frame.config(bg=bg_color)
        self.task_entry.config(bg=bg_color, fg=fg_color, insertbackground=fg_color)
        self.toggle_button.config(bg=bg_color, fg=fg_color)

        for day in self.tasks:
            for task_frame, _ in self.tasks[day]["tasks"]:
                task_frame.config(bg=bg_color)
        for child in self.week_frame.winfo_children():
            child.config(bg=bg_color, fg=fg_color)

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
                        task_frame = tk.Frame(self.tasks[day]["frame"])
                        task_frame.pack(anchor="w", pady=2)

                        task_label = tk.Label(task_frame, text=task_with_time, font=("Helvetica", 12))
                        task_label.pack(side=tk.LEFT, anchor="w")

                        tk.Button(task_frame, text="Delete", font=("Helvetica", 10),
                                  command=lambda d=day, t=task_frame, twt=task_with_time: self.delete_task(d, t, twt)).pack(side=tk.RIGHT)

                        self.tasks[day]["tasks"].append((task_frame, task_with_time))

if __name__ == "__main__":
    root = tk.Tk()
    app = WeeklyScheduler(root)
    root.mainloop()
