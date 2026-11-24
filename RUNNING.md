# Как запускать проекты

**Нужно:** macOS / Linux, Python 3.10+ (`python3 --version`), браузер.
Порт 5000 не используется: на macOS его занимает AirPlay Receiver.

| Проект | Папка | Порт | Адрес |
|---|---|---|---|
| Lab 6 — Payment Aggregator | `lab06` | 5003 | http://127.0.0.1:5003 |
| Lab 7 — Smart Game Store | `lab07` | 5001 | http://127.0.0.1:5001 |
| РК 1 — Online Shop | `rk1` | 5002 | http://127.0.0.1:5002 |
| Lab 12 — Student Management | `lab12` | 5004 | http://127.0.0.1:5004 |
| Lab 13 — Attendance | `lab13` | — | файл `index.html` |
| GameHub — итоговый проект | `gamehub` | 5005 | http://127.0.0.1:5005 |

---

## 1. Запустить всё сразу

```bash
cd ~/Desktop/"Design Pattern"
./run_all.sh
```

Скрипт [`run_all.sh`](run_all.sh):

1. Сам создаёт `.venv` и ставит зависимости, если их ещё нет (только при первом запуске).
2. Запускает в фоне все 5 Flask-серверов.
3. Печатает таблицу «порт → статус → адрес».
4. Открывает все сайты и Lab 13 в браузере.

| Команда | Что делает |
|---|---|
| `./run_all.sh` | запустить всё (уже запущенные проекты пропускаются) |
| `./run_all.sh status` | показать, какие проекты работают |
| `./run_all.sh stop` | остановить все серверы |
| `NO_OPEN=1 ./run_all.sh` | запустить, но не открывать браузер |

Логи серверов лежат в `.run-logs/<папка>.log`. Если проект не поднялся, смотрите там.

> Серверы работают в фоне, даже если закрыть терминал. Не забудьте `./run_all.sh stop`.

---

## 2. Запустить один проект

Общая схема для любого Flask-проекта:

```bash
cd ~/Desktop/"Design Pattern/<папка проекта>"
python3 -m venv .venv                         # только в первый раз
.venv/bin/pip install -r requirements.txt     # только в первый раз
.venv/bin/python app.py
```

Остановить — `Ctrl + C` в том же терминале.

### Lab 6 — Payment Aggregator (Singleton + Factory Method)

```bash
cd ~/Desktop/"Design Pattern/lab06"
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # первый раз
.venv/bin/python app.py
```

http://127.0.0.1:5003. На главной странице есть форма для запросов к API. API: `POST /api/pay`, `GET /api/payments`, `GET /api/singleton-check`.

### Lab 7 — Smart Game Store (Facade + Proxy)

```bash
cd ~/Desktop/"Design Pattern/lab07"
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # первый раз
.venv/bin/python app.py
```

http://127.0.0.1:5001. Вход: `admin` / `admin123` (администратор), `student` / `student123` (покупатель).

### РК 1 — Online Shop (Decorator)

```bash
cd ~/Desktop/"Design Pattern/rk1"
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # первый раз
.venv/bin/python app.py
```

http://127.0.0.1:5002

### Lab 12 — Student Management (MVC + Repository)

```bash
cd ~/Desktop/"Design Pattern/lab12"
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # первый раз
.venv/bin/python app.py
```

http://127.0.0.1:5004

### Lab 13 — Attendance (Observer)

Сервер не нужен — просто откройте файл в браузере:

```bash
open ~/Desktop/"Design Pattern/lab13/index.html"
```

### GameHub — итоговый проект

```bash
cd ~/Desktop/"Design Pattern/gamehub"
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # первый раз
.venv/bin/python app.py
```

http://127.0.0.1:5005. Вход: `admin` / `admin123`, `student` / `student123` (можно зарегистрировать нового пользователя).

Тесты, покрытие и проверка безопасности (из папки `gamehub`):

```bash
.venv/bin/python -m unittest discover -s tests -t . -v
.venv/bin/coverage run --source=. --omit='.venv/*,tests/*,seed.py' -m unittest discover -s tests -t . && .venv/bin/coverage report
.venv/bin/bandit -r . -x ./.venv,./tests
```

---

## 3. Частые проблемы

| Ошибка | Что делать |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` | не поставлены зависимости: `.venv/bin/pip install -r requirements.txt` |
| `Address already in use` | порт уже занят (проект уже запущен): `./run_all.sh stop` или `lsof -ti tcp:<порт> \| xargs kill` |
| `bad interpreter` при запуске `.venv/bin/pip` | папку переименовали или перенесли: удалите `.venv` и создайте заново (`rm -rf .venv && python3 -m venv .venv`) |
| `permission denied: ./run_all.sh` | `chmod +x run_all.sh` |
| Страница показывает `{% ... %}` и `{{ ... }}` | открыт HTML-шаблон из `templates/` как файл. Нужно запустить сервер и открыть адрес `http://127.0.0.1:<порт>` |
| Хочу начать с чистой базой | остановить сервер и удалить файл БД (`gamehub.db`, `store.db`, `database.db`, `students.db` или `app_database.db`), при запуске он создастся заново (с демо-данными; в Lab 6 — пустой, история платежей начнётся с нуля) |
