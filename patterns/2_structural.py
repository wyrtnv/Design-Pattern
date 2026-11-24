# Структурные паттерны
# Они отвечают за то, как объекты соединяются между собой
# В этом файле 7 примеров: Адаптер, Мост, Компоновщик, Декоратор, Фасад, Приспособленец, Заместитель


# Адаптер
# Старая система принимает тиыны, а мы хотим платить в тенге
class OldPayment:
    def pay_tiyn(self, tiyn):
        return f"Оплачено {tiyn} тиын"


class PaymentAdapter:
    def __init__(self, old):
        self.old = old

    def pay(self, tenge):
        return self.old.pay_tiyn(tenge * 100)


# Мост
# Пульт и устройство отдельно, любой пульт работает с любым устройством
class TV:
    def set_volume(self, v):
        return f"Телевизор, громкость {v}"


class Radio:
    def set_volume(self, v):
        return f"Радио, громкость {v}"


class Remote:
    def __init__(self, device):
        self.device = device

    def mute(self):
        return self.device.set_volume(0)


# Компоновщик
# У товара и у коробки с товарами одинаковый метод price
class Product:
    def __init__(self, price):
        self.p = price

    def price(self):
        return self.p


class Box:
    def __init__(self, items):
        self.items = items

    def price(self):
        total = 0
        for item in self.items:
            total += item.price()
        return total


# Декоратор
# Оборачиваем кофе и добавляем к нему что-то новое
class Coffee:
    def cost(self):
        return 800


class Milk:
    def __init__(self, drink):
        self.drink = drink

    def cost(self):
        return self.drink.cost() + 200


# Фасад
# Один метод вместо вызова трёх разных классов
class Warehouse:
    def reserve(self):
        return "товар зарезервирован"


class Payment:
    def charge(self):
        return "деньги списаны"


class Courier:
    def send(self):
        return "курьер выехал"


class OrderFacade:
    def order(self):
        return [Warehouse().reserve(), Payment().charge(), Courier().send()]


# Приспособленец
# Одинаковые данные храним один раз и переиспользуем
class TreeFactory:
    types = {}

    def get(self, name):
        if name not in self.types:
            self.types[name] = {"name": name, "texture": "тяжёлая картинка"}
        return self.types[name]


# Заместитель
# Проверяем права, прежде чем пустить к базе данных
class Database:
    def query(self, sql):
        return f"Выполнено: {sql}"


class DatabaseProxy:
    def __init__(self, role):
        self.role = role
        self.db = Database()

    def query(self, sql):
        if self.role != "admin":
            return "Нет доступа"
        return self.db.query(sql)


# Проверяем все примеры
print("Адаптер:", PaymentAdapter(OldPayment()).pay(50))
print("Мост:", Remote(TV()).mute(), "|", Remote(Radio()).mute())
print("Компоновщик:", Box(
    [Product(100), Box([Product(50), Product(30)])]).price())
print("Декоратор:", Milk(Milk(Coffee())).cost())
print("Фасад:", OrderFacade().order())

factory = TreeFactory()
trees = [factory.get("Берёза") for i in range(1000)]
print("Приспособленец: деревьев", len(trees), "типов", len(factory.types))

print("Заместитель:", DatabaseProxy("user").query(
    "DELETE"), "|", DatabaseProxy("admin").query("DELETE"))
