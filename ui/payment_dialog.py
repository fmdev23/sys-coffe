from decimal import Decimal, InvalidOperation
import tkinter as tk
from tkinter import ttk

from models.service import AppError, PENDING
from ui.common import center_window, report_error, money, notify
from ui.theme import COLORS


class PaymentDialog(tk.Toplevel):
    def __init__(self, parent, service, order_id, on_change):
        order, _ = service.get_order(order_id)
        if order["TrangThai"] != PENDING:
            raise AppError("Chỉ có thể thanh toán đơn đang xử lý.")
        super().__init__(parent)
        self.service, self.order, self.on_change = service, order, on_change
        self.title(f"Thanh toán đơn #{order_id}")
        self.transient(parent.winfo_toplevel())
        self.resizable(False, False)
        body = ttk.Frame(self, padding=32, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        header = ttk.Frame(body, style="Card.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text=f"Thanh toán đơn #{order_id}", style="Heading.TLabel",
                  font=("Segoe UI", 16, "bold")).pack(side="left", anchor="s", pady=(0, 4))
        ttk.Label(body, text="TỔNG CẦN THU", style="Muted.Card.TLabel",
                  font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(24, 5))
        ttk.Label(body, text=money(order["TongTien"]), style="Metric.TLabel",
                  foreground=COLORS["primary"], font=("Segoe UI", 28, "bold")).pack(anchor="w", pady=(0, 24))
        ttk.Label(body, text="Tiền khách đưa (đồng)", style="Card.TLabel").pack(anchor="w")
        self.received = tk.StringVar(self, str(int(order["TongTien"])))
        entry = ttk.Entry(body, textvariable=self.received, width=35, font=("Segoe UI", 13), style="Card.TEntry")
        entry.pack(fill="x", pady=(8, 14))
        quick = ttk.Frame(body, style="Card.TFrame")
        quick.pack(fill="x")
        for label, value in [("Vừa đủ", int(order["TongTien"])), ("100k", 100000),
                              ("200k", 200000), ("500k", 500000)]:
            ttk.Button(quick, text=label, style="Card.Soft.TButton",
                       command=lambda v=value: self.received.set(str(v))).pack(side="left", padx=(0, 8))
        self.change_label = ttk.Label(body, style="Card.TLabel", font=("Segoe UI", 15, "bold"))
        self.change_label.pack(anchor="w", pady=22)
        ttk.Label(body, text="Xác nhận sau khi đã nhận đủ tiền.\nBàn được giải phóng và hoá đơn được lưu lại.",
                  style="Muted.Card.TLabel", justify="left").pack(anchor="w", pady=(0, 22))
        self.confirm_button = ttk.Button(body, text="Đã thu tiền - Hoàn tất", style="Card.Accent.TButton",
                                          command=self.confirm)
        self.confirm_button.pack(fill="x")
        ttk.Button(body, text="Quay lại", command=self.destroy, style="Card.TButton").pack(fill="x", pady=(8, 0))
        self.received.trace_add("write", lambda *_: self.update_change())
        self.update_change()
        self.bind("<Escape>", lambda event: self.destroy())
        center_window(self)
        self.grab_set()
        entry.focus_set()
        entry.selection_range(0, "end")

    def change_amount(self):
        text = self.received.get().strip().replace(".", "").replace(" ", "")
        if not text.isascii() or not text.isdigit() or len(text) > 15:
            raise AppError("Nhập số tiền bằng đồng, ví dụ 100000.")
        return Decimal(text) - self.order["TongTien"]

    def update_change(self):
        try:
            change = self.change_amount()
            message = f"Tiền thừa: {money(change)}" if change >= 0 else f"Còn thiếu: {money(-change)}"
            enabled = change >= 0
        except (AppError, InvalidOperation) as error:
            message, enabled = str(error), False
        self.change_label.configure(text=message, foreground=COLORS["primary"] if enabled else COLORS["danger"])
        self.confirm_button.configure(state="normal" if enabled else "disabled")

    def confirm(self):
        try:
            if self.change_amount() < 0:
                raise AppError("Chưa nhận đủ số tiền cần thanh toán.")
            self.service.finish_order(self.order["MaDH"], expected_version=self.order["PhienBan"])
            self.on_change()
            notify(self.master, f"Đã thanh toán đơn #{self.order['MaDH']} - {money(self.order['TongTien'])}.")
            self.destroy()
        except Exception as error:
            report_error(self, error)
