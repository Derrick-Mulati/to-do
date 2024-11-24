import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import time
import json
import os
import threading
from playsound import playsound  # Cross-platform alarm sounds
from plyer import notification  # Cross-platform notifications


class WeeklyScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Weekly Scheduler")
        self.root.geometry("800x600")
        self.dark_mode = False

        # Persistent file setup
        self.save_file = "tasks.json"
        self.days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.tasks = {day: {"frame": None, "tasks": []} for day in self.days_of_week}

        # Load tasks from the save file
        self.load_tasks()

        # UI Setup
        self.setup_ui()

        # Alarm checker
        self.check_alarms()

    def setup_ui(self):
        # Weekly grid for tasks
        self.week_frame = tk.Frame(self.root)
        self.week_frame.pack(pady=10, fill="x")

        for idx, day in enumerate(self.days_of_week):
            self.create_day_column(day, idx)

        # Task Entry Section
        entry_frame = tk.Frame(self.root)
        entry_frame.pack(pady=10)

        self.task_entry = tk.Entry(entry_frame, font=("Helvetica", 12), width=30)
        self.task_entry.grid(row=0, column=0, padx=5)

        self.selected_day = tk.StringVar(value=self.days_of_week[0])
        self.day_menu = ttk.OptionMenu(entry_frame, self.selected_day, *self.days_of_week)
        self.day_menu.grid(row=0, column=1, padx=5)

        self.hour_spinbox = tk.Spinbox(entry_frame, from_=0, to=23, width=3, font=("Helvetica", 12), format="%02.0f")
        self.hour_spinbox.grid(row=0, column=2, padx=5)
        self.minute_spinbox = tk.Spinbox(entry_frame, from_=0, to=59, width=3, font=("Helvetica", 12), format="%02.0f")
        self.minute_spinbox.grid(row=0, column=3, padx=5)

        tk.Button(entry_frame, text="Add Task", font=("Helvetica", 12), command=self.add_task).grid(row=0, column=4, padx=5)

        # Search Section
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Search Tasks:", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, font=("Helvetica", 12), width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Search", font=("Helvetica", 12), command=self.search_tasks).pack(side=tk.LEFT)

        # Dark Mode Toggle
        tk.Button(self.root, text="Dark Mode", font=("Helvetica", 12), command=self.toggle_dark_mode).pack(pady=5)

        # Clear All Tasks
        tk.Button(self.root, text="Clear All Tasks", font=("Helvetica", 12), command=self.clear_all_tasks).pack(pady=5)

        # Apply theme
        self.apply_mode()

    def create_day_column(self, day, column_index):
        day_frame = tk.Frame(self.week_frame, padx=5, pady=5)
        day_frame.grid(row=0, column=column_index, sticky="nsew")

        tk.Label(day_frame, text=day, font=("Helvetica", 14, "bold")).pack()

        task_container = tk.Frame(day_frame)
        task_container.pack(fill="x")

        self.tasks[day]["frame"] = task_container

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

        # Save immediately after adding
        self.save_tasks()

    def add_task_to_ui(self, day, task_with_time):
        task_frame = tk.Frame(self.tasks[day]["frame"], bg=self.get_background_color())
        task_frame.pack(anchor="w", pady=2)

        task_label = tk.Label(task_frame, text=task_with_time, font=("Helvetica", 12), bg=self.get_background_color(), fg=self.get_foreground_color())
        task_label.pack(side=tk.LEFT, padx=5)

        # Add a checkbox to mark the task as done or pending
        task_status = tk.BooleanVar(value=False)  # False means pending, True means done
        check_button = tk.Checkbutton(task_frame, variable=task_status, command=lambda: self.toggle_task_status(task_label, task_status))
        check_button.pack(side=tk.RIGHT, padx=5)

        # Add delete button
        tk.Button(task_frame, text="Delete", font=("Helvetica", 10),
                  command=lambda: self.delete_task(day, task_frame, task_with_time)).pack(side=tk.RIGHT, padx=5)

        self.tasks[day]["tasks"].append((task_frame, task_with_time, task_status))

        # Automatically sort tasks by time
        self.sort_tasks(day)

    def toggle_task_status(self, task_label, task_status):
        if task_status.get():
            # Mark as done - color it green
            task_label.config(fg="green")
        else:
            # Mark as pending - color it red
            task_label.config(fg="red")

    def delete_task(self, day, task_frame, task_with_time):
        task_frame.destroy()
        self.tasks[day]["tasks"] = [t for t in self.tasks[day]["tasks"] if t[1] != task_with_time]

        # Save immediately after deletion
        self.save_tasks()

    def clear_all_tasks(self):
        if messagebox.askyesno("Confirmation", "Are you sure you want to delete all tasks?"):
            for day in self.tasks:
                for task_frame, _, _ in self.tasks[day]["tasks"]:
                    task_frame.destroy()
                self.tasks[day]["tasks"] = []
            self.save_tasks()

    def search_tasks(self):
        search_query = self.search_entry.get().strip().lower()
        if not search_query:
            messagebox.showwarning("Warning", "Please enter a search query.")
            return

        found_tasks = []
        for day in self.tasks:
            for _, task_with_time, _ in self.tasks[day]["tasks"]:
                if search_query in task_with_time.lower():
                    found_tasks.append(f"{day}: {task_with_time}")

        if found_tasks:
            messagebox.showinfo("Search Results", "\n".join(found_tasks))
        else:
            messagebox.showinfo("Search Results", "No tasks found matching your query.")

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_mode()

    def apply_mode(self):
        bg_color = self.get_background_color()
        fg_color = self.get_foreground_color()

        self.root.config(bg=bg_color)
        self.week_frame.config(bg=bg_color)

        for day in self.tasks:
            for task_frame, _, _ in self.tasks[day]["tasks"]:
                task_frame.config(bg=bg_color)

    def get_background_color(self):
        return "#333" if self.dark_mode else "#fff"

    def get_foreground_color(self):
        return "#fff" if self.dark_mode else "#000"

    def save_tasks(self):
        data = {day: [(task[1], task[2].get()) for task in self.tasks[day]["tasks"]] for day in self.tasks}
        with open(self.save_file, "w") as file:
            json.dump(data, file)

    def load_tasks(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as file:
                data = json.load(file)
                for day, task_list in data.items():
                    for task_with_time, status in task_list:
                        self.add_task_to_ui(day, task_with_time)
                        # Set the initial task status (True for done, False for pending)
                        self.tasks[day]["tasks"][-1][2].set(status)

    def sort_tasks(self, day):
        self.tasks[day]["tasks"].sort(key=lambda task: task[1].split(" - ")[0])
        for task_frame, _, _ in self.tasks[day]["tasks"]:
            task_frame.pack_forget()
            task_frame.pack(anchor="w", pady=2)

    def check_alarms(self):
        current_time = time.strftime("%H:%M")
        current_day = time.strftime("%A")

        for _, task_with_time, _ in self.tasks.get(current_day, {}).get("tasks", []):
            task_time = task_with_time.split(" - ")[0]
            if task_time == current_time:
                threading.Thread(target=self.play_alarm).start()
                notification.notify(title="Task Reminder", message=f"It's time for: {task_with_time.split(' - ')[1]}")

        self.root.after(60000, self.check_alarms)

    def play_alarm(self):
        try:
            playsound("alarm_sound.mp3")  # Replace with your sound file
        except Exception as e:
            print("Error playing sound:", e)


if __name__ == "__main__":
    root = tk.Tk()
    app = WeeklyScheduler(root)
    root.mainloop()
