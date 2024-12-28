import tkinter as tk
from tkinter import font
import sqlite3

root = tk.Tk()
root.title("To Do List App")
root.geometry("300x400")
root.configure(bg="#f0f0f0")

custom_font = font.Font(family="Comic Sans MS", size=16, weight="bold", slant="italic")

connection = sqlite3.connect("list.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS lists (
    id INTEGER PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMP,
    status TEXT
);
""")
connection.commit()

def clear_tasks():
    cursor.execute("DELETE FROM lists;")
    connection.commit()

current_editing_task_id = None

def load_tasks():
    global current_editing_task_id
    current_editing_task_id = None
    text_widget.config(state=tk.NORMAL)
    text_widget.delete(1.0, tk.END)
    cursor.execute("SELECT id, title FROM lists WHERE status='scheduled'")
    tasks = cursor.fetchall()
    for task in tasks:
        text_widget.insert(tk.END, f"{task[0]}: {task[1]}\n")
    text_widget.config(state=tk.DISABLED)

def add_task(entry):
    title = entry.get()
    if title:
        cursor.execute("INSERT INTO lists (title, created_at, status) VALUES (?, datetime('now'), ?)",
                       (title, 'scheduled'))
        connection.commit()
        load_tasks()
        entry.delete(0, tk.END)

def delete_task():
    try:
        sel_start, sel_end = text_widget.tag_ranges("sel")
        if sel_start and sel_end:
            selected_line = text_widget.get(sel_start, sel_end).strip()
            task_id = selected_line.split(":")[0]
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(sel_start, sel_end)
            text_widget.config(state=tk.DISABLED)
            cursor.execute("DELETE FROM lists WHERE id=?", (task_id,))
            connection.commit()
            load_tasks()
    except Exception as e:
        print(f"Error deleting task: {e}")

def mark_done():
    try:
        sel_start, sel_end = text_widget.tag_ranges("sel")
        if sel_start and sel_end:
            selected_text = text_widget.get(sel_start, sel_end).strip()
            checkmark = '✓ '
            updated_text = checkmark + selected_text.split(": ", 1)[1]
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(sel_start, sel_end)
            text_widget.insert(sel_start, updated_text)
            text_widget.config(state=tk.DISABLED)
            cursor.execute("UPDATE lists SET status='committed' WHERE title=?", (selected_text.split(": ")[1],))
            connection.commit()
        else:
            print("No task selected.")
    except Exception as e:
        print(f"Error marking task as done: {e}")

def edit_task():
    try:
        sel_start, sel_end = text_widget.tag_ranges("sel")
        if sel_start and sel_end:
            selected_text = text_widget.get(sel_start, sel_end).strip()
            global current_editing_task_id
            current_editing_task_id = selected_text.split(":")[0]
            receiver.delete(0, tk.END)
            receiver.insert(0, selected_text.split(": ", 1)[1])
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(sel_start, sel_end)
            text_widget.config(state=tk.DISABLED)
        else:
            print("No task selected for editing.")
    except Exception as e:
        print(f"Error editing task: {e}")

def update_task():
    try:
        new_title = receiver.get().strip()
        if new_title and current_editing_task_id:
            cursor.execute("UPDATE lists SET title=? WHERE id=?", (new_title, current_editing_task_id))
            connection.commit()
            load_tasks()
            receiver.delete(0, tk.END)
        else:
            print("No new title provided or no task being edited.")
    except Exception as e:
        print(f"Error updating task: {e}")

input_frame = tk.Frame(root, bg="#f0f0f0")
input_frame.pack(pady=10)
receiver = tk.Entry(input_frame, width=50, font=custom_font)
receiver.pack(padx=5, pady=5)

button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=5)

add_button = tk.Button(button_frame, text="Add", command=lambda: add_task(receiver), bg="#4CAF50", fg="white",
                       font=custom_font)
add_button.pack(side=tk.LEFT, padx=5)

delete_button = tk.Button(button_frame, text="Delete", bg="#F44336", fg="white", font=custom_font,
                          command=delete_task)
delete_button.pack(side=tk.LEFT, padx=5)

done_button = tk.Button(button_frame, text="Done", command=mark_done, bg="#2196F3", fg="white", font=custom_font)
done_button.pack(side=tk.LEFT, padx=5)

edit_button = tk.Button(button_frame, text="Edit", command=edit_task, bg="#FF9800", fg="white", font=custom_font)
edit_button.pack(side=tk.LEFT, padx=5)

update_button = tk.Button(button_frame, text="Update", command=update_task, bg="#FF5722", fg="white",
                          font=custom_font)
update_button.pack(side=tk.LEFT, padx=5)

text_widget = tk.Text(root, width=40, height=10, font=custom_font, bg="#ffffff", fg="#000000")
text_widget.pack(padx=5)
text_widget.config(state=tk.DISABLED)


load_tasks()

root.mainloop()

connection.close()
