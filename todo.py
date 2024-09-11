import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import os
import time

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WEEKLY SCHEDULER")

        self.dark_mode = False  # Variable to track the current mode

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

        # Set the default time to 07:00
        self.hour_spinbox = tk.Spinbox(time_frame, from_=0, to=23, width=3, font=("Helvetica", 12), format="%02.0f")
        self.hour_spinbox.pack(side=tk.LEFT, padx=5)
        self.hour_spinbox.delete(0, tk.END)  # Clear the default 0 value
        self.hour_spinbox.insert(0, "07")    # Set default hour to 07

        tk.Label(time_frame, text=":", font=("Helvetica", 12)).pack(side=tk.LEFT)

        self.minute_spinbox = tk.Spinbox(time_frame, from_=0, to=59, width=3, font=("Helvetica", 12), format="%02.0f")
        self.minute_spinbox.pack(side=tk.LEFT, padx=5)
        self.minute_spinbox.delete(0, tk.END)  # Clear the default 0 value
        self.minute_spinbox.insert(0, "00")    # Set default minute to 00

        # Buttons to add and delete tasks
        add_button = tk.Button(self.root, text="Add Task", font=("Helvetica", 12), command=self.add_task)
        add_button.pack(pady=5)

        # Button to toggle dark mode
        self.toggle_button = tk.Button(self.root, text="Dark Mode", font=("Helvetica", 12), command=self.toggle_dark_mode)
        self.toggle_button.pack(pady=10)

        # Load dustbin icon and resize it
        try:
            icon_path = "dustbin.png"  # Adjust the path if necessary
            original_icon = Image.open(icon_path)
            resized_icon = original_icon.resize((16, 16), Image.LANCZOS)
            self.dustbin_icon = ImageTk.PhotoImage(resized_icon)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load icon: {e}")
            self.dustbin_icon = None

        # Load tasks from file
        self.load_tasks()

        # Start checking for alarms
        self.check_alarms()

        # Apply the initial mode (default light mode)
        self.apply_mode()

    def create_day_column(self, day, column_index):
        day_frame = tk.Frame(self.week_frame)
        day_frame.grid(row=0, column=column_index, padx=10, pady=5, sticky="nsew")

        day_label = tk.Label(day_frame, text=day, font=("Helvetica", 14, "bold"))
        day_label.pack()

        task_container = tk.Frame(day_frame)
        task_container.pack()

        self.tasks_by_day[day] = {
            "frame": task_container,
            "tasks": [],
            "label": day_label
        }

    def add_task(self):
        task_text = self.task_entry.get()
        selected_day = self.selected_day.get()

        if task_text:
            time_text = f"{int(self.hour_spinbox.get()):02}:{int(self.minute_spinbox.get()):02}"
            task_with_time = f"{time_text} - {task_text}"  # Time appears before the task
            var = tk.BooleanVar()

            # Create task frame to hold the task text and delete button
            task_frame = tk.Frame(self.tasks_by_day[selected_day]["frame"])
            task_frame.pack(anchor="w", pady=2)

            # Task checkbutton with dynamic color change
            task = tk.Checkbutton(task_frame, text=task_with_time, variable=var, font=("Helvetica", 12),
                                  fg="red", command=lambda t=task, v=var: self.update_task_color(t, v))
            task.pack(side=tk.LEFT, anchor="w")

            # Delete button with resized dustbin icon
            if self.dustbin_icon:
                delete_button = tk.Button(task_frame, image=self.dustbin_icon, command=lambda: self.delete_task(selected_day, task_frame))
            else:
                delete_button = tk.Button(task_frame, text="Delete", command=lambda: self.delete_task(selected_day, task_frame))
            delete_button.pack(side=tk.RIGHT, padx=5)

            # Store task information
            self.tasks_by_day[selected_day]["tasks"].append((task_frame, task, var, time_text))

            self.task_entry.delete(0, tk.END)
            self.save_tasks()  # Save tasks after adding
        else:
            messagebox.showwarning("Warning", "You must enter a task.")

    def update_task_color(self, task, var):
        if var.get():
            task.config(fg="green")
        else:
            task.config(fg="red")

    def delete_task(self, selected_day, task_frame):
        # Remove the task frame and delete it from the list
        task_frame.pack_forget()
        task_frame.destroy()
        self.tasks_by_day[selected_day]["tasks"] = [t for t in self.tasks_by_day[selected_day]["tasks"] if t[0] != task_frame]
        self.save_tasks()  # Save tasks after deletion

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

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_mode()

    def apply_mode(self):
        bg_color = "#333333" if self.dark_mode else "#ffffff"
        fg_color = "#ffffff" if self.dark_mode else "#000000"
        button_bg_color = "#444444" if self.dark_mode else "#f0f0f0"

        # Update root window and all frames
        self.root.config(bg=bg_color)
        self.week_frame.config(bg=bg_color)

        # Update task entry, dropdown menu, and time spinboxes
        self.task_entry.config(bg=bg_color, fg=fg_color, insertbackground=fg_color)
        self.day_menu.config(bg=button_bg_color, fg=fg_color)
        self.hour_spinbox.config(bg=bg_color, fg=fg_color)
        self.minute_spinbox.config(bg=bg_color, fg=fg_color)

        # Update the day labels and tasks
        for day, data in self.tasks_by_day.items():
            data["label"].config(bg=bg_color, fg=fg_color)
            for task_frame, task, var, _ in data["tasks"]:
                task_frame.config(bg=bg_color)
                task.config(bg=bg_color, fg="green" if var.get() else "red")

        # Update buttons
        self.toggle_button.config(bg=button_bg_color, fg=fg_color)
        for child in self.root.winfo_children():
            if isinstance(child, tk.Button) and child != self.toggle_button:
                child.config(bg=button_bg_color, fg=fg_color)

    def save_tasks(self):
        try:
            with open("tasks.json", "w") as file:
                tasks_to_save = {
                    day: [
                        (task_frame.winfo_children()[0].cget("text"), var.get(), time_text)
                        for task_frame, task, var, time_text in data["tasks"]
                    ]
                    for day, data in self.tasks_by_day.items()
                }
                json.dump(tasks_to_save, file)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def load_tasks(self):
        if os.path.exists("tasks.json"):
            try:
                with open("tasks.json", "r") as file:
                    tasks_to_load = json.load(file)

                for day, tasks in tasks_to_load.items():
                    for task_text, completed, time_text in tasks:
                        # Recreate the task
                        var = tk.BooleanVar(value=completed)
                        task_frame = tk.Frame(self.tasks_by_day[day]["frame"])
                        task_frame.pack(anchor="w", pady=2)

                        task = tk.Checkbutton(task_frame, text=task_text, variable=var, font=("Helvetica", 12),
                                              fg="green" if completed else "red", command=lambda t=task, v=var: self.update_task_color(t, v))
                        task.pack(side=tk.LEFT, anchor="w")

                        if self.dustbin_icon:
                            delete_button = tk.Button(task_frame, image=self.dustbin_icon, command=lambda: self.delete_task(day, task_frame))
                        else:
                            delete_button = tk.Button(task_frame, text="Delete", command=lambda: self.delete_task(day, task_frame))
                        delete_button.pack(side=tk.RIGHT, padx=5)

                        self.tasks_by_day[day]["tasks"].append((task_frame, task, var, time_text))
            except Exception as e:
                print(f"Error loading tasks: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()

