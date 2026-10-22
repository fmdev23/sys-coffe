from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from models.service import AppError, MANAGER, PENDING
from ui.account_tab import AccountTab
from ui.common import FormDialog, center_window, report_error
from ui.dashboard import Dashboard
from ui.entity_tab import EntityTab
from ui.order_tab import OrderTab, OrderEditor
from ui.statistics_tab import StatisticsTab
from ui.table_tab import TableTab
from ui.theme import COLORS


class MainWindow(ttk.Frame):
    def __init__(self, parent, service, on_logout):
        self.profile = service.profile()
        super().__init__(parent)
        self.service, self.on_logout = service, on_logout
        self.manager = self.profile["VaiTro"] == MANAGER
        self.current_page = None
        self.pack(fill="both", expand=True)
        parent.title("Coffee - Quản lý quán")
        width, height = min(1440, parent.winfo_screenwidth() - 60), min(900, parent.winfo_screenheight() - 85)
        parent.minsize(min(1140, width), min(730, height))
        parent.resizable(True, True)
        center_window(parent, width, height)
        sidebar = tk.Frame(self, background=COLORS["sidebar"], width=205)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        brand = tk.Frame(sidebar, background=COLORS["sidebar"])
        brand.pack(fill="x", padx=18, pady=(22, 5))
        tk.Label(brand, image=parent.logo_small, background=COLORS["sidebar"]).pack(side="left", padx=(0, 9))
        tk.Label(brand, text="COFFEE", font=("Segoe UI", 15, "bold"), background=COLORS["sidebar"],
                 foreground="#F0D7AD").pack(side="left")
        tk.Label(sidebar, text="Quản lý quán cà phê", background=COLORS["sidebar"], foreground="#BDD0C4").pack(anchor="w", padx=24)
        account = tk.Frame(sidebar, background=COLORS["sidebar"], padx=16, pady=12)
        account.pack(side="bottom", fill="x")
        tk.Label(account, text=self.profile["VaiTro"], background=COLORS["sidebar"], foreground="#E9D4B3",
                 anchor="w", font=("Segoe UI", 10, "bold")).pack(fill="x", pady=(0, 8))
        for label, action in [("Đổi mật khẩu", self.change_password), ("Đăng xuất", self.logout)]:
            ttk.Button(account, text=label, command=action, style="Nav.TButton").pack(fill="x")
        workspace = ttk.Frame(self)
        workspace.pack(side="left", fill="both", expand=True)
        header = ttk.Frame(workspace, style="Card.TFrame", padding=(24, 15))
        header.pack(fill="x")
        ttk.Label(header, text="KHÔNG GIAN QUẢN LÝ" if self.manager else "KHÔNG GIAN PHỤC VỤ",
                  style="Muted.Card.TLabel", font=("Segoe UI", 9, "bold")).pack(side="left")
        ttk.Label(header, text=self.profile['HoTen'], style="Card.TLabel").pack(side="right")
        ttk.Label(header, text=datetime.now().strftime("%d / %m / %Y") + "    |    ",
                  style="Muted.Card.TLabel").pack(side="right")
        footer = ttk.Frame(workspace, padding=(24, 7))
        footer.pack(side="bottom", fill="x")

        self.status_label = ttk.Label(footer, text="Sẵn sàng phục vụ.", style="Subtitle.TLabel", font=("Segoe UI", 9))
        self.status_label.pack(side="left")
        ttk.Label(footer, text="F5  Làm mới", style="Subtitle.TLabel", font=("Segoe UI", 9)).pack(side="right")
        content = ttk.Frame(workspace)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)
        self.pages = {}
        self.pages["orders"] = OrderTab(content, service, self.manager, self.refresh_all)
        self.pages["tables"] = TableTab(content, service, self.manager, self.refresh_all, self.open_table)
        self.pages["products"] = EntityTab(content, service, "products", self.manager, self.refresh_all)
        if self.manager:
            self.pages["dashboard"] = Dashboard(content, service, self.show_page, self.pages["orders"].add)
            for entity in ("employees", "customers"):
                self.pages[entity] = EntityTab(content, service, entity, True, self.refresh_all)
            self.pages["accounts"] = AccountTab(content, service, self.refresh_all)
            self.pages["statistics"] = StatisticsTab(content, service)
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")
        self.nav_buttons = {}
        sections = [("VẬN HÀNH", [("dashboard", "Tổng quan"), ("orders", "Đơn hàng"),
            ("tables", "Sơ đồ bàn"), ("products", "Thực đơn")]),
            ("QUẢN TRỊ", [("customers", "Khách hàng"), ("employees", "Nhân viên"),
                          ("accounts", "Tài khoản"), ("statistics", "Báo cáo doanh thu")])]
        for title, links in sections:
            visible = [(key, label) for key, label in links if key in self.pages]
            if not visible:
                continue
            tk.Label(sidebar, text=title, background=COLORS["sidebar"], foreground="#92B2A1",
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=24, pady=(18, 8))
            for key, label in visible:
                button = ttk.Button(sidebar, text=label, command=lambda name=key: self.show_page(name), style="Nav.TButton")
                button.pack(fill="x", padx=12, pady=1)
                self.nav_buttons[key] = button
        self.bind_id = parent.bind("<F5>", lambda event: self.refresh_all())
        self.bind("<Destroy>", self.cleanup)
        self.show_page("dashboard" if self.manager else "tables")

    def cleanup(self, event):
        if event.widget == self:
            self.winfo_toplevel().unbind("<F5>", self.bind_id)

    def show_page(self, name):
        if name not in self.pages:
            return
        self.current_page = name
        self.pages[name].tkraise()
        for key, button in self.nav_buttons.items():
            button.configure(style="NavActive.TButton" if key == name else "Nav.TButton")
        self.pages[name].refresh()

    def refresh_all(self):
        if self.current_page:
            self.pages[self.current_page].refresh()
        self.set_status("Đã cập nhật dữ liệu.")

    def set_status(self, message):
        self.status_label.configure(text=f"{message}  -  {datetime.now():%H:%M}")

    def open_table(self, table_id):
        try:
            pending = next((o for o in self.service.list_orders(PENDING) if o["MaBan"] == table_id), None)
            return OrderEditor(self, self.service, self.refresh_all,
                               order_id=pending["MaDH"] if pending else None, table_id=table_id)
        except Exception as error:
            report_error(self, error)

    def logout(self):
        if messagebox.askyesno("Đăng xuất", "Kết thúc phiên làm việc hiện tại?", parent=self):
            self.on_logout()

    def change_password(self):
        try:
            def save(values):
                if values["new"] != values["confirm"]:
                    raise AppError("Mật khẩu xác nhận không trùng khớp.")
                self.service.change_password(values["old"], values["new"])
                self.set_status("Đã đổi mật khẩu.")

            return FormDialog(self, "Đổi mật khẩu", [("old", "Mật khẩu hiện tại", "password"),
                ("new", "Mật khẩu mới", "password"), ("confirm", "Nhập lại mật khẩu mới", "password")], {}, save,
                "Mật khẩu mới phải có ít nhất 8 ký tự.")
        except Exception as error:
            report_error(self, error)
