import tkinter as tk
from tkinter import messagebox, ttk

from models.service import AppError, PENDING
from ui.common import FormDialog, ScrollFrame, report_error, money, notify
from ui.entity_tab import CONFIG
from ui.theme import COLORS


class TableTab(ttk.Frame):
    def __init__(self, parent, service, manager, on_change, open_order):
        super().__init__(parent, padding=24)
        self.service, self.on_change, self.open_order = service, on_change, open_order
        self.data, self.orders = [], {}
        self.selected = None
        heading = ttk.Frame(self)
        heading.pack(fill="x", pady=(0, 6))
        ttk.Label(heading, text="Sơ đồ bàn", style="Title.TLabel").pack(side="left")
        self.summary = ttk.Label(heading, style="Subtitle.TLabel")
        self.summary.pack(side="right")
        ttk.Label(self, text="Chọn bàn trống để gọi món, hoặc tiếp tục đơn đang phục vụ.",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(0, 20))
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 16))
        self.edit_button = self.delete_button = None
        if manager:
            ttk.Button(toolbar, text="Thêm bàn", style="Accent.TButton", command=self.add).pack(side="left")
            self.edit_button = ttk.Button(toolbar, text="Sửa bàn", state="disabled", command=self.edit)
            self.edit_button.pack(side="left", padx=6)
            self.delete_button = ttk.Button(toolbar, text="Xoá bàn", style="Danger.TButton", state="disabled", command=self.delete)
            self.delete_button.pack(side="left")
        ttk.Button(toolbar, text="Làm mới", command=self.refresh).pack(side="left", padx=6)
        self.area = tk.StringVar(self, "Tất cả khu vực")
        self.area_combo = ttk.Combobox(toolbar, textvariable=self.area, state="readonly", width=23)
        self.area_combo.pack(side="right")
        self.area_combo.bind("<<ComboboxSelected>>", lambda event: self.render())
        self.cards = ScrollFrame(self)
        self.cards.pack(fill="both", expand=True)
        for column in range(4):
            self.cards.body.columnconfigure(column, weight=1, uniform="tables")

    def refresh(self):
        try:
            self.data = self.service.list_entities("tables")
            self.orders = {o["MaBan"]: o for o in self.service.list_orders(PENDING)}
            areas = ["Tất cả khu vực"] + sorted({r["KhuVuc"] for r in self.data})
            self.area_combo.configure(values=areas)
            if self.area.get() not in areas:
                self.area.set(areas[0])
            if self.selected not in {row["MaBan"] for row in self.data}:
                self.selected = None
            self.render()
        except Exception as error:
            report_error(self, error)

    def render(self):
        for widget in self.cards.body.winfo_children():
            widget.destroy()
        free = 0
        for row in self.data:
            if row["TrangThai"] == "Trống":
                free += 1
        self.summary.configure(text=f"{free} trống - {len(self.data) - free} đang phục vụ")
        data = [row for row in self.data if self.area.get() == "Tất cả khu vực" or row["KhuVuc"] == self.area.get()]
        if self.selected not in {row["MaBan"] for row in data}:
            self.selected = None
        for button in (self.edit_button, self.delete_button):
            if button:
                button.configure(state="normal" if self.selected else "disabled")
        if not data:
            ttk.Label(self.cards.body, text="Chưa có bàn. Thêm bàn để bắt đầu phục vụ.",
                      style="Subtitle.TLabel").grid(row=0, column=0, columnspan=4, pady=60)
        for index, row in enumerate(data):
            table_id = row["MaBan"]
            order = self.orders.get(table_id)
            is_selected = table_id == self.selected
            card = ttk.Frame(self.cards.body, padding=16,
                             style="SelectedPanel.TFrame" if is_selected else "Panel.TFrame")
            card.grid(row=index // 4, column=index % 4, sticky="nsew", padx=(0, 12), pady=(0, 12))
            select = lambda event=None, key=table_id: self.select(key)
            card.bind("<Button-1>", select)
            name_frame = tk.Frame(card, background="white")
            name_frame.pack(fill="x", pady=(0, 4))
            name_frame.bind("<Button-1>", select)
            tk.Label(name_frame, text=row["TenBan"], font=("Segoe UI", 15, "bold"),
                     background="white", foreground=COLORS["ink"], anchor="w").pack(side="left", padx=0)
            for widget in name_frame.winfo_children():
                widget.bind("<Button-1>", select)
            area_label = tk.Label(card, text=row["KhuVuc"], font=("Segoe UI", 10),
                                  background="white", foreground=COLORS["muted"], anchor="w")
            area_label.pack(fill="x", pady=(0, 8))
            area_label.bind("<Button-1>", select)
            if order:
                badge_bg, badge_fg = COLORS["gold_light"], "#8A5C26"
                badge_text = "Đang phục vụ"
            else:
                badge_bg, badge_fg = COLORS["green_light"], COLORS["primary"]
                badge_text = "Trống"
            badge = tk.Label(card, text=badge_text, anchor="w", background=badge_bg,
                             foreground=badge_fg, padx=12, pady=6, font=("Segoe UI", 9, "bold"))
            badge.pack(fill="x", pady=(0, 8))
            badge.bind("<Button-1>", select)
            info_text = f"Đơn #{order['MaDH']}  -  {money(order['TongTien'])}" if order else "Sẵn sàng đón khách"
            info = tk.Label(card, text=info_text, background="white", foreground=COLORS["muted"],
                            anchor="w", font=("Segoe UI", 9))
            info.pack(fill="x", pady=(0, 12))
            info.bind("<Button-1>", select)
            btn_text = "Tiếp tục đơn" if order else "Gọi món"
            ttk.Button(card, text=btn_text, style="Card.Soft.TButton" if not order else "Card.Accent.TButton",
                       command=lambda key=table_id: self.open_order(key)).pack(fill="x")

    def select(self, table_id):
        self.selected = table_id
        self.render()

    def save(self, values, table_id=None):
        self.service.save_entity("tables", values, table_id)
        self.on_change()
        notify(self, "Đã lưu thông tin bàn.")

    def add(self):
        try:
            return FormDialog(self, "Thêm bàn", CONFIG["tables"]["fields"], {}, self.save, "Tên bàn không được trùng nhau.")
        except Exception as error:
            report_error(self, error)

    def edit(self):
        try:
            current = next((r for r in self.data if r["MaBan"] == self.selected), None)
            if not current:
                raise AppError("Chọn tên bàn cần chỉnh sửa.")
            return FormDialog(self, "Sửa bàn", CONFIG["tables"]["fields"], current,
                              lambda values: self.save(values, current["MaBan"]))
        except Exception as error:
            report_error(self, error)

    def delete(self):
        try:
            current = next((r for r in self.data if r["MaBan"] == self.selected), None)
            if not current:
                raise AppError("Chọn tên bàn cần xoá.")
            if messagebox.askyesno("Xoá bàn", f"Xoá {current['TenBan']}? Bàn có lịch sử đơn hàng sẽ được giữ lại.", parent=self):
                self.service.delete_entity("tables", self.selected)
                self.selected = None
                self.on_change()
                notify(self, "Đã xoá bàn.")
        except Exception as error:
            report_error(self, error)
