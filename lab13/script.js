// =====================================================================
// Lab 13 — Student Attendance System
// Event-Driven Architecture + Observer Design Pattern
// Parts A, B, C, D, E are placed in ONE file in exactly this order.
// =====================================================================


// =====================================================================
// PART A. SUBJECT: AttendanceManager
// Stores student data and notifies observers when something changes.
// =====================================================================
class AttendanceManager {
    constructor() {
        this.students = [];
        this.observers = [];
        this.nextId = 1;
    }

    // Register an observer
    subscribe(observer) {
        this.observers.push(observer);
    }

    // EXTENSION: remove an observer (it stops receiving events)
    unsubscribe(observer) {
        this.observers = this.observers.filter(o => o !== observer);
    }

    // Notify all observers
    notify(event) {
        this.observers.forEach(observer => {
            observer.update(this.students, event);
        });
    }

    // Add a student
    addStudent(name) {
        const student = {
            id: this.nextId++,
            name: name,
            status: "Pending"
        };

        this.students.push(student);

        this.notify({
            type: "studentAdded",
            message: name + " was added"
        });
    }

    // Change attendance status
    markAttendance(id, status) {
        const student = this.students.find(
            s => s.id === id
        );

        if (student) {
            student.status = status;

            this.notify({
                type: "attendanceChanged",
                message: student.name + " is " + status
            });
        }
    }

    // Delete a student
    deleteStudent(id) {
        const student = this.students.find(
            s => s.id === id
        );

        if (!student) return;

        this.students = this.students.filter(
            s => s.id !== id
        );

        this.notify({
            type: "studentDeleted",
            message: student.name + " was deleted"
        });
    }
}


// =====================================================================
// PART B. OBSERVER 1: StatisticsDisplay
// Recalculates Total / Present / Absent counters on every update.
// =====================================================================
class StatisticsDisplay {
    update(students, event) {
        const total = students.length;

        const present = students.filter(
            s => s.status === "Present"
        ).length;

        const absent = students.filter(
            s => s.status === "Absent"
        ).length;

        document.getElementById("totalCount")
            .textContent = total;

        document.getElementById("presentCount")
            .textContent = present;

        document.getElementById("absentCount")
            .textContent = absent;
    }
}


// =====================================================================
// PART C. OBSERVER 2: NotificationDisplay
// Shows a message about the event; the message fades out after ~3 s.
// =====================================================================
class NotificationDisplay {
    constructor() {
        this.hideTimer = null;
        this.removeTimer = null;
    }

    update(students, event) {
        const notification =
            document.getElementById("notification");

        notification.textContent = event.message;
        notification.style.display = "block";

        // colour depends on the kind of event
        notification.className = "type-" + event.type;
        if (event.type === "attendanceChanged" && / is Absent$/.test(event.message)) {
            notification.className = "type-absent";
        }

        // fade out after ~3 seconds (restart the timer on every new event)
        clearTimeout(this.hideTimer);
        clearTimeout(this.removeTimer);
        this.hideTimer = setTimeout(() => {
            notification.classList.add("fade-out");
            this.removeTimer = setTimeout(() => {
                notification.style.display = "none";
            }, 600);
        }, 3000);

        console.log(
            "Event received:",
            event.type,
            event.message
        );
    }
}


