import json
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from time import localtime, strftime
from tkinter import messagebox
from typing import Callable
from datetime import datetime

from PIL import Image, ImageTk

# Important directory
assets = Path(__file__).resolve().parent / "assets"

# This will serve as our database
ORDERS = {}

# This is the item price reference
ITEMS_UNIT_PRICE = json.loads(
    (assets / "unit_price.json").read_text(encoding="utf-8")
)


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
        self.profile = tk.Label(self.frame, image=self.profile_img,
                                text="Jethro Arciaga", compound=tk.BOTTOM)
        self.profile.image = self.profile_img
        self.profile.grid(row=0, column=0)

        self.time_label = tk.Label(self.frame)
        self.time_label.grid(row=1, column=0, sticky="ew")


@dataclass
class ProductWidget:
    master: tk.Tk
    order_details_widget: "OrderDetailsWidget"

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
            # Update ProductTable
            self.order_details_widget.create_table(ORDERS)
            # Update Total Amount
            self.order_details_widget.update_total_amount(ORDERS)

        update_config(
            "asian_glow_kojic_avocado.jpg",
            "P100\nAsian Glow Kojic Avocado",
            lambda: add_orders("Kojic Avocado", 100)
        )
        kojic_avocado = ImageButton(**button_config)
        kojic_avocado.grid_layout(0, 1)

        update_config(
            "asian_glow_serum.jpg",
            "P360\nAsian Glow Serum",
            lambda: add_orders("Asian Glow Serum", 360)
        )
        serum = ImageButton(**button_config)
        serum.grid_layout(1, 1)

        update_config(
            "asian_glow_set.jpg",
            "P288\nAsian Glow Ultimate Set",
            lambda: add_orders("Ultimate Set", 288)
        )
        serum = ImageButton(**button_config)
        serum.grid_layout(2, 1)

        update_config(
            "asian_glow_sunscreen.jpg",
            "P160\nAsian Glow Premium Sunscreen",
            lambda: add_orders("Premium Sunscreen", 160)
        )
        sunscreen = ImageButton(**button_config)
        sunscreen.grid_layout(0, 2)

        update_config(
            "asian_glow_toner.jpg",
            "P120\nAsian Glow Toner",
            lambda: add_orders("Asian Glow Toner", 120)
        )
        toner = ImageButton(**button_config)
        toner.grid_layout(1, 2)


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
class OrderDetailsWidget:
    master: tk.Tk

    def __post_init__(self):
        self.frame = tk.Frame(self.master, bd=1)
        self.frame.grid(row=0, column=3, sticky="ns")
        self.create_table(ORDERS)
        self.generate_widget()

    def receipt_window(self):
        if len(ORDERS) < 1:
            messagebox.showerror("Receipt Error", "Nothing to generate.")
            return

        receipt_window = tk.Toplevel(self.frame)
        receipt_window.title("Receipt")
        receipt_window.grab_set()

        current_date = datetime.now()
        headers = tk.Label(receipt_window, text=f"Asian Glow Skin Care\n{current_date}", bg="white")
        headers.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.create_table(ORDERS, receipt=True, headers=False, frame=receipt_window)

    def modify_transaction_window(self):
        temp_order = ORDERS.copy()

        def refresh_window():
            selection = product_listbox.curselection()
            product_listbox.delete(0, "end")
            for item in temp_order:
                product_listbox.insert(tk.END, f"{item} \t|\t QTY: {ORDERS[item]["quantity"]}")
            if selection:
                product_listbox.selection_set(selection[0])

        def confirm_changes(orders):
            global ORDERS
            for order in orders.copy():
                if orders[order]["quantity"] == 0:
                    del orders[order]

            ORDERS = orders
            modify_window.destroy()
            self.create_table(ORDERS)
            self.update_total_amount(ORDERS)

        def add_item(orders):
            selection = product_listbox.curselection()
            if len(selection) == 0:
                messagebox.showerror("Selection Error.", "Please select an item to modify.")

            if selection:
                index = selection[0]
                selected_item = product_listbox.get(index)
                key = selected_item.split("|")[0].strip()
                unit_price = ITEMS_UNIT_PRICE[key]
                orders[key]["quantity"] += 1
                orders[key]["price"] = unit_price * orders[key]["quantity"]
            refresh_window()

        def subtract_item(orders):
            selection = product_listbox.curselection()
            if len(selection) == 0:
                messagebox.showerror("Selection Error.", "Please select an item to modify.")

            if selection:
                index = selection[0]
                selected_item = product_listbox.get(index)
                key = selected_item.split("|")[0].strip()
                if orders[key]["quantity"] == 0:
                    messagebox.showerror("Error", "If quantity is 0 the product will be \
                                         deleted from the transaction.")
                else:
                    unit_price = ITEMS_UNIT_PRICE[key]
                    orders[key]["quantity"] -= 1
                    orders[key]["price"] = unit_price * orders[key]["quantity"]
            refresh_window()

        modify_window = tk.Toplevel(self.frame)
        modify_window.title("Edit transaction window")
        modify_window.grab_set()

        product_listbox = tk.Listbox(modify_window, selectmode=tk.SINGLE, width=40)
        product_listbox.grid(row=0, column=0, padx=5, pady=5, columnspan=3)

        subtract_button = tk.Button(
            modify_window,
            text="-",
            width=4,
            height=1,
            font=("Helvetica", 20),
            command=lambda: subtract_item(temp_order)
            )
        subtract_button.grid(row=1, column=0, pady=3)

        add_button = tk.Button(
            modify_window,
            text="+",
            width=4,
            height=1,
            font=("Helvetica", 20),
            command=lambda: add_item(temp_order)
            )
        add_button.grid(row=1, column=1, pady=3)

        confirm_button = tk.Button(
            modify_window,
            text="✓",
            width=4,
            height=1,
            font=("Helvetica", 20),
            fg="green",
            command=lambda: confirm_changes(temp_order)
            )
        confirm_button.grid(row=1, column=2, pady=3)
        refresh_window()

    def generate_widget(self):
        label = tk.Label(self.frame, text="Transaction Details")
        label.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.total_amount_label = tk.Label(self.frame, text="Total: ")
        self.total_amount_label.grid(row=2, column=0, sticky="nw")

        edit_transaction = tk.Button(self.frame, text="Edit transaction",
                                     command=self.modify_transaction_window,
                                     height=3)
        edit_transaction.grid(row=2, column=1, padx=1, pady=4, sticky="ne")

        receipt_button = tk.Button(self.frame, text="Generate Receipt", height=3, command=self.receipt_window)
        receipt_button.grid(row=2, column=2, padx=1, pady=4)

    def update_total_amount(self, products):
        total_price = sum(product['price'] for product in products.values())
        self.total_amount_label.config(text=f"Total: {total_price}")
        return total_price

    def create_table(self, products, receipt=False, headers=True, frame=None):
        start = 1
        if frame is None:
            frame = self.frame
        if not headers:
            start = 2
        table_frame = tk.Frame(frame, bg="white", bd=1)
        table_frame.grid(row=1, column=0, columnspan=3)
        canvas = tk.Canvas(table_frame, bg="white")
        scrollbar = tk.Scrollbar(
            table_frame,
            orient="vertical",
            command=canvas.yview,
            bg="white"
        )
        scrollable_frame = tk.Frame(canvas, bg="white")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), anchor="nw", window=scrollable_frame)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=1, column=0, columnspan=3)
        scrollbar.grid(column=4, row=1, sticky="ns")

        # Create table headers
        if headers:
            headers = ["Product", "Quantity", "Price"]
            for i, header in enumerate(headers):
                label = tk.Label(table_frame, text=header, relief=tk.RIDGE, width=17)
                label.grid(row=0, column=i)

        # Populate products
        for i, product in enumerate(products.values(), start=start):
            label_product = tk.Label(scrollable_frame, text=product["name"], width=17, bg="white")
            label_product.grid(row=i, column=0)

            label_quantity = tk.Label(scrollable_frame, text=str(product["quantity"]),
                                      bg="white", width=17)
            label_quantity.grid(row=i, column=1)

            label_price = tk.Label(scrollable_frame, text=str(product["price"]),
                                   bg="white", width=17)
            label_price.grid(row=i, column=2)

        if receipt:
            grand_total = self.update_total_amount(ORDERS)
            total_amount = tk.Label(scrollable_frame, text=f"Total: {grand_total}", bg="white", bd=1, font=("Helvetica", 13))
            total_amount.grid(row=i+1, column=2)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Asian Glow")
    ProfileWidget(root)
    order_details_widget = OrderDetailsWidget(root)
    ProductWidget(root, order_details_widget)
    root.mainloop()
