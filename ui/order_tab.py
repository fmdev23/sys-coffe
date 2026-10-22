import tkinter as tk
from tkinter import messagebox, ttk

from models.service import AppError, CANCELLED, PAID, PENDING
from ui.common import DataTable, display, report_error, money, notify, search_text
from ui.order_editor import OrderEditor
from ui.payment_dialog import PaymentDialog


class OrderTab(ttk.Frame):
    def __init__(self, parent, service, manager, on_change):
        super().__init__(parent, padding=24)
        self.service, self.on_change = service, on_change
        self.data = []
        heading = ttk.Frame(self)
        heading.pack(fill="x")
        ttk.Label(heading, text="Đơn hàng", style="Title.TLabel").pack(side="left")
        ttk.Button(heading, text="Tạo đơn hàng", style="Accent.TButton", command=self.add).pack(side="right")
        ttk.Label(self, text="Theo dõi đơn, điều chỉnh món và thu tiền tại một nơi.",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(5, 20))
        filters = ttk.Frame(self)
        filters.pack(fill="x", pady=(0, 16))
        self.status = tk.StringVar(self, PENDING)
        self.filter_buttons = {}
        for state, label in [(PENDING, "Đang phục vụ"), (PAID, "Đã thanh toán"),
                                    (CANCELLED, "Đã huỷ"), ("Tất cả", "Tất cả")]:
            button = ttk.Button(filters, text=label, command=lambda value=state: self.filter_status(value))
            button.pack(side="left", padx=(0, 6))
            self.filter_buttons[state] = button
        search_frame = ttk.Frame(filters)
        search_frame.pack(side="right")
        self.search = tk.StringVar(self)
        ttk.Label(search_frame, text="Tìm: ").pack(side="left")
        ttk.Entry(search_frame, textvariable=self.search, width=20).pack(side="left")
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 12))
        self.actions = {}
        commands = [("edit", "Xem / Sửa", self.edit, "TButton"),
                    ("pay", "Thu tiền", self.pay, "Accent.TButton"),
                    ("cancel", "Huỷ đơn", self.cancel, "Danger.TButton")]
        if manager:
            commands.append(("delete", "Xoá", self.delete, "Danger.TButton"))
        for key, text, command, style in commands:
            button = ttk.Button(toolbar, text=text, command=command, style=style, state="disabled")
            button.pack(side="left", padx=(0, 6))
            self.actions[key] = button
        ttk.Button(toolbar, text="Làm mới", command=self.refresh).pack(side="right")
        self.summary = ttk.Label(self, style="Subtitle.TLabel")
        self.summary.pack(side="bottom", anchor="w", pady=(10, 0))
        self.table = DataTable(self, [("MaDH", "Mã đơn", 75), ("TenBan", "Bàn", 100),
            ("KhachHang", "Khách hàng", 185), ("ThoiGianTao", "Thời gian", 160),
            ("TongTien", "Tổng tiền", 135), ("TrangThai", "Trạng thái", 155)],
            empty_text="Chưa có đơn phù hợp.\nChọn Tạo đơn hàng hoặc đổi bộ lọc.")
        self.table.pack(fill="both", expand=True)
        self.table.tree.bind("<Double-1>", lambda event: self.edit())
        self.table.tree.bind("<Return>", lambda event: self.edit())
        self.table.tree.bind("<<TreeviewSelect>>", self.update_actions)
        self.search.trace_add("write", lambda *_: self.render())

    def refresh(self):
        try:
            self.data = self.service.list_orders()
            self.render()
        except Exception as error:
            report_error(self, error)

    def filter_status(self, value):
        self.status.set(value)
        self.render()

    def render(self):
        term = search_text(self.search.get().strip())
        data = [row for row in self.data if (self.status.get() == "Tất cả" or row["TrangThai"] == self.status.get()) and
                term in search_text(f"{row['MaDH']} {row['TenBan']} {row['KhachHang'] or 'Khách lẻ'}")]
        self.table.fill(data, "MaDH", lambda key, value: money(value) if key == "TongTien" else
                        (value or "Khách lẻ") if key == "KhachHang" else display(value))
        for state, button in self.filter_buttons.items():
            button.configure(style="Soft.TButton" if state == self.status.get() else "TButton")
        self.summary.configure(text=f"{len(data)} đơn hiển thị - Chọn một đơn để thao tác. Hoá đơn đã thanh toán được giữ lại.")
        self.update_actions()

    def update_actions(self, event=None):
        selection = self.table.tree.selection()
        current = next((row for row in self.data if selection and row["MaDH"] == int(selection[0])), None)
        for key, button in self.actions.items():
            allowed = bool(current) and (key == "edit" or
                (key in ("pay", "cancel") and current["TrangThai"] == PENDING) or
                (key == "delete" and current["TrangThai"] != PAID))
            button.configure(state="normal" if allowed else "disabled")

    def add(self):
        try:
            return OrderEditor(self, self.service, self.on_change)
        except Exception as error:
            report_error(self, error)

    def edit(self):
        try:
            return OrderEditor(self, self.service, self.on_change, self.table.selected_id())
        except Exception as error:
            report_error(self, error)

    def selected(self):
        order_id = self.table.selected_id()
        return next(row for row in self.data if row["MaDH"] == order_id)

    def pay(self):
        try:
            return PaymentDialog(self, self.service, self.table.selected_id(), self.on_change)
        except Exception as error:
            report_error(self, error)

    def cancel(self):
        try:
            order = self.selected()
            if order["TrangThai"] != PENDING:
                raise AppError("Chỉ có thể huỷ đơn đang xử lý.")
            if messagebox.askyesno("Huỷ đơn", f"Huỷ đơn #{order['MaDH']} tại {order['TenBan']}?\nBàn được giải phóng, đơn không tính vào doanh thu.", parent=self):
                self.service.finish_order(order["MaDH"], pay=False, expected_version=order["PhienBan"])
                self.on_change()
                notify(self, f"Đã huỷ đơn #{order['MaDH']}.")
        except Exception as error:
            report_error(self, error)

    def delete(self):
        try:
            order = self.selected()
            if messagebox.askyesno("Xoá đơn", f"Xoá vĩnh viễn đơn #{order['MaDH']} và các món trong đơn?", parent=self):
                self.service.delete_order(order["MaDH"], order["PhienBan"])
                self.on_change()
                notify(self, f"Đã xoá đơn #{order['MaDH']}.")
        except Exception as error:
            report_error(self, error)