// =====================================================================
// PART D. OBSERVER 3: StudentListDisplay
// Redraws the student list and creates the Present/Absent/Delete buttons.
// =====================================================================
class StudentListDisplay {
    update(students, event) {
        const list =
            document.getElementById("studentList");

        list.innerHTML = ""; // only clears the list, no user data here

        if (students.length === 0) {
            const empty = document.createElement("p");
            empty.className = "empty";
            empty.textContent = "No students yet. Add the first one above.";
            list.appendChild(empty);
            return;
        }

        students.forEach(student => {
            const row = document.createElement("div");
            row.className = "student is-" + student.status.toLowerCase();

            const info = document.createElement("div");
            info.className = "student-info";

            const name = document.createElement("strong");
            name.textContent = student.name; // textContent: name is text, not HTML

            const status = document.createElement("span");
            status.className =
                "status-badge status-" + student.status.toLowerCase();
            status.textContent = "Status: " + student.status;

            info.appendChild(name);
            info.appendChild(status);

            const actions = document.createElement("div");
            actions.className = "student-actions";

            const presentBtn =
                document.createElement("button");
            presentBtn.textContent = "Present";
            presentBtn.className = "present";
            if (student.status === "Present") presentBtn.classList.add("active");
            presentBtn.addEventListener("click", () => {
                attendanceManager.markAttendance(
                    student.id, "Present"
                );
            });

            const absentBtn =
                document.createElement("button");
            absentBtn.textContent = "Absent";
            absentBtn.className = "absent";
            if (student.status === "Absent") absentBtn.classList.add("active");
            absentBtn.addEventListener("click", () => {
                attendanceManager.markAttendance(
                    student.id, "Absent"
                );
            });

            const deleteBtn =
                document.createElement("button");
            deleteBtn.textContent = "Delete";
            deleteBtn.className = "delete";
            deleteBtn.addEventListener("click", () => {
                attendanceManager.deleteStudent(student.id);
            });

            actions.appendChild(presentBtn);
            actions.appendChild(absentBtn);
            actions.appendChild(deleteBtn);

            row.appendChild(info);
            row.appendChild(actions);

            list.appendChild(row);
        });
    }
}


// =====================================================================
// EXTENSION. OBSERVER 4: EventLogDisplay
// Not part of the original assignment. Shows that a NEW observer can be
// added without modifying AttendanceManager (control question 10):
// it only implements update(students, event) and is subscribed below.
// =====================================================================
class EventLogDisplay {
    constructor() {
        this.count = 0;
    }

    update(students, event) {
        const log = document.getElementById("eventLog");

        if (!event) { // initial display: no event yet
            log.innerHTML = "";
            const empty = document.createElement("li");
            empty.className = "log-empty";
            empty.textContent = "No events yet";
            log.appendChild(empty);
            return;
        }

        const placeholder = log.querySelector(".log-empty");
        if (placeholder) placeholder.remove();

        this.count++;

        const item = document.createElement("li");

        const time = document.createElement("span");
        time.className = "log-time";
        time.textContent = "#" + this.count + " " +
            new Date().toLocaleTimeString("en-GB");

        const type = document.createElement("span");
        type.className = "log-type";
        type.textContent = event.type;

        const message = document.createElement("span");
        message.textContent = event.message +
            "  (students: " + students.length + ")";

        item.appendChild(time);
        item.appendChild(type);
        item.appendChild(message);

        log.prepend(item); // newest event on top
    }
}


// =====================================================================
// PART E. CONNECT THE SUBJECT AND OBSERVERS
// =====================================================================

// CREATE THE SUBJECT
const attendanceManager = new AttendanceManager();

// CREATE OBSERVERS
const statisticsObserver = new StatisticsDisplay();
const notificationObserver = new NotificationDisplay();
const studentListObserver = new StudentListDisplay();

// SUBSCRIBE OBSERVERS
attendanceManager.subscribe(statisticsObserver);
attendanceManager.subscribe(notificationObserver);
attendanceManager.subscribe(studentListObserver);

// EXTENSION: one more observer — AttendanceManager is NOT modified
const eventLogObserver = new EventLogDisplay();
attendanceManager.subscribe(eventLogObserver);

// HANDLE ADD STUDENT EVENT
document.getElementById("addStudentBtn")
    .addEventListener("click", () => {
        const input =
            document.getElementById("studentName");

        const name = input.value.trim();

        if (name === "") {
            // NOTE: in the PDF `return;` stands before alert(), so the alert
            // never shows. Here the alert comes first, then return.
            alert("Please enter a student name");
            return;
        }

        attendanceManager.addStudent(name);

        input.value = "";
        input.focus();
    });

// ADD STUDENT USING ENTER KEY
document.getElementById("studentName")
    .addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            document.getElementById("addStudentBtn")
                .click();
        }
    });

// INITIAL DISPLAY
statisticsObserver.update(
    attendanceManager.students, null
);

studentListObserver.update(
    attendanceManager.students, null
);

eventLogObserver.update(
    attendanceManager.students, null
);
