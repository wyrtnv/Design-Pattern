# Design Patterns — лабораторные работы и итоговый проект

**Студент:** Alibi Auyespek · **Преподаватель:** Dina Aldanazarova
**Технологии:** Python 3, Flask, SQLite, HTML, CSS, JavaScript

---

## Содержание

| Папка | Задание | Паттерны | Технологии | Порт |
|---|---|---|---|---|
| [oop](oop/) | 4 принципа ООП (шпаргалка) | — | Python | — |
| [patterns](patterns/) | Обзор паттернов: порождающие, структурные, поведенческие | все группы GoF | Python | — |
| [lab06](lab06/) | **Lab 6** — Payment Aggregator API (вариант 2) | Singleton, Factory Method | Flask, SQLAlchemy, SQLite | 5003 |
| [lab07](lab07/) | **Lab 7** — Smart Game Store | Facade, Proxy | Flask, SQLite | 5001 |
| [rk1](rk1/) | **РК 1** — Online Shop Product Management | Decorator | Flask, SQLite | 5002 |
| [lab12](lab12/) | **Lab 12** — Student Management System | MVC / Layered, Repository | Flask, SQLite | 5004 |
| [lab13](lab13/) | **Lab 13** — Student Attendance System | Event-Driven, Observer | HTML, CSS, JavaScript | — (открыть `index.html`) |
| [gamehub](gamehub/) | **Итоговый проект** — GameHub, интернет-магазин игровой техники (команда из 3 человек) | Factory Method, Singleton, Adapter, Observer, Strategy, Repository | Flask, SQLite, unittest, Bandit | 5005 |

Другие папки:

| Папка | Что внутри |
|---|---|
| [tasks](tasks/) | PDF с условиями заданий |
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
| [lab06.pdf](tasks/lab06.pdf) | [lab06](lab06/) |
| [lab07.pdf](tasks/lab07.pdf) | [lab07](lab07/) |
| [rk1.pdf](tasks/rk1.pdf) | [rk1](rk1/) |
| [lab12.pdf](tasks/lab12.pdf) | [lab12](lab12/) |
| [lab13.pdf](tasks/lab13.pdf) | [lab13](lab13/) |
| [spec.docx](gamehub/docs/spec.docx) | [gamehub](gamehub/) |
