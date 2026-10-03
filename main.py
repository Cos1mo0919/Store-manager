import json
import re
from datetime import datetime

import numpy as np
from numpy import random

FILENAME = "products.json"
sales_history = []


class Product:
    def __init__(self, name, category, price, stock):
        self.name = name
        self.category = category
        self.__price = price
        self.stock = stock

    def get_price(self):
        return self.__price

    def set_price(self, new_price):
        if new_price > 0:
            self.__price = new_price
        else:
            print("Price can't be < 0!!")

    def stock_value(self):
        return self.__price * self.stock

    def display(self):
        print(f"Products: {self.name} | {self.category} | {self.__price} | {self.stock}.")


class DiscountProduct(Product):
    def __init__(self, name, category, price, stock, discount):
        super().__init__(name, category, price, stock)
        self.discount = discount

    def discount_price(self):
        current_price = self.get_price()
        discount_amount = current_price * self.discount / 100
        return current_price - discount_amount

    def display(self):
        print(f"Products: {self.name} | {self.category} | {self.get_price()} | "
              f"{self.stock} | {self.discount} | {self.discount_price()}.")


products = [
    Product("Laptop", "electronics", 120, 15),
    Product("Mouse", "electronics", 70, 25),
    DiscountProduct("Keyboard", "electronics", 55, 35, 20),
    Product("Headphones", "electronics", 40, 30),
    Product("Chair", "furniture", 110, 10),
    DiscountProduct("Sofa", "furniture", 170, 12, 15),
    Product("Table", "furniture", 95, 35),
    Product("Wardrobe", "furniture", 200, 12),
]


def show_products():
    for product in products:
        product.display()


def add_product():
    name = input("Enter product name: ").strip()

    if not name:
        print("Name can't be empty")
        return

    for p in products:
        if p.name.lower() == name.lower():
            print("Product with this name already exists")
            return

    category = input("Enter product category: ")

    try:
        price = float(input("Enter product price: "))
        stock = int(input("Enter product stock: "))
    except ValueError:
        print("The price/stock should be number")
        return

    if price <= 0 or stock < 0:
        print("Price must be > 0 and stock can't be < 0")
        return

    has_discount = input("Does it have a discount? (y/n): ").lower()

    if has_discount == "y":
        try:
            discount = float(input("Enter discount in %: "))
        except ValueError:
            print("The discount should be number")
            return

        if not 0 <= discount <= 100:
            print("Discount must be between 0 and 100")
            return

        new_product = DiscountProduct(name, category, price, stock, discount)
    else:
        new_product = Product(name, category, price, stock)

    products.append(new_product)
    new_product.display()


def random_discount():
    return random.randint(1, 11)


def buy_product():
    name = input("Enter product name: ")

    product = None
    for p in products:
        if p.name.lower() == name.lower():
            product = p
            break

    if product is None:
        print("Product not found")
        return False

    quantity_input = input("Enter quantity: ")

    if not quantity_input.isdigit():
        print("Quantity must be a number")
        return False

    quantity = int(quantity_input)

    if quantity <= 0:
        print("Quantity must be greater than 0")
        return False

    if quantity > product.stock:
        print("Not enough stock")
        return False

    product.stock -= quantity

    if isinstance(product, DiscountProduct):
        unit_price = product.discount_price()
    else:
        unit_price = product.get_price()

    total = unit_price * quantity

    discount = random_discount()
    print(f"Random discount: {discount}%")
    print(f"Total before discount: {total:.2f}")

    total = round(float(total * (1 - discount / 100)), 2)

    date = datetime.now()

    sales_history.append({
        "name": product.name,
        "quantity": quantity,
        "total": total,
        "date": date
    })

    with open("sales_log.txt", "a", encoding="utf-8") as file:
        file.write(f"{date.strftime('%Y-%m-%d %H:%M')} | {product.name} | {quantity} | {total}\n")

    print(f"Purchase successful. Total after discount: {total}")
    return True


