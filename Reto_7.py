import json
from collections import deque, namedtuple
from typing import List, Dict, Any

MenuItemTuple = namedtuple('MenuItemTuple', ['name', 'price', 'type', 'details'])

class MenuItem:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def calculate_total_price(self, quantity: int = 1) -> float:
        return self.price * quantity

    def __str__(self):
        return f"{self.name} - ${self.price:.2f}"


class Beverage(MenuItem):
    def __init__(self, name: str, price: float, size: str):
        super().__init__(name, price)
        self.size = size

    def __str__(self):
        return f"{self.name} - ${self.price:.2f} ({self.size})"


class Appetizer(MenuItem):
    def __init__(self, name: str, price: float, portion_size: str):
        super().__init__(name, price)
        self.portion_size = portion_size

    def __str__(self):
        return f"{self.name} - ${self.price:.2f} ({self.portion_size})"


class MainCourse(MenuItem):
    def __init__(self, name: str, price: float):
        super().__init__(name, price)

    def __str__(self):
        return f"{self.name} - ${self.price:.2f}"


class Order:
    def __init__(self):
        self.items = []

    def add_item(self, item: MenuItem, quantity: int = 1):
        self.items.append((item, quantity))

    def calculate_total(self) -> float:
        total = 0
        has_maincourse = any(isinstance(item, MainCourse) for item, _ in self.items)
        for item, quantity in self.items:
            if has_maincourse and isinstance(item, Beverage):
                total += item.calculate_total_price(quantity) * 0.9  
            else:
                total += item.calculate_total_price(quantity)
        return total

    def print_order(self):
        print("Detalles del pedido:")
        for item, quantity in self.items:
            print(f"{quantity}x {item}")
        print(f"Total: ${self.calculate_total():.2f}")

    def save_menu(self, menu: List[MenuItem], filename: str):
        menu_data = []
        for item in menu:
            if isinstance(item, Beverage):
                menu_data.append(MenuItemTuple(item.name, item.price, "Beverage", {"size": item.size})._asdict())
            elif isinstance(item, Appetizer):
                menu_data.append(MenuItemTuple(item.name, item.price, "Appetizer", {"portion_size": item.portion_size})._asdict())
            elif isinstance(item, MainCourse):
                menu_data.append(MenuItemTuple(item.name, item.price, "MainCourse", {})._asdict())
        with open(filename, 'w') as f:
            json.dump(menu_data, f, indent=4)

    def load_menu(self, filename: str) -> List[MenuItem]:
        with open(filename, 'r') as f:
            menu_data = json.load(f)
        menu = []
        for item_data in menu_data:
            if item_data['type'] == "Beverage":
                menu.append(Beverage(item_data['name'], item_data['price'], item_data['details']['size']))
            elif item_data['type'] == "Appetizer":
                menu.append(Appetizer(item_data['name'], item_data['price'], item_data['details']['portion_size']))
            elif item_data['type'] == "MainCourse":
                menu.append(MainCourse(item_data['name'], item_data['price']))
        return menu

class Payment:
    def __init__(self, order: Order):
        self.order = order
        self.amount_paid = 0.0

    def process_payment(self, amount: float, method: str):
        total = self.order.calculate_total()
        if amount < total:
            print(f"El monto pagado es menor que el total del pedido. Faltan ${total - amount:.2f}.")
            return False

        self.amount_paid = amount
        print(f"Pago de ${amount:.2f} procesado con éxito mediante {method}.")
        return True

    def print_receipt(self):
        print("Recibo de Pago:")
        self.order.print_order()
        print(f"Monto pagado: ${self.amount_paid:.2f}")
        if self.amount_paid > self.order.calculate_total():
            change = self.amount_paid - self.order.calculate_total()
            print(f"Cambio: ${change:.2f}")
        elif self.amount_paid < self.order.calculate_total():
            print("Pago incompleto.")
        else:
            print("Pago exacto.")

class Restaurant:
    def __init__(self):
        self.orders = deque()

    def add_order(self, order: Order):
        self.orders.append(order)

    def process_next_order(self):
        if self.orders:
            order = self.orders.popleft()
            order.print_order()
            return order
        else:
            print("No hay pedidos en la cola.")
            return None

menu = [
    Beverage("Coke", 2.5, "Large"),
    Beverage("Fanta", 2.5, "Medium"),
    Beverage("Water", 1.0, "Small"),
    Appetizer("Spring Rolls", 5.0, "Medium"),
    Appetizer("Garlic Bread", 4.0, "4 pieces"),
    MainCourse("Spaghetti", 12.0),
    MainCourse("Steak", 20.0),
    MainCourse("Salmon", 18.0),
    MainCourse("Vegetarian Pasta", 10.0),
    Beverage("Orange Juice", 3.0, "Medium"),
    Appetizer("Bruschetta", 6.0, "6 pieces"),
    Beverage("Tea", 1.5, "Small")
]
#EJEMPLO DE USO
if __name__ == "__main__":
    order = Order()
    order.save_menu(menu, "menu.json")

    loaded_menu = order.load_menu("menu.json")
    print("Menú cargado desde JSON:")
    for item in loaded_menu:
        print(item)

    restaurant = Restaurant()

    order1 = Order()
    order1.add_item(Beverage("Coke", 2.5, "Large"), quantity=2)
    order1.add_item(Appetizer("Spring Rolls", 5.0, "Medium"), quantity=1)
    order1.add_item(MainCourse("Spaghetti", 12.0), quantity=1)
    restaurant.add_order(order1)
    processed_order = restaurant.process_next_order()
    if processed_order:
        payment = Payment(processed_order)
        payment.process_payment(30.0, "Tarjeta de crédito")
        payment.print_receipt()