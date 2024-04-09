import tkinter as tk
from PIL import Image, ImageTk
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List
from time import localtime, strftime
import functools


ORDERS = {"Asian Glow": {"name": "Asian Glow Set", "quantity": 1, "price": 288}}

@dataclass
class ProfileWidget:
    master: tk.Tk

    def __post_init__(self):
        self.frame = tk.Frame(self.master, bd=1, bg="gray")
        self.frame.grid(column=0, row=0, sticky="ns")
        self.generate_widget()
        self.update_time()

    def update_time(self):
        current_time = strftime('%A, %d %B %Y\n %I:%M:%S %p', localtime())
        self.time_label.config(text=current_time)
        self.time_label.grid(column=0, row=2)
        self.frame.after(1000, self.update_time)

    def _load_image(self, filename):
        img_dir = Path(__file__).resolve().parent / "img"
        self.profile_img = ImageTk.PhotoImage(Image.open(img_dir / filename).resize((200, 200)))


    def generate_widget(self):
        self._load_image("Profile.jpg")
        self.profile = tk.Label(self.frame, image=self.profile_img, text="Jethro Arciaga", compound=tk.BOTTOM)
        self.profile.image = self.profile_img
        self.profile.grid(row=0, column=0)

        self.time_label = tk.Label(self.frame)
        self.time_label.grid(row=1, column=0, sticky="ew")


@dataclass
class ProductWidget:
    master: tk.Tk

    def __post_init__(self):
        self.frame = tk.Frame(self.master, bd=1)
        self.frame.grid(column=1, row=0)
        self.generate_widget()

    @staticmethod
    def _load_image(filename):
        images = Path(__file__).resolve().parent / "img"
        return images / filename

    def generate_widget(self):
        self.title = tk.Label(self.frame, text="Available Products")
        self.title.grid(column=1, row=0, padx=5, pady=5)

        button_config = {
            "frame": self.frame,
            "img": "",
            "command": lambda: print("x"),
            "product": "unnamed"
        }

        def update_config(img: str, product: str, command=(lambda: print("x"))):
            nonlocal button_config


            button_config.update({
                "img": self._load_image(img),
                "product": product,
                "command": command
            })

        def add_orders(name, price):
            if name not in ORDERS:
                ORDERS.update({name: {"name": name, "quantity": 1, "price": price}})
            else:
                ORDERS[name]["quantity"] += 1
                ORDERS[name]["price"] = ORDERS[name]["quantity"] * price
            print(ORDERS)



        update_config(
            "asian_glow_kojic_avocado.jpg",
            "P100\nAsian Glow Kojic Avocado",
            lambda: add_orders("Asian Glow Kojic Avocado", 288)
        )
        kojic_avocado = ImageButton(**button_config)
        print(kojic_avocado)
        kojic_avocado.grid_layout(0,1)

        update_config(
            "asian_glow_serum.jpg",
            "P360\nAsian Glow Serum",
            lambda: add_orders("Asian Glow Serum", 360)
        )
        serum = ImageButton(**button_config)
        serum.grid_layout(1,1)

        update_config("asian_glow_set.jpg", "P288\nAsian Glow Ultimate Set")
        serum = ImageButton(**button_config)
        serum.grid_layout(2,1)

        update_config("asian_glow_sunscreen.jpg", "P160\nAsian Premium Sunscreen")
        sunscreen = ImageButton(**button_config)
        sunscreen.grid_layout(0,2)

        update_config("asian_glow_toner.jpg", "P120\nAsian Glow Toner")
        sunscreen = ImageButton(**button_config)
        sunscreen.grid_layout(1,2)



@dataclass
class ImageButton:
    frame: tk.Frame
    img: Path
    command: Callable
    product: str  # Product name w/ price

    def __post_init__(self):
        self.image = ImageTk.PhotoImage(Image.open(self.img).resize((200, 200)))
        self.button = tk.Button(
            self.frame,
            image=self.image,
            text=self.product,
            compound=tk.TOP,
            command=self.command
        )
        self.button.image = self.image

    def grid_layout(self, col, row):
        self.button.grid(column=col, row=row, padx=5, pady=5)


