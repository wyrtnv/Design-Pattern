from abc import ABC, abstractmethod

# 1. АБСТРАКЦИЯ - скрываем сложность, оставляем только нужные методы


class Vehicle(ABC):
    def __init__(self, brand, speed):
        # 2. ИНКАПСУЛЯЦИЯ - данные защищены (приватные через _)
        self._brand = brand
        self._speed = speed

    def get_info(self):
        return f"{self._brand}, скорость: {self._speed} км/ч"

    @abstractmethod
    def move(self):
        pass


# 3. НАСЛЕДОВАНИЕ - Bike наследует от Vehicle
class Bike(Vehicle):
    def __init__(self, brand, speed):
        super().__init__(brand, speed)

    # 4. ПОЛИМОРФИЗМ - свой вариант метода move()
    def move(self):
        return f"{self._brand} едет, крутя педали 🚲"


class Car(Vehicle):
    def __init__(self, brand, speed):
        super().__init__(brand, speed)

    # 4. ПОЛИМОРФИЗМ - другой вариант move() для машины
    def move(self):
        return f"{self._brand} едет на двигателе"


# Проверяем работу
vehicles = [Bike("Trek", 25), Car("Toyota", 180)]

for v in vehicles:
    print(v.get_info())
    print(v.move())
    print()
