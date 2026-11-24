class Student:
    """Model: доменный объект «студент»."""

    def __init__(self, id, name, group, email, phone=""):
        self.id = id
        self.name = name
        self.group = group
        self.email = email
        self.phone = phone

    @classmethod
    def from_row(cls, row):
        """Превращает строку SQLite (sqlite3.Row) в объект Student."""
        if row is None:
            return None
        keys = row.keys()
        return cls(
            id=row["id"],
            name=row["name"],
            group=row["student_group"],
            email=row["email"],
            phone=row["phone"] if "phone" in keys else "",
        )

    @property
    def student_group(self):
        # Совместимость с исходными шаблонами из задания (student.student_group).
        return self.group

    def __repr__(self):
        return f"Student(id={self.id!r}, name={self.name!r}, group={self.group!r})"
