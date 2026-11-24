#!/usr/bin/env bash
# Запуск всех проектов курса Design Patterns одной командой.
#
#   ./run_all.sh            запустить все Flask-проекты (и открыть их в браузере)
#   ./run_all.sh stop       остановить все
#   ./run_all.sh status     показать, что запущено
#
# При первом запуске скрипт сам создаёт .venv в каждой папке и ставит зависимости.
# Логи серверов пишутся в .run-logs/<папка>.log

set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$ROOT/.run-logs"

# папка | порт | название
PROJECTS=(
  "lab07-facade-proxy-game-store|5001|Lab 7 — Smart Game Store (Facade + Proxy)"
  "rk1-decorator-online-shop|5002|РК 1 — Online Shop (Decorator)"
  "lab06-singleton-factory-payments|5003|Lab 6 — Payment Aggregator (Singleton + Factory Method)"
  "lab12-mvc-repository-students|5004|Lab 12 — Student Management (MVC + Repository)"
  "final-project-gamehub|5005|GameHub — итоговый проект"
)
STATIC_PAGE="$ROOT/lab13-observer-attendance/index.html"

port_pids() { lsof -ti tcp:"$1" -sTCP:LISTEN 2>/dev/null; }

status() {
  printf "\nПорт   Статус    Проект\n"
  for entry in "${PROJECTS[@]}"; do
    IFS="|" read -r dir port title <<<"$entry"
    if [ -n "$(port_pids "$port")" ]; then state="работает"; else state="  стоп  "; fi
    printf "%s   %s  %s  →  http://127.0.0.1:%s\n" "$port" "$state" "$title" "$port"
  done
  echo "       (статика) Lab 13 — Attendance (Observer)  →  open \"$STATIC_PAGE\""
  echo
}

stop_all() {
  for entry in "${PROJECTS[@]}"; do
    IFS="|" read -r dir port title <<<"$entry"
    pids="$(port_pids "$port")"
    if [ -n "$pids" ]; then
      kill $pids 2>/dev/null && echo "Остановлен: $title (порт $port)"
    fi
  done
}

start_all() {
  mkdir -p "$LOG_DIR"
  for entry in "${PROJECTS[@]}"; do
    IFS="|" read -r dir port title <<<"$entry"
    path="$ROOT/$dir"
    if [ -n "$(port_pids "$port")" ]; then
      echo "Уже работает: $title (порт $port)"
      continue
    fi
    if [ ! -x "$path/.venv/bin/python" ]; then
      echo "Создаю окружение для $dir ..."
      python3 -m venv "$path/.venv" || { echo "  ошибка: не удалось создать .venv"; continue; }
    fi
    check="import flask"
    [ "$dir" = "lab06-singleton-factory-payments" ] && check="import flask, flask_sqlalchemy"
    if ! "$path/.venv/bin/python" -c "$check" 2>/dev/null; then
      echo "Ставлю зависимости для $dir ..."
      "$path/.venv/bin/pip" install -q -r "$path/requirements.txt" || { echo "  ошибка установки"; continue; }
    fi
    (cd "$path" && nohup .venv/bin/python app.py >"$LOG_DIR/$dir.log" 2>&1 &)
    echo "Запускаю: $title (порт $port)"
  done

  # ждём, пока серверы поднимутся (до ~15 секунд)
  for _ in $(seq 1 30); do
    all_up=1
    for entry in "${PROJECTS[@]}"; do
      IFS="|" read -r dir port title <<<"$entry"
      [ -z "$(port_pids "$port")" ] && all_up=0
    done
    [ "$all_up" = 1 ] && break
    sleep 0.5
  done

  status
  if [ "${NO_OPEN:-0}" != "1" ] && command -v open >/dev/null; then
    for entry in "${PROJECTS[@]}"; do
      IFS="|" read -r dir port title <<<"$entry"
      [ -n "$(port_pids "$port")" ] && open "http://127.0.0.1:$port"
    done
    open "$STATIC_PAGE"
  fi
  echo "Остановить всё:  ./run_all.sh stop"
}

case "${1:-start}" in
  start)  start_all ;;
  stop)   stop_all ;;
  status) status ;;
  *) echo "Использование: ./run_all.sh [start|stop|status]"; exit 1 ;;
esac
