from decimal import Decimal
import tkinter as tk
from tkinter import messagebox, ttk

from models.service import AppError, PENDING, integer
from ui.common import DataTable, ScrollFrame, center_window, display, report_error, money, notify, search_text
from ui.payment_dialog import PaymentDialog
from ui.theme import COLORS

class OrderEditor(tk.Toplevel):
    def __init__(self, parent, service, on_change, order_id=None, table_id=None):
        order, lines = service.get_order(order_id) if order_id else ({}, [])
        tables, customers, products = service.order_options()
        super().__init__(parent)
        self.service, self.on_change = service, on_change
        self.order_id, self.order = order_id, order
        self.editable = not order_id or order["TrangThai"] == PENDING
        self.dirty = False
        self.cart = {line["MaSP"]: {"MaSP": line["MaSP"], "TenSP": line["TenSPLucBan"],
                     "SoLuong": line["SoLuong"], "DonGia": line["DonGia"]} for line in lines}
        self.products = {p["MaSP"]: p for p in products}
        self.title(f"Coffee - Đơn #{order_id}" if order_id else "Coffee - Gọi món")
        width, height = min(1200, self.winfo_screenwidth() - 60), min(780, self.winfo_screenheight() - 85)
        self.minsize(min(1050, width), min(660, height))
        self.transient(parent.winfo_toplevel())
        center_window(self, width, height)
        self.configure(background=COLORS["background"])
        body = ttk.Frame(self, padding=18)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(2, weight=1)
        heading = ttk.Frame(body)
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        title_text = f"Đơn #{order_id}" if order_id else "Gọi món mới"
        ttk.Label(heading, text=title_text, style="Title.TLabel").pack(side="left")
        status_text = order.get("TrangThai", "Chưa lưu")
        ttk.Label(heading, text=status_text, style="Subtitle.TLabel").pack(side="right")
        self.table_options = {f"{t['TenBan']} - {t['KhuVuc']}": t["MaBan"] for t in tables
            if not self.editable or t["TrangThai"] == "Trống" or t["MaBan"] == order.get("MaBan")}
        self.customer_options = {"Khách lẻ": None}
        self.customer_options.update({f"{c['MaKH']} - {c['HoTen']} ({c['SDT'] or 'chưa có SĐT'})": c["MaKH"] for c in customers})
        chosen_table = order.get("MaBan", table_id)
        self.table_var = tk.StringVar(self, next((k for k, v in self.table_options.items() if v == chosen_table), ""))
        self.customer_var = tk.StringVar(self, next((k for k, v in self.customer_options.items() if v == order.get("MaKH")), "Khách lẻ"))
        self.initial_table, self.initial_customer = self.table_var.get(), self.customer_var.get()
        info = ttk.Frame(body, padding=14, style="Panel.TFrame")
        info.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        info.columnconfigure(1, weight=1)
        info.columnconfigure(3, weight=1)
        ttk.Label(info, text="Bàn *", style="Card.TLabel").grid(row=0, column=0, padx=(0, 12))
        state = "readonly" if self.editable else "disabled"
        ttk.Combobox(info, textvariable=self.table_var, values=list(self.table_options), state=state, width=26, style="Card.TCombobox").grid(row=0, column=1, sticky="ew")
        ttk.Label(info, text="Khách hàng", style="Card.TLabel").grid(row=0, column=2, padx=15)
        ttk.Combobox(info, textvariable=self.customer_var, values=list(self.customer_options), state=state, width=26, style="Card.TCombobox").grid(row=0, column=3, sticky="ew")
        panes = ttk.Frame(body)
        panes.grid(row=2, column=0, sticky="nsew")
        panes.rowconfigure(0, weight=1)
        panes.columnconfigure(0, weight=1, uniform="panes")
        panes.columnconfigure(1, weight=1, uniform="panes")
        menu = ttk.Frame(panes, padding=(0, 0, 18, 0))
        menu.grid(row=0, column=0, sticky="nsew")
        menu.columnconfigure(0, weight=1)
        menu.rowconfigure(2, weight=1)
        ttk.Label(menu, text="Thực đơn", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 12))
        filters = ttk.Frame(menu)
        filters.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        filters.columnconfigure(1, weight=1)
        self.category = tk.StringVar(self, "Tất cả món")
        category_box = ttk.Combobox(filters, textvariable=self.category, values=["Tất cả món"] + sorted({p["DanhMuc"] for p in products}), state="readonly", width=13)
        category_box.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        category_box.bind("<<ComboboxSelected>>", lambda event: self.render_menu())
        self.search = tk.StringVar(self)
        search_frame = ttk.Frame(filters)
        search_frame.grid(row=0, column=1, sticky="ew")
        ttk.Label(search_frame, text="Tìm: ").pack(side="left")
        search_box = ttk.Entry(search_frame, textvariable=self.search, width=17)
        search_box.pack(side="left", fill="x", expand=True)
        ttk.Label(menu, text="Tìm món theo tên (có thể gõ không dấu)", style="Subtitle.TLabel").grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.menu_cards = ScrollFrame(menu)
        self.menu_cards.grid(row=2, column=0, sticky="nsew")
        for column in range(2):
            self.menu_cards.body.columnconfigure(column, weight=1, uniform="menu")
        self.search.trace_add("write", lambda *_: self.render_menu())
        receipt = ttk.Frame(panes, style="Panel.TFrame", padding=16)
        receipt.grid(row=0, column=1, sticky="nsew")
        receipt.columnconfigure(0, weight=1)
        receipt.rowconfigure(1, weight=1)
        self.cart_title = ttk.Label(receipt, text="Giỏ hàng", style="Heading.TLabel")
        self.cart_title.grid(row=0, column=0, sticky="w", pady=(0, 12))
        self.cart_table = DataTable(receipt, [("TenSP", "Món", 190), ("SoLuong", "SL", 50), ("ThanhTien", "Thành tiền", 120)],
                                    height=5, empty_text="Giỏ hàng đang trống.\nChọn món ở bên trái để thêm vào đơn.")
        self.cart_table.grid(row=1, column=0, sticky="nsew")
        self.cart_table.tree.bind("<<TreeviewSelect>>", self.item_selected)
        self.quantity_var = tk.StringVar(self, "1")
        quantity_bar = ttk.Frame(receipt, style="Card.TFrame")
        quantity_bar.grid(row=2, column=0, sticky="ew", pady=8)
        self.quantity_buttons = []
        if self.editable:
            for label, command in [("-", lambda: self.adjust_quantity(-1)), ("+", lambda: self.adjust_quantity(1))]:
                button = ttk.Button(quantity_bar, text=label, width=3, command=command, state="disabled", style="Card.TButton")
                button.pack(side="left", padx=(0, 5))
                self.quantity_buttons.append(button)
            self.quantity_entry = ttk.Spinbox(quantity_bar, from_=1, to=999, textvariable=self.quantity_var, width=4, command=self.update_item, style="Card.TSpinbox")
            self.quantity_entry.pack(side="left", padx=(0, 5))
            self.quantity_entry.bind("<Return>", lambda event: self.update_item())
            for label, command in [("Áp dụng", self.update_item), ("Bỏ món", self.remove_item)]:
                button = ttk.Button(quantity_bar, text=label, command=command, state="disabled", style="Card.TButton")
                button.pack(side="left", padx=(0, 5))
                self.quantity_buttons.append(button)
        total_frame = ttk.Frame(receipt, style="Card.TFrame")
        total_frame.grid(row=3, column=0, sticky="ew", pady=(2, 6))
        ttk.Label(total_frame, text="TỔNG CỘNG", style="Muted.Card.TLabel",
                  font=("Segoe UI", 9, "bold")).pack(side="left")
        self.total_label = ttk.Label(total_frame, style="Metric.TLabel", foreground=COLORS["gold"])
        self.total_label.pack(side="right")
        self.error_label = ttk.Label(receipt, text="", style="Card.TLabel", foreground=COLORS["danger"], wraplength=405)
        self.error_label.grid(row=4, column=0, sticky="w", pady=(0, 6))
        self.save_button = self.pay_button = None
        if self.editable:
            actions = ttk.Frame(receipt, style="Card.TFrame")
            actions.grid(row=5, column=0, sticky="ew", pady=(8, 0))
            actions.columnconfigure((0, 1), weight=1, uniform="actions")
            self.save_button = ttk.Button(actions, text="Lưu đơn", style="Card.TButton", command=self.save)
            self.save_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))
            self.pay_button = ttk.Button(actions, text="Lưu & thu tiền", style="Card.Accent.TButton", command=self.checkout)
            self.pay_button.grid(row=0, column=1, sticky="ew")
        ttk.Button(body, text="Đóng", command=self.close).grid(row=3, column=0, sticky="e", pady=(14, 0))
        self.render_menu()
        self.render_cart()
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Escape>", lambda event: self.close())
        self.grab_set()

    def render_menu(self):
        for widget in self.menu_cards.body.winfo_children():
            widget.destroy()
        term = search_text(self.search.get().strip())
        data = [p for p in self.products.values() if term in search_text(p["TenSP"]) and
                (self.category.get() == "Tất cả món" or p["DanhMuc"] == self.category.get())]
        if not data:
            ttk.Label(self.menu_cards.body, text="Không tìm thấy món phù hợp.", style="Subtitle.TLabel").grid(columnspan=2, pady=40)
        for index, product in enumerate(data):
            card = ttk.Frame(self.menu_cards.body, style="Panel.TFrame", padding=15)
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=(0, 9), pady=(0, 10))
            ttk.Label(card, text=product["DanhMuc"].upper(), style="Muted.Card.TLabel",
                      font=("Segoe UI", 8, "bold")).pack(anchor="w")
            ttk.Label(card, text=product["TenSP"], style="Heading.TLabel", wraplength=185).pack(anchor="w", pady=(10, 4))
            ttk.Label(card, text=money(product["Gia"]), style="Card.TLabel", foreground=COLORS["gold"],
                      font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 12))
            ttk.Button(card, text="Thêm món", style="Card.Soft.TButton", state="normal" if self.editable else "disabled",
                       command=lambda key=product["MaSP"]: self.add_item(key)).pack(fill="x")

    def render_cart(self):
        data = [dict(line, ThanhTien=line["DonGia"] * line["SoLuong"]) for line in self.cart.values()]
        self.cart_table.fill(data, "MaSP", lambda key, value: money(value) if key == "ThanhTien" else display(value))
        total = sum([row['ThanhTien'] for row in data], Decimal(0))
        self.total_label.configure(text=money(total))
        item_count = 0
        for row in data:
            item_count += row["SoLuong"]
        self.cart_title.configure(text=f"Giỏ hàng - {item_count} món")
        self.error_label.configure(text="")
        self.error_label.grid_remove()
        for button in (self.save_button, self.pay_button):
            if button:
                button.configure(state="normal" if data else "disabled")
        self.item_selected()

    def item_selected(self, event=None):
        selected = self.cart_table.tree.selection()
        if hasattr(self, "quantity_entry"):
            self.quantity_entry.configure(state="normal" if selected else "disabled")
        for button in self.quantity_buttons:
            button.configure(state="normal" if selected else "disabled")
        if selected and int(selected[0]) in self.cart:
            self.quantity_var.set(str(self.cart[int(selected[0])]["SoLuong"]))

    def add_item(self, product_id):
        try:
            if product_id in self.cart:
                self.cart[product_id]["SoLuong"] = integer(self.cart[product_id]["SoLuong"] + 1, "Số lượng", 1, 999)
            else:
                product = self.products[product_id]
                self.cart[product_id] = {"MaSP": product_id, "TenSP": product["TenSP"], "SoLuong": 1, "DonGia": product["Gia"]}
            self.dirty = True
            self.render_cart()
            self.cart_table.tree.selection_set(str(product_id))
            self.item_selected()
        except Exception as error:
            report_error(self, error)

    def update_item(self):
        try:
            product_id = self.cart_table.selected_id()
            try:
                self.cart[product_id]["SoLuong"] = integer(self.quantity_var.get(), "Số lượng", 1, 999)
            except AppError as error:
                self.error_label.configure(text=str(error))
                self.error_label.grid()
                return
            self.dirty = True
            self.render_cart()
        except Exception as error:
            report_error(self, error)

    def adjust_quantity(self, delta):
        try:
            product_id = self.cart_table.selected_id()
            count = self.cart[product_id]["SoLuong"] + delta
            if count < 1:
                return self.remove_item()
            self.quantity_var.set(str(count))
            self.update_item()
        except Exception as error:
            report_error(self, error)

    def remove_item(self):
        try:
            del self.cart[self.cart_table.selected_id()]
            self.dirty = True
            self.render_cart()
        except Exception as error:
            report_error(self, error)

    def persist(self):
        table_id = self.table_options.get(self.table_var.get())
        if table_id is None:
            raise AppError("Vui lòng chọn bàn trống trước khi lưu đơn.")
        if self.cart_table.tree.selection():
            key = self.cart_table.selected_id()
            self.cart[key]["SoLuong"] = integer(self.quantity_var.get(), "Số lượng", 1, 999)
        self.order_id = self.service.save_order(table_id, self.customer_options[self.customer_var.get()],
            [(key, item["SoLuong"]) for key, item in self.cart.items()], self.order_id, self.order.get("PhienBan"))
        self.on_change()
        notify(self.master, f"Đã lưu đơn #{self.order_id}.")

    def save(self):
        try:
            try:
                self.persist()
            except AppError as error:
                self.error_label.configure(text=str(error))
                self.error_label.grid()
                return
            self.destroy()
        except Exception as error:
            report_error(self, error)

    def checkout(self):
        try:
            try:
                self.persist()
            except AppError as error:
                self.error_label.configure(text=str(error))
                self.error_label.grid()
                return
            parent, order_id = self.master, self.order_id
            self.destroy()
            return PaymentDialog(parent, self.service, order_id, self.on_change)
        except Exception as error:
            report_error(self, error)

    def close(self):
        changed = self.dirty or self.table_var.get() != self.initial_table or self.customer_var.get() != self.initial_customer
        selection = self.cart_table.tree.selection()
        if selection:
            changed = changed or self.quantity_var.get() != str(self.cart[int(selection[0])]["SoLuong"])
        if self.editable and changed and not messagebox.askyesno("Đóng đơn hàng", "Bỏ các thay đổi chưa lưu?", parent=self):
            return
        self.destroy()
