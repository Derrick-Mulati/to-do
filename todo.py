import tkinter as tk
from tkinter import messagebox

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do App with Checkboxes")

        # Frame for the tasks and scrollbar
        self.task_frame = tk.Frame(self.root)
        self.task_frame.pack(pady=10)

        # Canvas for the task list and scrollbar
        self.canvas = tk.Canvas(self.task_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.task_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.task_container = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.task_container, anchor="nw")

        # Entry widget to add tasks
        self.task_entry = tk.Entry(self.root, font=("Helvetica", 12), width=42)
        self.task_entry.pack(pady=10)

        # Buttons to add and delete tasks
        add_button = tk.Button(self.root, text="Add Task", font=("Helvetica", 12), command=self.add_task)
        add_button.pack(pady=5)

        delete_button = tk.Button(self.root, text="Delete Task", font=("Helvetica", 12), command=self.delete_task)
        delete_button.pack(pady=5)

        self.tasks = []

    def add_task(self):
        task_text = self.task_entry.get()
        if task_text:
            var = tk.BooleanVar()
            task = tk.Checkbutton(self.task_container, text=task_text, variable=var, font=("Helvetica", 12))
            task.pack(anchor="w")
            self.tasks.append((task, var))
            self.task_entry.delete(0, tk.END)
            self.update_canvas()
        else:
            messagebox.showwarning("Warning", "You must enter a task.")

    def delete_task(self):
        tasks_to_remove = [task for task, var in self.tasks if var.get()]
        if tasks_to_remove:
            for task, _ in tasks_to_remove:
                task.pack_forget()
                self.tasks.remove((task, _))
            self.update_canvas()
        else:
            messagebox.showwarning("Warning", "You must select a task to delete.")

    def update_canvas(self):
        self.root.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
