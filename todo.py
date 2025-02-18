import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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
            self.week_frame.columnconfigure(idx, weight=1)  # Make columns expand evenly

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

        self.priority_var = tk.StringVar(value="Medium")
        self.priority_menu = ttk.OptionMenu(entry_frame, self.priority_var, "Medium", "High", "Medium", "Low")
        self.priority_menu.grid(row=0, column=4, padx=5)

        ttk.Button(entry_frame, text="Add Task", command=self.add_task).grid(row=0, column=5, padx=5)

    def create_settings_view(self):
        settings_frame = ttk.Frame(self.settings_tab, padding=10)
        settings_frame.pack(fill="both", expand=True)

        ttk.Label(settings_frame, text="Customize Settings", font=("Helvetica", 16)).pack(pady=10)
        ttk.Button(settings_frame, text="Toggle Theme", command=self.toggle_theme).pack(pady=5)
        ttk.Button(settings_frame, text="Export Tasks", command=self.export_tasks).pack(pady=5)
        ttk.Button(settings_frame, text="Import Tasks", command=self.import_tasks).pack(pady=5)

    def add_task(self):
        task_text = self.task_entry.get().strip()
        selected_day = self.selected_day.get()
        time_text = f"{int(self.hour_spinbox.get()):02}:{int(self.minute_spinbox.get()):02}"
        priority = self.priority_var.get()

        if not task_text:
            messagebox.showwarning("Warning", "Please enter a task description.")
            return

        task_with_time = f"{time_text} - {task_text} [{priority}]"
        self.add_task_to_ui(selected_day, task_with_time)
        self.task_entry.delete(0, tk.END)

        self.save_tasks()

    def add_task_to_ui(self, day, task_with_time):
        task_frame = ttk.Frame(self.tasks[day]["frame"])
        task_frame.pack(anchor="w", pady=2)

        task_var = tk.BooleanVar(value=False)
        task_check = ttk.Checkbutton(task_frame, variable=task_var, command=lambda: self.mark_task_complete(day, task_with_time, task_var))
        task_check.pack(side=tk.LEFT, padx=5)

        task_label = ttk.Label(task_frame, text=task_with_time, font=("Helvetica", 12))
        task_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(task_frame, text="Delete", command=lambda: self.delete_task(day, task_frame, task_with_time)).pack(side=tk.RIGHT, padx=5)

        self.tasks[day]["tasks"].append((task_frame, task_with_time, task_var))

    def mark_task_complete(self, day, task_with_time, task_var):
        if task_var.get():
            print(f"Task '{task_with_time}' on {day} marked as complete.")

    def delete_task(self, day, task_frame, task_with_time):
        task_frame.destroy()
        self.tasks[day]["tasks"] = [t for t in self.tasks[day]["tasks"] if t[1] != task_with_time]
        self.save_tasks()

    def toggle_theme(self):
        current_theme = self.style.theme_use()
        new_theme = "litera" if current_theme == "darkly" else "darkly"
        self.style.theme_use(new_theme)

    def save_tasks(self, file_path=None):
        file_path = file_path or self.save_file
        data = {day: [task[1] for task in self.tasks[day]["tasks"]] for day in self.tasks}
        try:
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tasks: {e}")

    def load_tasks(self, file_path=None):
        file_path = file_path or self.save_file
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as file:
                    data = json.load(file)
                    for day, task_list in data.items():
                        for task_with_time in task_list:
                            self.add_task_to_ui(day, task_with_time)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load tasks: {e}")

    def export_tasks(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:
            threading.Thread(target=self.save_tasks, args=(file_path,)).start()

    def import_tasks(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            threading.Thread(target=self.load_tasks, args=(file_path,)).start()

    def check_alarms(self):
        current_time = time.strftime("%H:%M")
        for day in self.days_of_week:
            for task in self.tasks[day]["tasks"]:
                task_time = task[1].split(" - ")[0]  # Extract time from task string
                if task_time == current_time:
                    self.notify_user(day, task[1])
        self.root.after(60000, self.check_alarms)  # Check every minute

    def notify_user(self, day, task):
        messagebox.showinfo("Task Reminder", f"It's time for your task on {day}:\n{task}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernWeeklyScheduler(root)
    root.mainloop()