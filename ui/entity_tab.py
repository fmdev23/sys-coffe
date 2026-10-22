import tkinter as tk
from tkinter import messagebox, ttk

from ui.common import DataTable, FormDialog, display, report_error, money, notify, search_text

CONFIG = {
    "products": {
        "title": "Thực đơn", "key": "MaSP",
        "note": "Giá theo đồng Việt Nam. Ngừng bán để giữ lịch sử các sản phẩm đã có trong hoá đơn.",
        "columns": [("MaSP", "Mã", 60), ("TenSP", "Tên sản phẩm", 210), ("DanhMuc", "Danh mục", 150),
                    ("Gia", "Giá bán", 130), ("MoTa", "Mô tả", 250), ("TrangThai", "Trạng thái", 120)],
        "fields": [("TenSP", "Tên sản phẩm *", None), ("DanhMuc", "Danh mục *", None),
                   ("Gia", "Giá bán (đồng) *", None), ("MoTa", "Mô tả", None),
                   ("TrangThai", "Trạng thái", {"Còn bán": 1, "Ngừng bán": 0})],
    },
    "tables": {
        "title": "Bàn & khu vực", "key": "MaBan",
        "note": "Trạng thái bàn tự cập nhật khi tạo, chuyển bàn, thanh toán, huỷ hoặc xoá đơn.",
        "columns": [("MaBan", "Mã", 70), ("TenBan", "Tên bàn", 220), ("KhuVuc", "Khu vực", 300),
                    ("TrangThai", "Trạng thái", 190)],
        "fields": [("TenBan", "Tên bàn *", None), ("KhuVuc", "Khu vực *", None)],
    },
    "employees": {
        "title": "Nhân viên", "key": "MaNV",
        "note": "Tạo hồ sơ nhân viên trước, sau đó liên kết đăng nhập tại mục Tài khoản.",
        "columns": [("MaNV", "Mã", 65), ("HoTen", "Họ tên", 260), ("SDT", "Điện thoại", 180),
                    ("ChucVu", "Chức vụ", 160), ("TenDangNhap", "Tài khoản liên kết", 180)],
        "fields": [("HoTen", "Họ tên *", None), ("SDT", "Điện thoại", None), ("ChucVu", "Chức vụ *", None)],
    },
    "customers": {
        "title": "Khách hàng", "key": "MaKH",
        "note": "Mỗi 10.000 đồng thanh toán được cộng 1 điểm. Điện thoại có thể để trống.",
        "columns": [("MaKH", "Mã", 70), ("HoTen", "Họ tên", 300), ("SDT", "Điện thoại", 220),
                    ("DiemTichLuy", "Điểm tích luỹ", 160)],
        "fields": [("HoTen", "Họ tên *", None), ("SDT", "Điện thoại", None),
                   ("DiemTichLuy", "Điểm tích luỹ", None)],
    },
}


class EntityTab(ttk.Frame):
    def __init__(self, parent, service, entity, manager, on_change):
        super().__init__(parent, padding=24)
        self.service, self.entity, self.manager = service, entity, manager
        self.on_change = on_change
        self.config = CONFIG[entity]
        self.data = []
        ttk.Label(self, text=self.config["title"], style="Title.TLabel").pack(anchor="w")
        ttk.Label(self, text=self.config["note"], style="Subtitle.TLabel").pack(anchor="w", pady=(5, 18))
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 12))
        self.edit_button = self.delete_button = None
        if manager:
            ttk.Button(toolbar, text="Thêm mới", style="Accent.TButton", command=self.add).pack(side="left")
            self.edit_button = ttk.Button(toolbar, text="Sửa", command=self.edit, state="disabled")
            self.edit_button.pack(side="left", padx=6)
            self.delete_button = ttk.Button(toolbar, text="Xoá", command=self.delete, style="Danger.TButton", state="disabled")
            self.delete_button.pack(side="left")
        ttk.Button(toolbar, text="Làm mới", command=self.refresh).pack(side="left", padx=6)
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side="right")
        self.search = tk.StringVar(self)
        ttk.Label(search_frame, text="Tìm: ").pack(side="left")
        ttk.Entry(search_frame, textvariable=self.search, width=24).pack(side="left")
        self.table = DataTable(self, self.config["columns"])
        self.table.pack(fill="both", expand=True)
        self.table.tree.bind("<<TreeviewSelect>>", self.update_actions)
        self.count = ttk.Label(self, style="Subtitle.TLabel")
        self.count.pack(side="bottom", before=self.table, anchor="w", pady=(10, 0))
        self.search.trace_add("write", lambda *_: self.render())
        if manager:
            self.table.tree.bind("<Double-1>", lambda event: self.edit())

    def refresh(self):
        try:
            self.data = self.service.list_entities(self.entity)
            self.render()
        except Exception as error:
            report_error(self, error)

    def render(self):
        term = search_text(self.search.get().strip())
        filtered = []
        for row in self.data:
            values = []
            for value in row.values():
                values.append(display(value))
            if term in search_text(" ".join(values)):
                filtered.append(row)
        self.table.fill(filtered, self.config["key"], self.format_value)
        self.count.configure(text=f"{len(filtered)} / {len(self.data)} bản ghi  -  Nhấn tiêu đề cột để sắp xếp")
        self.update_actions()

    def update_actions(self, event=None):
        for button in (self.edit_button, self.delete_button):
            if button:
                button.configure(state="normal" if self.table.tree.selection() else "disabled")

    def format_value(self, key, value):
        if key == "Gia":
            return money(value)
        if key == "TrangThai" and self.entity == "products":
            return "Còn bán" if value else "Ngừng bán"
        return display(value)

    def save(self, values, record_id=None):
        self.service.save_entity(self.entity, values, record_id)
        self.on_change()
        notify(self)

    def add(self):
        try:
            return FormDialog(self, f"Thêm mới - {self.config['title']}", self.config["fields"],
                              {"DiemTichLuy": 0, "TrangThai": 1}, self.save, "* Trường bắt buộc.")
        except Exception as error:
            report_error(self, error)

    def edit(self):
        try:
            record_id = self.table.selected_id()
            current = next(r for r in self.data if r[self.config["key"]] == record_id)
            return FormDialog(self, f"Chỉnh sửa - {self.config['title']}", self.config["fields"], current,
                              lambda values: self.save(values, record_id), "* Trường bắt buộc.")
        except Exception as error:
            report_error(self, error)

    def delete(self):
        try:
            record_id = self.table.selected_id()
            if messagebox.askyesno("Xác nhận xoá", "Xoá bản ghi đang chọn? Thao tác này không thể hoàn tác.", parent=self):
                self.service.delete_entity(self.entity, record_id)
                self.on_change()
                notify(self, "Đã xoá bản ghi.")
        except Exception as error:
            report_error(self, error)
