from database import get_connection
from models.student import Student


class StudentRepository:
    """Repository: единственное место, где есть SQL для таблицы students."""

    def get_all_students(self):
        connection = get_connection()

        rows = connection.execute(
            "SELECT * FROM students ORDER BY id"
        ).fetchall()

        connection.close()
        return [Student.from_row(row) for row in rows]

    def get_student_by_id(self, student_id):
        connection = get_connection()

        row = connection.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

        connection.close()
        return Student.from_row(row)

    def add_student(self, name, group, email, phone):
        connection = get_connection()

        connection.execute(
            """
            INSERT INTO students
            (name, student_group, email, phone)
            VALUES (?, ?, ?, ?)
            """,
            (name, group, email, phone)
        )

        connection.commit()
        connection.close()

    def update_student(self, student_id, name, group, email, phone):
        connection = get_connection()

        connection.execute(
            """
            UPDATE students
            SET name = ?, student_group = ?, email = ?, phone = ?
            WHERE id = ?
            """,
            (name, group, email, phone, student_id)
        )

        connection.commit()
        connection.close()

    def delete_student(self, student_id):
        connection = get_connection()

        connection.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )

        connection.commit()
        connection.close()
