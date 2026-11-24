from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from services.student_service import StudentService


student_bp = Blueprint("student", __name__)
service = StudentService()


def read_form():
    """Читает поля формы студента (включая новое поле phone)."""
    return (
        request.form.get("name", "").strip(),
        request.form.get("group", "").strip(),
        request.form.get("email", "").strip(),
        request.form.get("phone", "").strip(),
    )


@student_bp.route("/")
@student_bp.route("/students")
def students():
    student_list = service.get_all_students()

    return render_template(
        "students.html",
        students=student_list
    )


@student_bp.route("/add", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":
        name, group, email, phone = read_form()

        try:
            service.add_student(name, group, email, phone)
            flash(f"Student {name} added successfully!", "success")
            return redirect(url_for("student.students"))

        except ValueError as error:
            flash(str(error), "error")

    return render_template("add_student.html")


@student_bp.route(
    "/edit/<int:student_id>",
    methods=["GET", "POST"]
)
def edit_student(student_id):

    student = service.get_student_by_id(student_id)

    if student is None:
        abort(404)

    if request.method == "POST":
        name, group, email, phone = read_form()

        try:
            service.update_student(
                student_id, name, group, email, phone
            )

            flash(f"Student {name} updated successfully!", "success")
            return redirect(url_for("student.students"))

        except ValueError as error:
            flash(str(error), "error")

    return render_template(
        "edit_student.html",
        student=student
    )


@student_bp.route(
    "/delete/<int:student_id>",
    methods=["POST"]
)
def delete_student(student_id):

    student = service.get_student_by_id(student_id)

    if student is None:
        abort(404)

    service.delete_student(student_id)

    flash(f"Student {student.name} deleted successfully!", "success")

    return redirect(url_for("student.students"))
