import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import time

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weekly To-Do App with Time")

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

        # Buttons to add and delete tasks
        add_button = tk.Button(self.root, text="Add Task", font=("Helvetica", 12), command=self.add_task)
        add_button.pack(pady=5)

        delete_button = tk.Button(self.root, text="Delete Task", font=("Helvetica", 12), command=self.delete_task)
        delete_button.pack(pady=5)

        # Start checking for alarms
        self.check_alarms()

    def create_day_column(self, day, column_index):
        day_frame = tk.Frame(self.week_frame)
        day_frame.grid(row=0, column=column_index, padx=10)

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
            time_text = simpledialog.askstring("Task Time", "Enter time for the task (e.g., 14:30):")
            if not time_text:
                time_text = "No time specified"
            
            task_with_time = f"{task_text} - {time_text}"
            var = tk.BooleanVar()
            task = tk.Checkbutton(self.tasks_by_day[selected_day]["frame"], text=task_with_time, variable=var, font=("Helvetica", 12))
            task.pack(anchor="w")
            self.tasks_by_day[selected_day]["tasks"].append((task, var, time_text))
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "You must enter a task.")

    def delete_task(self):
        selected_day = self.selected_day.get()
        tasks_to_remove = [task for task, var, _ in self.tasks_by_day[selected_day]["tasks"] if var.get()]
        if tasks_to_remove:
            for task, _, _ in tasks_to_remove:
                task.pack_forget()
                self.tasks_by_day[selected_day]["tasks"].remove((task, _, _))
        else:
            messagebox.showwarning("Warning", "You must select a task to delete.")

    def check_alarms(self):
        current_time = time.strftime("%H:%M")
        current_day = time.strftime("%A")
        tasks = self.tasks_by_day.get(current_day, {}).get("tasks", [])

        for task, _, task_time in tasks:
            if task_time == current_time:
                messagebox.showinfo("Task Reminder", f"Time to do: {task.cget('text')}")
                # Optionally, mark the task as completed or delete it after the reminder

        # Check again after 60 seconds
        self.root.after(60000, self.check_alarms)

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