def find_product():
    name = input("Enter product name: ")

    for index, product in enumerate(products):
        if re.search(re.escape(name), product.name, re.IGNORECASE):
            product.display()
            print()

            next_products = iter(products[index + 1:])

            while True:
                print("1. Next product")
                print("2. Back")
                print()

                choice = input("Choose: ")

                if choice == "1":
                    try:
                        next_product = next(next_products)
                        next_product.display()
                        print()
                    except StopIteration:
                        print("There is no next product.")
                        print()

                elif choice == "2":
                    return

                else:
                    print("Invalid option")

    print("Nothing has found")


def show_sales_history():
    if not sales_history:
        print("No sales yet")
        return

    for sale in sales_history:
        print(f"{sale['date'].strftime('%Y-%m-%d %H:%M')} | "
              f"{sale['name']} | {sale['quantity']} | {sale['total']}")

    totals = np.array([sale["total"] for sale in sales_history])
    print("Total revenue:", round(float(np.sum(totals)), 2))


def save_products():
    data = []

    for product in products:
        item = {
            "name": product.name,
            "category": product.category,
            "price": product.get_price(),
            "stock": product.stock
        }

        if isinstance(product, DiscountProduct):
            item["discount"] = product.discount

        data.append(item)

    with open(FILENAME, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print("Products saved.")


def load_products():
    try:
        with open(FILENAME, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("File not found. Nothing to load yet.")
        return

    products.clear()

    for item in data:
        if "discount" in item:
            product = DiscountProduct(item["name"], item["category"],
                                      item["price"], item["stock"], item["discount"])
        else:
            product = Product(item["name"], item["category"],
                              item["price"], item["stock"])
        products.append(product)

    print("Products loaded.")


def price_label(price):
    if price < 60:
        return "cheap"
    elif price < 120:
        return "medium"
    return "expensive"


price_label_ufunc = np.frompyfunc(price_label, 1, 1)


def show_statistics():
    if not products:
        print("No products to analyze")
        return

    prices = np.array([p.get_price() for p in products])
    stocks = np.array([p.stock for p in products])
    names = np.array([p.name for p in products])
    discounts = np.array(
        [p.discount if isinstance(p, DiscountProduct) else 0 for p in products]
    )

    print("Average price:", np.mean(prices))
    print("Max price:", np.max(prices), "-", names[np.argmax(prices)])
    print("Min price:", np.min(prices), "-", names[np.argmin(prices)])
    print("Total stock:", np.sum(stocks))
    print()

    print("Sorted prices:", np.sort(prices))
    print()

    expensive_mask = prices > 100
    print("Prices above 100:", prices[expensive_mask])
    print("Expensive products:", names[expensive_mask])
    print()

    high_stock_idx = np.where(stocks > 20)[0]
    print("Indexes with stock > 20:", high_stock_idx)
    print("Products with stock > 20:", names[high_stock_idx])
    print()

    discount_factor = np.subtract(1, np.divide(discounts, 100))
    final_prices = np.multiply(prices, discount_factor)
    print("Prices with discount:", np.round(final_prices, 2))

    stock_values = np.multiply(prices, stocks)
    print("Stock value per product:", stock_values)
    print("Total stock value:", np.add.reduce(stock_values))
    print()

    print("Price labels:", price_label_ufunc(prices))
    print()

    print("Price differences:", np.diff(prices))
    print("Cumulative stock:", np.cumsum(stocks))


def main():
    load_products()

    while True:
        print()
        print("1. Show products")
        print("2. Add product")
        print("3. Find product")
        print("4. Buy product")
        print("5. Statistics")
        print("6. Sales history")
        print("7. Save and exit")
        print()

        choice = input("Choose: ")

        if choice == "1":
            show_products()
        elif choice == "2":
            add_product()
        elif choice == "3":
            find_product()
        elif choice == "4":
            buy_product()
        elif choice == "5":
            show_statistics()
        elif choice == "6":
            show_sales_history()
        elif choice == "7":
            save_products()
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()
