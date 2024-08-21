import tkinter as tk
from tkinter import messagebox

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do App")

        # Frame for the listbox and scrollbar
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        # Listbox to display tasks
        self.task_listbox = tk.Listbox(
            frame, height=10, width=50, selectmode=tk.SINGLE, font=("Helvetica", 12)
        )
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        # Scrollbar for the listbox
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.task_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.task_listbox.yview)

        # Entry widget to add tasks
        self.task_entry = tk.Entry(
            self.root, font=("Helvetica", 12), width=42
        )
        self.task_entry.pack(pady=10)

        # Buttons to add and delete tasks
        add_button = tk.Button(
            self.root, text="Add Task", font=("Helvetica", 12), command=self.add_task
        )
        add_button.pack(pady=5)

        delete_button = tk.Button(
            self.root, text="Delete Task", font=("Helvetica", 12), command=self.delete_task
        )
        delete_button.pack(pady=5)

    def add_task(self):
        task = self.task_entry.get()
        if task:
            self.task_listbox.insert(tk.END, task)
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "You must enter a task.")

    def delete_task(self):
        try:
            selected_task_index = self.task_listbox.curselection()[0]
            self.task_listbox.delete(selected_task_index)
        except IndexError:
            messagebox.showwarning("Warning", "You must select a task to delete.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
