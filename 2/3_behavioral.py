# Поведенческие паттерны
# Они отвечают за то, как объекты общаются и делят работу
# В этом файле 11 примеров: Цепочка обязанностей, Команда, Интерпретатор, Итератор, Посредник,
# Хранитель, Наблюдатель, Состояние, Стратегия, Шаблонный метод, Посетитель


# Цепочка обязанностей
# Запрос передаётся дальше, пока кто-то не сможет его обработать
class Manager:
    def __init__(self, boss):
        self.boss = boss

    def approve(self, amount):
        if amount <= 10000:
            return "Одобрил менеджер"
        return self.boss.approve(amount)


class Director:
    def approve(self, amount):
        if amount <= 100000:
            return "Одобрил директор"
        return "Отказ"


# Команда
# Действие хранится как объект, поэтому его можно отменить
class AddText:
    def __init__(self, editor, text):
        self.editor = editor
        self.text = text

    def do(self):
        self.editor.append(self.text)

    def undo(self):
        self.editor.pop()


# Интерпретатор
# Каждое правило языка это отдельный класс, выражение считается само
class Num:
    def __init__(self, n):
        self.n = n

    def calc(self):
        return self.n


class Plus:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def calc(self):
        return self.a.calc() + self.b.calc()


# Итератор
# Перебираем элементы по одному через next
class Playlist:
    def __init__(self, songs):
        self.songs = songs
        self.i = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.i >= len(self.songs):
            raise StopIteration
        self.i += 1
        return self.songs[self.i - 1]


# Посредник
# Пользователи пишут не друг другу, а через чат
class Chat:
    def __init__(self):
        self.users = []

    def send(self, sender, msg):
        for user in self.users:
            if user != sender:
                print(f"Посредник: {user} <- {sender}: {msg}")


# Хранитель
# Сохраняем состояние игры и потом возвращаем его
class Game:
    def __init__(self):
        self.level = 1

    def save(self):
        return {"level": self.level}

    def load(self, saved):
        self.level = saved["level"]


# Наблюдатель
# Все подписчики получают уведомление о новом видео
class Channel:
    def __init__(self):
        self.subscribers = []

    def upload(self, video):
        for sub in self.subscribers:
            print(f"Наблюдатель: {sub} узнал(а) о видео {video}")


# Состояние
# Заказ ведёт себя по-разному в зависимости от статуса
class Order:
    def __init__(self):
        self.state = "новый"

    def next(self):
        if self.state == "новый":
            self.state = "оплачен"
        elif self.state == "оплачен":
            self.state = "доставлен"
        return self.state


# Стратегия
# Способ расчёта скидки можно подменить
class NoDiscount:
    def apply(self, price):
        return price


class StudentDiscount:
    def apply(self, price):
        return price * 0.8


# Шаблонный метод
# Порядок шагов задан в родителе, дети меняют только один шаг
class Exporter:
    def export(self):
        data = ["Алия", "Ерлан"]
        return self.format(data)


class CsvExporter(Exporter):
    def format(self, data):
        return ",".join(data)


class TextExporter(Exporter):
    def format(self, data):
        return " и ".join(data)


# Посетитель
# Новая операция (площадь) вынесена в отдельный класс, фигуры не меняем
class Circle:
    def __init__(self, r):
        self.r = r

    def accept(self, visitor):
        return visitor.circle(self)


class Square:
    def __init__(self, a):
        self.a = a

    def accept(self, visitor):
        return visitor.square(self)


class AreaVisitor:
    def circle(self, c):
        return 3.14 * c.r * c.r

    def square(self, s):
        return s.a * s.a


# Проверяем все примеры
manager = Manager(Director())
print("Цепочка:", manager.approve(5000), "|",
      manager.approve(50000), "|", manager.approve(500000))

editor = []
cmd = AddText(editor, "Привет")
cmd.do()
print("Команда: после ввода", editor)
cmd.undo()
print("Команда: после отмены", editor)

print("Интерпретатор: 2 + 3 + 4 =", Plus(Num(2), Plus(Num(3), Num(4))).calc())

for song in Playlist(["Песня 1", "Песня 2"]):
    print("Итератор:", song)

chat = Chat()
chat.users = ["Али", "Дана", "Тимур"]
chat.send("Али", "Привет всем")

game = Game()
saved = game.save()
game.level = 5
game.load(saved)
print("Хранитель: уровень после загрузки", game.level)

channel = Channel()
channel.subscribers = ["Подписчик 1", "Подписчик 2"]
channel.upload("Паттерны")

order = Order()
print("Состояние:", order.next(), "->", order.next())

print("Стратегия:", NoDiscount().apply(1000),
      "|", StudentDiscount().apply(1000))
print("Шаблонный метод:", CsvExporter().export(), "|", TextExporter().export())

visitor = AreaVisitor()
print("Посетитель:", Circle(2).accept(visitor), "|", Square(3).accept(visitor))
