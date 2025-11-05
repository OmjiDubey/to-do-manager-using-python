import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os

# Set appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class Task:
    def __init__(self, title, category, priority, due_date, completed=False, timestamp=None):
        self.title = title
        self.category = category
        self.priority = priority
        self.due_date = due_date
        self.completed = completed
        self.timestamp = timestamp if timestamp else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class ToDoManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("To-Do Manager")
        
        # Data storage
        self.tasks = []
        self.load_tasks()
        
        # Main container
        self.create_widgets()
        self.display_tasks()
        
        # Maximize the window after everything is loaded
        self.after(100, lambda: self.state('zoomed'))
        
    def create_widgets(self):
        # Header
        header = ctk.CTkLabel(self, text="To-Do Manager", font=ctk.CTkFont(size=32, weight="bold"))
        header.pack(pady=20)
        
        # Filter frame
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=40, pady=10)
        
        # Search
        search_label = ctk.CTkLabel(filter_frame, text="Search:", font=ctk.CTkFont(size=14))
        search_label.grid(row=0, column=0, padx=5, sticky="w")
        
        self.search_entry = ctk.CTkEntry(filter_frame, width=200, placeholder_text="")
        self.search_entry.grid(row=0, column=1, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.display_tasks())
        
        # Filter dropdown
        filter_label = ctk.CTkLabel(filter_frame, text="Filter:", font=ctk.CTkFont(size=14))
        filter_label.grid(row=0, column=2, padx=(40, 5), sticky="w")
        
        self.filter_var = ctk.StringVar(value="All")
        self.filter_dropdown = ctk.CTkComboBox(
            filter_frame, 
            values=["All", "Completed", "Pending"],
            variable=self.filter_var,
            width=150,
            command=lambda x: self.display_tasks()
        )
        self.filter_dropdown.grid(row=0, column=3, padx=5)
        
        # Category dropdown
        category_label = ctk.CTkLabel(filter_frame, text="Category:", font=ctk.CTkFont(size=14))
        category_label.grid(row=0, column=4, padx=(40, 5), sticky="w")
        
        self.category_var = ctk.StringVar(value="All")
        self.category_dropdown = ctk.CTkComboBox(
            filter_frame,
            values=["All", "Personal", "Work"],
            variable=self.category_var,
            width=150,
            command=lambda x: self.display_tasks()
        )
        self.category_dropdown.grid(row=0, column=5, padx=5)
        
        # Sort by
        sort_label = ctk.CTkLabel(filter_frame, text="Sort by:", font=ctk.CTkFont(size=14))
        sort_label.grid(row=0, column=6, padx=(40, 5), sticky="w")
        
        self.sort_var = ctk.StringVar(value="Recent")
        
        recent_btn = ctk.CTkButton(
            filter_frame,
            text="Recent",
            width=100,
            command=lambda: self.set_sort("Recent")
        )
        recent_btn.grid(row=0, column=7, padx=2)
        
        priority_btn = ctk.CTkButton(
            filter_frame,
            text="Priority",
            width=100,
            fg_color="gray",
            command=lambda: self.set_sort("Priority")
        )
        priority_btn.grid(row=0, column=8, padx=2)
        
        date_btn = ctk.CTkButton(
            filter_frame,
            text="Date",
            width=100,
            fg_color="gray",
            command=lambda: self.set_sort("Date")
        )
        date_btn.grid(row=0, column=9, padx=2)
        
        self.recent_btn = recent_btn
        self.priority_btn = priority_btn
        self.date_btn = date_btn
        
        # Tasks label
        tasks_label = ctk.CTkLabel(self, text="Tasks", font=ctk.CTkFont(size=16), 
                                   fg_color="#c0c0c0", corner_radius=10, height=40)
        tasks_label.pack(fill="x", padx=40, pady=(20, 10))
        
        # Scrollable frame for tasks
        self.tasks_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.tasks_frame.pack(fill="both", expand=True, padx=40, pady=10)
        
        # Add new task button
        add_btn = ctk.CTkButton(
            self,
            text="+ Add New Task",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            command=self.open_add_task_dialog
        )
        add_btn.pack(pady=20)
        
        # Status bar
        self.status_bar = ctk.CTkLabel(
            self,
            text="Total: 0 | Pending: 0 | Completed: 0",
            font=ctk.CTkFont(size=14),
            fg_color="#404040",
            text_color="white",
            height=35
        )
        self.status_bar.pack(fill="x", side="bottom")
        
    def set_sort(self, sort_type):
        self.sort_var.set(sort_type)
        if sort_type == "Recent":
            self.recent_btn.configure(fg_color=["#3B8ED0", "#1F6AA5"])
            self.priority_btn.configure(fg_color="gray")
            self.date_btn.configure(fg_color="gray")
        elif sort_type == "Priority":
            self.recent_btn.configure(fg_color="gray")
            self.priority_btn.configure(fg_color=["#3B8ED0", "#1F6AA5"])
            self.date_btn.configure(fg_color="gray")
        else:
            self.recent_btn.configure(fg_color="gray")
            self.priority_btn.configure(fg_color="gray")
            self.date_btn.configure(fg_color=["#3B8ED0", "#1F6AA5"])
        self.display_tasks()
        
    def display_tasks(self):
        # Clear existing tasks
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()
        
        # Filter tasks
        filtered_tasks = self.filter_tasks()
        
        # Sort tasks
        filtered_tasks = self.sort_tasks(filtered_tasks)
        
        # Display tasks
        for task in filtered_tasks:
            self.create_task_widget(task)
        
        # Update status bar
        self.update_status_bar()
        
    def filter_tasks(self):
        filtered = self.tasks.copy()
        
        # Search filter
        search_text = self.search_entry.get().lower()
        if search_text:
            filtered = [t for t in filtered if search_text in t.title.lower()]
        
        # Completion filter
        filter_val = self.filter_var.get()
        if filter_val == "Completed":
            filtered = [t for t in filtered if t.completed]
        elif filter_val == "Pending":
            filtered = [t for t in filtered if not t.completed]
        
        # Category filter
        category_val = self.category_var.get()
        if category_val != "All":
            filtered = [t for t in filtered if t.category == category_val]
        
        return filtered
    
    def sort_tasks(self, tasks):
        if self.sort_var.get() == "Recent":
            # Sort by timestamp - newest first
            return sorted(tasks, key=lambda t: datetime.strptime(t.timestamp, "%Y-%m-%d %H:%M:%S"), reverse=True)
        elif self.sort_var.get() == "Priority":
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            return sorted(tasks, key=lambda t: priority_order.get(t.priority, 3))
        else:  # Date
            # Separate tasks with and without dates
            tasks_with_date = [t for t in tasks if t.due_date]
            tasks_without_date = [t for t in tasks if not t.due_date]
            
            # Sort tasks with dates
            tasks_with_date.sort(key=lambda t: datetime.strptime(t.due_date, "%m/%d/%Y"))
            
            # Return tasks with dates first, then tasks without dates
            return tasks_with_date + tasks_without_date
    
    def create_task_widget(self, task):
        task_frame = ctk.CTkFrame(self.tasks_frame, fg_color="white", corner_radius=10)
        task_frame.pack(fill="x", pady=5, padx=10)
        
        # Checkbox
        checkbox = ctk.CTkCheckBox(
            task_frame,
            text="",
            command=lambda: self.toggle_task(task),
            checkbox_width=24,
            checkbox_height=24
        )
        checkbox.pack(side="left", padx=(15, 10), pady=15)
        
        if task.completed:
            checkbox.select()
        
        # Task details
        priority_color = {"High": "#ff4444", "Medium": "#ffaa00", "Low": "#44aa44"}.get(task.priority, "gray")
        
        due_date_text = f" (Due: {task.due_date})" if task.due_date else ""
        task_text = f"[{task.priority}] {task.title} - {task.category}{due_date_text}"
        
        # Change text color based on completion status
        text_color = "#999999" if task.completed else "#000000"
        
        task_label = ctk.CTkLabel(
            task_frame,
            text=task_text,
            font=ctk.CTkFont(size=14),
            anchor="w",
            text_color=text_color
        )
        task_label.pack(side="left", fill="x", expand=True, padx=10)
        
        # Update button
        update_btn = ctk.CTkButton(
            task_frame,
            text="Update",
            width=80,
            fg_color="#1976d2",
            hover_color="#1565c0",
            command=lambda: self.open_update_task_dialog(task)
        )
        update_btn.pack(side="right", padx=(5, 15))
        
        # Delete button
        delete_btn = ctk.CTkButton(
            task_frame,
            text="Delete",
            width=80,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            command=lambda: self.delete_task(task)
        )
        delete_btn.pack(side="right", padx=5)
        
    def toggle_task(self, task):
        task.completed = not task.completed
        self.save_tasks()
        self.display_tasks()
        
    def delete_task(self, task):
        self.tasks.remove(task)
        self.save_tasks()
        self.display_tasks()
        
    def open_add_task_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Task")
        dialog.geometry("500x450")
        dialog.grab_set()  # Make dialog modal
        
        # Center the dialog
        dialog.transient(self)
        
        self.create_task_dialog(dialog, None)
    
    def open_update_task_dialog(self, task):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Update Task")
        dialog.geometry("500x450")
        dialog.grab_set()  # Make dialog modal
        
        # Center the dialog
        dialog.transient(self)
        
        self.create_task_dialog(dialog, task)
    
    def create_task_dialog(self, dialog, task=None):
        
        # Title
        title_label = ctk.CTkLabel(dialog, text="Task Title:", font=ctk.CTkFont(size=14))
        title_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        title_entry = ctk.CTkEntry(dialog, width=460, placeholder_text="Enter task title")
        title_entry.pack(pady=5, padx=20)
        if task:
            title_entry.insert(0, task.title)
        
        # Category
        category_label = ctk.CTkLabel(dialog, text="Category:", font=ctk.CTkFont(size=14))
        category_label.pack(pady=(15, 5), padx=20, anchor="w")
        
        category_var = ctk.StringVar(value=task.category if task else "Personal")
        category_combo = ctk.CTkComboBox(
            dialog,
            values=["Personal", "Work"],
            variable=category_var,
            width=460
        )
        category_combo.pack(pady=5, padx=20)
        
        # Priority
        priority_label = ctk.CTkLabel(dialog, text="Priority:", font=ctk.CTkFont(size=14))
        priority_label.pack(pady=(15, 5), padx=20, anchor="w")
        
        priority_var = ctk.StringVar(value=task.priority if task else "Medium")
        priority_combo = ctk.CTkComboBox(
            dialog,
            values=["Low", "Medium", "High"],
            variable=priority_var,
            width=460
        )
        priority_combo.pack(pady=5, padx=20)
        
        # Due date
        date_label = ctk.CTkLabel(dialog, text="Due Date (MM/DD/YYYY) - Optional:", font=ctk.CTkFont(size=14))
        date_label.pack(pady=(15, 5), padx=20, anchor="w")
        
        date_entry = ctk.CTkEntry(dialog, width=460, placeholder_text="MM/DD/YYYY (Leave empty if no due date)")
        date_entry.pack(pady=5, padx=20)
        if task and task.due_date:
            date_entry.insert(0, task.due_date)
        
        def save_task():
            title = title_entry.get().strip()
            category = category_var.get()
            priority = priority_var.get()
            due_date = date_entry.get().strip()
            
            if not title:
                messagebox.showerror("Error", "Please enter a task title")
                return
            
            # Validate date format only if date is provided
            if due_date:
                try:
                    datetime.strptime(due_date, "%m/%d/%Y")
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Use MM/DD/YYYY")
                    return
            
            if task:  # Update existing task
                task.title = title
                task.category = category
                task.priority = priority
                task.due_date = due_date
            else:  # Create new task
                new_task = Task(title, category, priority, due_date)
                self.tasks.append(new_task)
            
            self.save_tasks()
            self.display_tasks()
            dialog.destroy()
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=30)
        
        button_text = "Update Task" if task else "Save Task"
        save_btn = ctk.CTkButton(btn_frame, text=button_text, width=150, command=save_task)
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", width=150, 
                                   fg_color="gray", command=dialog.destroy)
        cancel_btn.pack(side="left", padx=10)
        
    def update_status_bar(self):
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.completed)
        pending = total - completed
        
        self.status_bar.configure(text=f"Total: {total} | Pending: {pending} | Completed: {completed}")
        
    def save_tasks(self):
        try:
            with open("tasks.txt", "w") as f:
                for task in self.tasks:
                    # Format: title|category|priority|due_date|completed|timestamp
                    line = f"{task.title}|{task.category}|{task.priority}|{task.due_date}|{task.completed}|{task.timestamp}\n"
                    f.write(line)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def load_tasks(self):
        if os.path.exists("tasks.txt"):
            try:
                with open("tasks.txt", "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if line:
                            parts = line.split("|")
                            if len(parts) == 6:
                                title, category, priority, due_date, completed, timestamp = parts
                                task = Task(
                                    title,
                                    category,
                                    priority,
                                    due_date,
                                    completed == "True",
                                    timestamp
                                )
                                self.tasks.append(task)
            except Exception as e:
                print(f"Error loading tasks: {e}")

if __name__ == "__main__":
    app = ToDoManager()
    app.mainloop()