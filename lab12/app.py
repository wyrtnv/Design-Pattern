from flask import Flask, render_template

from database import create_database
from controllers.student_controller import student_bp


app = Flask(__name__)

app.secret_key = "beginner-project-secret-key"

app.register_blueprint(student_bp)

create_database()


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    # Порт 5004: 5000 на macOS занят AirPlay, 5001–5003 — другие лабораторные.
    app.run(debug=True, port=5004)
