import tkinter as tk
from tkinter import ttk

from models.service import login, AppError, CoffeeService
from ui.common import center_window, report_error
from ui.theme import COLORS


class LoginWindow(ttk.Frame):
    def __init__(self, parent, on_login):
        super().__init__(parent, style="Card.TFrame")
        self.on_login = on_login
        self.pack(fill="both", expand=True)
        parent.title("Coffee - Đăng nhập")
        parent.minsize(850, 580)
        parent.resizable(False, False)
        center_window(parent, 900, 580)

        brand = tk.Frame(self, background=COLORS["sidebar"], width=360)
        brand.pack(side="left", fill="y")
        brand.pack_propagate(False)

        tk.Label(brand, text="C O F F E E", background=COLORS["sidebar"], foreground="#F0D7AD",
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=38, pady=(45, 0))

        tk.Label(brand, image=parent.logo_large, background=COLORS["sidebar"]).pack(pady=(46, 46))

        tk.Label(brand, text="Quản lý gọn gàng.\nPhục vụ chu đáo.", justify="left", anchor="w", wraplength=280,
                 background=COLORS["sidebar"], foreground="#FFF9ED", font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=38)
        tk.Label(brand, text="Bàn - Gọi món - Thanh toán", background=COLORS["sidebar"],
                 foreground="#BBD0C2", font=("Segoe UI", 10)).pack(anchor="w", padx=38, pady=17)

        form = ttk.Frame(self, style="Card.TFrame", padding=(48, 38))
        form.pack(side="left", fill="both", expand=True)

        ttk.Label(form, text="Chào mừng trở lại", style="Heading.TLabel", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        ttk.Label(form, text="Đăng nhập để bắt đầu ca làm việc.", style="Muted.Card.TLabel", font=("Segoe UI", 11)).pack(anchor="w", pady=(8, 30))

        self.username, self.password = tk.StringVar(self), tk.StringVar(self)

        ttk.Label(form, text="Tên đăng nhập", style="Card.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.username_entry = ttk.Entry(form, textvariable=self.username, font=("Segoe UI", 11), style="Card.TEntry")
        self.username_entry.pack(fill="x", pady=(7, 16))

        ttk.Label(form, text="Mật khẩu", style="Card.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        password_entry = ttk.Entry(form, textvariable=self.password, show="*", font=("Segoe UI", 11), style="Card.TEntry")
        password_entry.pack(fill="x", pady=(7, 12))

        self.show_password = tk.BooleanVar(self, False)
        ttk.Checkbutton(form, text="Hiện mật khẩu", variable=self.show_password,
            command=lambda: password_entry.configure(show="" if self.show_password.get() else "*")).pack(anchor="w")

        self.error_label = ttk.Label(form, text="", foreground=COLORS["danger"], style="Card.TLabel", wraplength=375)
        self.error_label.pack(fill="x", pady=(12, 0))

        self.button = ttk.Button(form, text="Đăng nhập ", style="Card.Accent.TButton", command=self.login)
        self.button.pack(fill="x", pady=(12, 18), ipady=2)

        ttk.Label(form, text="Chưa có tài khoản? Liên hệ quản lý quán.", style="Muted.Card.TLabel").pack(anchor="w")

        self.username_entry.bind("<Return>", lambda event: password_entry.focus_set())
        password_entry.bind("<Return>", lambda event: self.login())
        self.username_entry.focus_set()

    def login(self):
        try:
            self.error_label.configure(text="")
            if not self.username.get().strip() or not self.password.get():
                self.error_label.configure(text="Vui lòng nhập tên đăng nhập và mật khẩu.")
                return
            self.button.configure(state="disabled", text="Đang đăng nhập...")
            self.update_idletasks()
            try:
                service = login(self.username.get(), self.password.get())
            except AppError as error:
                self.error_label.configure(text=str(error))
                return
            finally:
                self.button.configure(state="normal", text="Đăng nhập ")
            self.password.set("")
            self.on_login(service)
        except Exception as error:
            report_error(self, error)
