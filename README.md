# Design Patterns — лабораторные работы и итоговый проект

**Студент:** Alibi Auyespek · **Преподаватель:** Dina Aldanazarova
**Технологии:** Python 3, Flask, SQLite, HTML, CSS, JavaScript

---

## Содержание

| Папка | Задание | Паттерны | Технологии | Порт |
|---|---|---|---|---|
| [01-oop-basics](01-oop-basics/) | 4 принципа ООП (шпаргалка) | — | Python | — |
| [02-patterns-overview](02-patterns-overview/) | Обзор паттернов: порождающие, структурные, поведенческие | все группы GoF | Python | — |
| [lab06-singleton-factory-payments](lab06-singleton-factory-payments/) | **Lab 6** — Payment Aggregator API (вариант 2) | Singleton, Factory Method | Flask, SQLAlchemy, SQLite | 5003 |
| [lab07-facade-proxy-game-store](lab07-facade-proxy-game-store/) | **Lab 7** — Smart Game Store | Facade, Proxy | Flask, SQLite | 5001 |
| [rk1-decorator-online-shop](rk1-decorator-online-shop/) | **РК 1** — Online Shop Product Management | Decorator | Flask, SQLite | 5002 |
| [lab12-mvc-repository-students](lab12-mvc-repository-students/) | **Lab 12** — Student Management System | MVC / Layered, Repository | Flask, SQLite | 5004 |
| [lab13-observer-attendance](lab13-observer-attendance/) | **Lab 13** — Student Attendance System | Event-Driven, Observer | HTML, CSS, JavaScript | — (открыть `index.html`) |
| [final-project-gamehub](final-project-gamehub/) | **Итоговый проект** — GameHub, интернет-магазин игровой техники (команда из 3 человек) | Factory Method, Singleton, Adapter, Observer, Strategy, Repository | Flask, SQLite, unittest, Bandit | 5005 |

Другие папки:

| Папка | Что внутри |
|---|---|
| [assignments](assignments/) | PDF с условиями заданий |
| [reports](reports/) | Отчёты: OOP, Creational Patterns, Structural Patterns (`.docx` и `.pdf`) |

В каждой папке с проектом есть свой `README.md`. В нём описаны структура, запуск, объяснение паттерна, скриншоты и ответы на контрольные вопросы.

## Как запустить

📄 Подробная инструкция для каждого проекта и для всех сразу: **[RUNNING.md](RUNNING.md)**

Всё сразу (5 серверов + Lab 13 откроются в браузере):

```bash
./run_all.sh          # запустить
./run_all.sh status   # что работает
./run_all.sh stop     # остановить
```

Один Flask-проект:

```bash
cd ~/Desktop/"Design Pattern/<папка проекта>"
python3 -m venv .venv                         # только в первый раз
.venv/bin/pip install -r requirements.txt     # только в первый раз
.venv/bin/python app.py
```

Затем откройте `http://127.0.0.1:<порт>` (порт указан в таблице выше). Порт 5000 не используется: на macOS его занимает AirPlay Receiver.

## Задания (PDF) → решения

| Файл задания | Решение |
|---|---|
| [lab06-creational-patterns.pdf](assignments/lab06-creational-patterns.pdf) | [lab06-singleton-factory-payments](lab06-singleton-factory-payments/) |
| [lab07-structural-game-store.pdf](assignments/lab07-structural-game-store.pdf) | [lab07-facade-proxy-game-store](lab07-facade-proxy-game-store/) |
| [rk1-structural-patterns.pdf](assignments/rk1-structural-patterns.pdf) | [rk1-decorator-online-shop](rk1-decorator-online-shop/) |
| [lab12-mvc-repository.pdf](assignments/lab12-mvc-repository.pdf) | [lab12-mvc-repository-students](lab12-mvc-repository-students/) |
| [lab13-event-driven-observer.pdf](assignments/lab13-event-driven-observer.pdf) | [lab13-observer-attendance](lab13-observer-attendance/) |
| [Technical_Specification_GameHub.docx](final-project-gamehub/docs/Technical_Specification_GameHub.docx) | [final-project-gamehub](final-project-gamehub/) |
