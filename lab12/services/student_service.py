import re

from repositories.student_repository import StudentRepository

PHONE_ALLOWED = re.compile(r"^\+?[\d\s\-()]+$")


class StudentService:
    """Service: бизнес-логика и проверка данных. SQL здесь нет."""

    def __init__(self, repository=None):
        self.repository = repository or StudentRepository()

    def get_all_students(self):
        return self.repository.get_all_students()

    def get_student_by_id(self, student_id):
        return self.repository.get_student_by_id(student_id)

    def validate_student(self, name, group, email, phone):
        if not name or not group or not email or not phone:
            raise ValueError("All fields are required.")

        if "@" not in email or "." not in email:
            raise ValueError("Please enter a valid email.")

        self.validate_phone(phone)

    def validate_phone(self, phone):
        if not PHONE_ALLOWED.match(phone):
            raise ValueError(
                "Phone number may contain only digits, spaces, dashes, "
                "brackets and a leading +."
            )

        digits = re.sub(r"\D", "", phone)
        if not 10 <= len(digits) <= 15:
            raise ValueError("Phone number must contain from 10 to 15 digits.")

    def add_student(self, name, group, email, phone):
        self.validate_student(name, group, email, phone)
        self.repository.add_student(name, group, email, phone)

    def update_student(self, student_id, name, group, email, phone):
        self.validate_student(name, group, email, phone)
        self.repository.update_student(
            student_id, name, group, email, phone
        )

    def delete_student(self, student_id):
        self.repository.delete_student(student_id)