@dataclass
class ProductTable:
    frame: tk.Frame
    products: List[dict]

    def __post_init__(self):
        self.table_frame = tk.Frame(self.frame, bg="white", bd=1)
        self.canvas = tk.Canvas(self.table_frame, bg="white")
        self.scrollbar = tk.Scrollbar(
            self.table_frame,
            orient="vertical",
            command=self.canvas.yview,
            bg="white"
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), anchor="nw", window=self.scrollable_frame)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.table_frame.grid(column=0, row=1)
        self.canvas.grid(row=1, column=0, columnspan=3)
        self.scrollbar.grid(column=4, row=1, sticky="ns")
        self.create_table()

    def create_table(self):
        # Create table headers
        headers = ["Product", "Quantity", "Price"]
        for i, header in enumerate(headers):
            label = tk.Label(self.table_frame, text=header, relief=tk.RIDGE, width=17)
            label.grid(row=0, column=i)

        # Populate products
        for i, product in enumerate(self.products, 1):
            print("HERE", product)
            label_product = tk.Label(self.scrollable_frame, text=self.products[product]["name"], width=17, bg="white")
            label_product.grid(row=i, column=0)

            label_quantity = tk.Label(self.scrollable_frame, text=str(self.products[product]["quantity"]), bg="white", width=17)
            label_quantity.grid(row=i, column=1)

            label_price = tk.Label(self.scrollable_frame, text=str(self.products[product]["price"]), bg="white", width=17)
            label_price.grid(row=i, column=2)



        # for i, product in enumerate(self.products, 1):
        #     label_product = tk.Label(self.scrollable_frame, text=product["name"], width=17, bg="white")
        #     label_product.grid(row=i, column=0)

        #     label_quantity = tk.Label(self.scrollable_frame, text=str(product["quantity"]), bg="white", width=17)
        #     label_quantity.grid(row=i, column=1)

        #     label_price = tk.Label(self.scrollable_frame, text=str(product["price"]), bg="white", width=17)
        #     label_price.grid(row=i, column=2)


@dataclass
class OrderDetailsWidget:
    master: tk.Tk

    def __post_init__(self):
        self.frame = tk.Frame(self.master, bd=1)
        self.frame.grid(row=0, column=3, sticky="ns")
        self.generate_widget()


    def generate_widget(self):
        label = tk.Label(self.frame, text="Order Details")
        label.grid(row=0, column=0, sticky="ew")
        # test_data = [
        #     {"name": "Asian Glow Set", "quantity": 1, "price": 288},
        #     {"name": "Asian Glow Serum", "quantity": 2, "price": 360},
        #     {"name": "Asian Glow Serum", "quantity": 2, "price": 360},
        #     {"name": "Asian Glow Serum", "quantity": 2, "price": 360},
        #     {"name": "Asian Glow Serum", "quantity": 2, "price": 360},
        #     {"name": "Asian Glow Serum", "quantity": 2, "price": 360},
        #     {"name": "Asian Glow Serum", "quantity": 2, "price": 360},
        #     {"name": "Asian Glow Serum", "quantity": 2, "price": 360},
        #     {"name": "Asian Glow Serum", "quantity": 2, "price": 360},
        #     {"name": "Asian Glow Serum", "quantity": 2, "price": 360},
        #     {"name": "Asian Glow Serum", "quantity": 2, "price": 360},
        #     {"name": "Asian Glow Serum", "quantity": 2, "price": 360},
        #     {"name": "Asian Glow Serum", "quantity": 2, "price": 360},
        #     {"name": "Asian Glow Sunscreen", "quantity": 1, "price": 160}
        # ]
        ProductTable(self.frame, ORDERS)

        total_amount = tk.Label(self.frame, text=f"Total: ")
        total_amount.grid(row=2, column=0)




if __name__ == "__main__":
    root = tk.Tk()
    ProfileWidget(root)
    ProductWidget(root)
    OrderDetailsWidget(root)

    root.mainloop()

