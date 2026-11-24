import os
import sqlite3

# Путь к БД рядом с этим файлом — приложение работает из любой текущей папки.
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.db")

DEMO_STUDENTS = [
    ("Aigerim Nurlanova", "SE-2301", "aigerim.nurlanova@example.com", "+7 701 234 5678"),
    ("Daniyar Seitkali", "SE-2301", "daniyar.seitkali@example.com", "+7 702 345 6789"),
    ("Madina Omarova", "CS-2302", "madina.omarova@example.com", "+7 705 456 7890"),
    ("Arman Bekov", "CS-2302", "arman.bekov@example.com", "+7 707 567 8901"),
    ("Zhanna Tulegenova", "IT-2303", "zhanna.tulegenova@example.com", "+7 747 678 9012"),
]


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_group TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL DEFAULT ''
        )
    """)

    # Task 5: миграция старой базы — если колонки phone нет, добавляем её.
    columns = [row["name"] for row in connection.execute("PRAGMA table_info(students)")]
    if "phone" not in columns:
        connection.execute("ALTER TABLE students ADD COLUMN phone TEXT NOT NULL DEFAULT ''")

    # Task 2: демо-данные (5 студентов), только если таблица пустая.
    count = connection.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    if count == 0:
        connection.executemany(
            "INSERT INTO students (name, student_group, email, phone) VALUES (?, ?, ?, ?)",
            DEMO_STUDENTS,
        )

    connection.commit()
    connection.close()
