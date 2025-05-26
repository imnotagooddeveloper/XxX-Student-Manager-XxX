import tkinter as tk
from tkinter import messagebox
import sqlite3

def init_db():
    connection = sqlite3.connect("veri.db")
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Students (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID2 TEXT,
            Name TEXT,
            Surname TEXT,
            Gender TEXT,
            GradeClass TEXT,
            Note TEXT,
            StudentNumber TEXT,
            DateOfBirth TEXT,
            MomName TEXT,
            MomSurname TEXT,
            MomPhone TEXT,
            DadName TEXT,
            DadSurname TEXT,
            DadPhone TEXT,
            HomeAddress TEXT
        )
    ''')
    connection.commit()
    return connection, cursor

def add_or_update_student(connection, cursor, data, student_id=None):
    try:
        if student_id:
            cursor.execute('''
                UPDATE Students SET
                ID2=?, Name=?, Surname=?, Gender=?, GradeClass=?, Note=?,
                StudentNumber=?, DateOfBirth=?, MomName=?, MomSurname=?, MomPhone=?,
                DadName=?, DadSurname=?, DadPhone=?, HomeAddress=?
                WHERE ID=?
            ''', data + (student_id,))
        else:
            cursor.execute('''
                INSERT INTO Students (
                    ID2, Name, Surname, Gender, GradeClass, Note,
                    StudentNumber, DateOfBirth, MomName, MomSurname, MomPhone,
                    DadName, DadSurname, DadPhone, HomeAddress
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
        connection.commit()
        messagebox.showinfo("Yippiee I did it!")
    except Exception as e:
        messagebox.showerror("Oops,", f"Something bad happened :c : {e}")

def student_form_window(connection, cursor, existing_data=None):
    def submit():
        values = [entry.get() for entry in entries]
        add_or_update_student(connection, cursor, tuple(values), existing_data[0] if existing_data else None)
        form_win.destroy()
        refresh()

    labels = [
        "ID2", "Name", "Surname", "Gender", "Grade/Class", "Note", "Student Phone Number", "DOB",
        "Mommy Name", "Mommy Surname", "Mommy Phone", "Daddy Name", "Daddy Surname", "Daddy Phone", "Address"
    ]

    form_win = tk.Toplevel()
    form_win.title("Student Entry")

    entries = []
    for i, label in enumerate(labels):
        tk.Label(form_win, text=label).grid(row=i, column=0, sticky='e', padx=5, pady=2)
        entry = tk.Entry(form_win, width=30)
        entry.grid(row=i, column=1, padx=5, pady=2)
        if existing_data:
            entry.insert(0, existing_data[i+1])
        entries.append(entry)

    tk.Button(form_win, text="Save", command=submit).grid(row=len(labels), columnspan=2, pady=10)

def delete_student(connection, cursor, student_id):
    if messagebox.askyesno("Sure?", "Really delete this student?"):
        try:
            cursor.execute("DELETE FROM Students WHERE ID=?", (student_id,))
            connection.commit()
            refresh()
        except Exception as e:
            messagebox.showerror("Hata", f"Silinemedi: {e}")

def show_students_list(frame, records, connection, cursor):
    for widget in frame.winfo_children():
        widget.destroy()

    headers = [
        "ID", "ID2", "Name", "Surname", "Gender", "Grade/Class", "Note", "Phone", "DOB",
        "Mom Name", "Mom Surname", "Mom Phone", "Dad Name", "Dad Surname", "Dad Phone", "Address", "Edit", "Delete"
    ]

    for col, header in enumerate(headers):
        tk.Label(frame, text=header, bg='lightgrey', anchor='center', relief='ridge').grid(
            row=0, column=col, sticky="nsew", padx=1, pady=1
        )

    for idx, row in enumerate(records, start=1):
        for col in range(len(row)):
            val = row[col] if row[col] is not None else ""
            tk.Label(frame, text=val, anchor='center', relief='groove').grid(
                row=idx, column=col, sticky="nsew", padx=1, pady=1
            )

        tk.Label(frame, text=row[0], anchor='center', relief='groove').grid(row=idx, column=0, sticky="nsew")
        tk.Button(frame, text="Edit", command=lambda r=row: student_form_window(connection, cursor, r)).grid(
            row=idx, column=16, sticky="nsew"
        )
        tk.Button(frame, text="Delete", command=lambda r=row: delete_student(connection, cursor, r[0])).grid(
            row=idx, column=17, sticky="nsew"
        )

    for col in range(len(headers)):
        frame.grid_columnconfigure(col, weight=1)
    for row in range(len(records) + 1):
        frame.grid_rowconfigure(row, weight=1)

def filter_students_window(connection, cursor, list_frame):
    def apply_filter():
        filters = [entry.get() for entry in entries]
        columns = ["ID2", "Name", "Surname", "Gender", "GradeClass", "Note", "StudentNumber", "DateOfBirth", "MomName",
                   "MomSurname", "MomPhone", "DadName", "DadSurname", "DadPhone", "HomeAddress"]
        query = "SELECT * FROM Students WHERE 1=1"
        params = []
        for val, col in zip(filters, columns):
            if val:
                query += f" AND {col} LIKE ?"
                params.append(f"%{val}%")

        cursor.execute(query, tuple(params))
        records = cursor.fetchall()
        show_students_list(list_frame, records, connection, cursor)
        filter_win.destroy()

    labels = [
        "ID2", "Name", "Surname", "Gender", "Grade/Class", "Note", "Phone", "DOB",
        "Mom Name", "Mom Surname", "Mom Phone", "Dad Name", "Dad Surname", "Dad Phone", "Address"
    ]

    filter_win = tk.Toplevel()
    filter_win.title("Filter Students")

    entries = []
    for i, label in enumerate(labels):
        tk.Label(filter_win, text=label).grid(row=i, column=0, padx=4, pady=2, sticky="e")
        entry = tk.Entry(filter_win, width=25)
        entry.grid(row=i, column=1, padx=4, pady=2)
        entries.append(entry)

    tk.Button(filter_win, text="Filter", command=apply_filter).grid(row=len(labels), columnspan=2, pady=10)

def main_window():
    global refresh
    connection, cursor = init_db()

    window = tk.Tk()
    window.title("Student Management Thingy.")

    window.rowconfigure(1, weight=1)
    window.columnconfigure(0, weight=1)

    top_frame = tk.Frame(window)
    top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
    top_frame.columnconfigure([0, 1, 2], weight=1)

    list_frame = tk.Frame(window)
    list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

    def _refresh():
        cursor.execute("SELECT * FROM Students")
        records = cursor.fetchall()
        show_students_list(list_frame, records, connection, cursor)

    refresh = _refresh
    _refresh()

    tk.Button(top_frame, text="Add", command=lambda: student_form_window(connection, cursor), bg="#4caf50", fg="white").grid(row=0, column=0, padx=5)
    tk.Button(top_frame, text="Refresh", command=_refresh, bg="#2196f3", fg="white").grid(row=0, column=1, padx=5)
    tk.Button(top_frame, text="Filter", command=lambda: filter_students_window(connection, cursor, list_frame), bg="#ff9800", fg="white").grid(row=0, column=2, padx=5)

    window.mainloop()

if __name__ == "__main__":
    main_window()
