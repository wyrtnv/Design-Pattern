# Порождающие паттерны
# Они отвечают за создание объектов
# В этом файле 5 примеров: Одиночка, Фабричный метод, Абстрактная фабрика, Строитель, Прототип

import copy


# Одиночка
# Класс всегда возвращает один и тот же объект
class Config:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance


# Фабричный метод
# Каждый класс доставки сам решает, какой транспорт создать
class Truck:
    def deliver(self):
        return "Везём грузовиком"


class Ship:
    def deliver(self):
        return "Везём кораблём"


class RoadDelivery:
    def create_transport(self):
        return Truck()


class SeaDelivery:
    def create_transport(self):
        return Ship()


# Абстрактная фабрика
# Фабрика создаёт сразу набор похожих объектов (кнопка и текст одной темы)
class LightTheme:
    def button(self):
        return "Светлая кнопка"

    def text(self):
        return "Светлый текст"


class DarkTheme:
    def button(self):
        return "Тёмная кнопка"

    def text(self):
        return "Тёмный текст"


# Строитель
# Собираем объект по шагам
class PizzaBuilder:
    def __init__(self):
        self.size = 0
        self.toppings = []

    def set_size(self, size):
        self.size = size
        return self

    def add(self, topping):
        self.toppings.append(topping)
        return self

    def build(self):
        return f"Пицца {self.size} см: {', '.join(self.toppings)}"


# Прототип
# Создаём новый объект копированием старого
class Document:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages

    def clone(self):
        return copy.deepcopy(self)


# Проверяем Одиночку: оба объекта одинаковые
a = Config()
b = Config()
print("Одиночка:", a is b)

# Проверяем Фабричный метод
print("Фабричный метод:", RoadDelivery().create_transport().deliver())
print("Фабричный метод:", SeaDelivery().create_transport().deliver())

# Проверяем Абстрактную фабрику
for theme in [LightTheme(), DarkTheme()]:
    print("Абстрактная фабрика:", theme.button(), "и", theme.text())

# Проверяем Строителя
print("Строитель:", PizzaBuilder().set_size(
    30).add("сыр").add("грибы").build())

# Проверяем Прототип: копию меняем, оригинал остаётся прежним
doc = Document("Договор", ["Стр. 1"])
doc2 = doc.clone()
doc2.pages.append("Стр. 2")
print("Прототип:", doc.pages, doc2.pages)
