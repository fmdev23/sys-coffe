from tkinter import messagebox, ttk

from models.service import MANAGER, STAFF, AppError
from ui.common import DataTable, FormDialog, display, report_error, notify


class AccountTab(ttk.Frame):
    def __init__(self, parent, service, on_change):
        super().__init__(parent, padding=24)
        self.service, self.on_change = service, on_change
        self.data = []
        ttk.Label(self, text="Tài khoản & phân quyền", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self, text="Mỗi nhân viên liên kết một tài khoản. Mật khẩu tối thiểu 8 ký tự.",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(5, 18))
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 12))
        self.actions = []
        for text, command in [("Thêm tài khoản", self.add), ("Sửa / đặt lại mật khẩu", self.edit),
                              ("Xoá", self.delete), ("Làm mới", self.refresh)]:
            button = ttk.Button(toolbar, text=text, command=command,
                                style="Accent.TButton" if command == self.add else "Danger.TButton" if command == self.delete else "TButton")
            button.pack(side="left", padx=(0, 6))
            if command in (self.edit, self.delete):
                button.configure(state="disabled")
                self.actions.append(button)
        self.table = DataTable(self, [("MaTK", "Mã", 60), ("TenDangNhap", "Tên đăng nhập", 190),
            ("HoTen", "Nhân viên", 250), ("VaiTro", "Vai trò", 160), ("HoatDong", "Trạng thái", 170)])
        self.table.pack(fill="both", expand=True)
        self.table.tree.bind("<Double-1>", lambda event: self.edit())
        self.table.tree.bind("<<TreeviewSelect>>", self.update_actions)

    def update_actions(self, event=None):
        for button in self.actions:
            button.configure(state="normal" if self.table.tree.selection() else "disabled")

    def refresh(self):
        try:
            self.data = self.service.list_accounts()
            self.table.fill(self.data, "MaTK", self.format_status)
            self.update_actions()
        except Exception as error:
            report_error(self, error)

    def format_status(self, key, value):
        if key == "HoatDong":
            return "Hoạt động" if value else "Đã khoá"
        return display(value)

    def form(self, current=None):
        current = current or {}
        employees = self.service.list_entities("employees")
        accounts = self.service.list_accounts()
        taken = {a["MaNV"] for a in accounts if a["MaTK"] != current.get("MaTK")}
        options = {f"{e['MaNV']} - {e['HoTen']}": e["MaNV"] for e in employees if e["MaNV"] not in taken}
        if not options:
            raise AppError("Hãy thêm nhân viên chưa có tài khoản ở mục Nhân viên trước.")
        fields = [("TenDangNhap", "Tên đăng nhập *", None), ("password", "Mật khẩu", "password"),
                  ("MaNV", "Nhân viên *", options), ("VaiTro", "Vai trò", {STAFF: STAFF, MANAGER: MANAGER}),
                  ("HoatDong", "Trạng thái", {"Hoạt động": 1, "Đã khoá": 0})]

        def save(values):
            self.service.save_account(values["TenDangNhap"], values["password"], values["VaiTro"],
                                      values["MaNV"], values["HoatDong"], current.get("MaTK"))
            self.on_change()
            notify(self, "Đã lưu tài khoản.")

        return FormDialog(self, "Sửa tài khoản" if current else "Thêm tài khoản", fields, current, save,
                          "Khi sửa, để trống mật khẩu để giữ mật khẩu hiện tại. Không thể tự khoá hoặc hạ quyền.")

    def add(self):
        try:
            return self.form()
        except Exception as error:
            report_error(self, error)

    def edit(self):
        try:
            account_id = self.table.selected_id()
            return self.form(next(a for a in self.data if a["MaTK"] == account_id))
        except Exception as error:
            report_error(self, error)

    def delete(self):
        try:
            account_id = self.table.selected_id()
            if messagebox.askyesno("Xoá tài khoản", "Xoá tài khoản đang chọn? Hồ sơ nhân viên vẫn được giữ lại.", parent=self):
                self.service.delete_account(account_id)
                self.on_change()
                notify(self, "Đã xoá tài khoản.")
        except Exception as error:
            report_error(self, error)
