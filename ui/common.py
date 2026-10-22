import logging
import tkinter as tk
from datetime import datetime
from decimal import Decimal
from tkinter import messagebox, ttk

import pyodbc

from models.service import AppError
from ui.theme import COLORS


def money(value):
    return f"{Decimal(value or 0):,.0f}".replace(",", ".") + " ₫"


def display(value):
    if value is None:
        return "—"
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M")
    return str(value)


def report_error(parent, error):
    if isinstance(error, (AppError, ValueError)):
        message = str(error)
    elif isinstance(error, pyodbc.IntegrityError):
        logging.exception("Ràng buộc dữ liệu")
        details = str(error)
        if "2601" in details or "2627" in details:
            message = "Tên bàn, tên đăng nhập hoặc nhân viên liên kết đã được sử dụng. Hãy kiểm tra lại."
        elif "547" in details:
            message = ("Dữ liệu đang được tài khoản hoặc đơn hàng sử dụng, hoặc vừa thay đổi. "
                       "Không thể xoá bản ghi có liên kết. Với sản phẩm cũ, hãy chọn Ngừng bán.")
        else:
            message = "Dữ liệu không hợp lệ hoặc có liên kết với bản ghi khác. Hãy làm mới và kiểm tra lại."
    elif isinstance(error, pyodbc.Error):
        logging.exception("Lỗi SQL Server")
        message = ("Không thể thực hiện thao tác với SQL Server. Kiểm tra dịch vụ SQL Server, "
                   "kết nối và chạy database_setup.py nếu chưa tạo dữ liệu. "
                   "Nếu dữ liệu đang được dùng ở cửa sổ khác, hãy thử lại.")
    else:
        logging.exception("Lỗi ứng dụng")
        message = "Không thể hoàn thành thao tác. Chi tiết được ghi trong coffee.log."
    messagebox.showerror("Không thể thực hiện", message, parent=parent)


def center_window(window, width=None, height=None):
    window.update_idletasks()
    width = width or window.winfo_reqwidth()
    height = height or window.winfo_reqheight()
    x = max(0, (window.winfo_screenwidth() - width) // 2)
    y = max(0, (window.winfo_screenheight() - height) // 2 - 25)
    window.geometry(f"{width}x{height}+{x}+{y}")


def notify(widget, message="Đã lưu thay đổi."):
    """Hiển thị kết quả thao tác tại thanh trạng thái chung."""
    screen = getattr(widget.winfo_toplevel(), "screen", None)
    if screen and hasattr(screen, "set_status"):
        screen.set_status(message)


def search_text(value):
    # Tìm được "ca phe" khi dữ liệu lưu là "Cà phê".
    import unicodedata
    value = str(value).casefold().replace("đ", "d")
    result = ""
    for character in unicodedata.normalize("NFD", value):
        if not unicodedata.combining(character):
            result += character
    return result


def greeting():
    """Lời chào theo giờ trong ngày."""
    hour = datetime.now().hour
    if hour < 12:
        return "Chào buổi sáng"
    if hour < 18:
        return "Chào buổi chiều"
    return "Chào buổi tối"


class MetricCard(ttk.Frame):
    def __init__(self, parent, label, hint="", accent="primary"):
        super().__init__(parent, style="Panel.TFrame", padding=(18, 15))
        ttk.Label(self, text=label.upper(), style="Muted.Card.TLabel",
                  font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.value = ttk.Label(self, text="—", style="Metric.TLabel", foreground=COLORS[accent])
        self.value.pack(anchor="w", pady=(8, 3))
        self.hint = ttk.Label(self, text=hint, style="Muted.Card.TLabel", font=("Segoe UI", 9))
        self.hint.pack(anchor="w")

    def set(self, value, hint=None):
        size = 23 if len(str(value)) <= 14 else 18 if len(str(value)) <= 18 else 15
        self.value.configure(text=value, font=("Segoe UI", size, "bold"))
        if hint is not None:
            self.hint.configure(text=hint)


class ScrollFrame(ttk.Frame):
    """Vùng cuộn cho các thẻ món/bàn; không bắt con lăn của cửa sổ khác."""
    def __init__(self, parent):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, background=COLORS["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.body = ttk.Frame(self.canvas)
        self.window_id = self.canvas.create_window(0, 0, window=self.body, anchor="nw")
        self.body.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda event: self.canvas.itemconfigure(self.window_id, width=event.width))
        self.top = self.winfo_toplevel()
        self.wheel_binding = self.top.bind("<MouseWheel>", self.scroll, add="+")
        self.bind("<Destroy>", self.cleanup)

    def scroll(self, event):
        widget = event.widget
        if str(widget).startswith(str(self)) and self.body.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(-int(event.delta / 120), "units")
            return "break"

    def cleanup(self, event):
        if event.widget == self:
            self.top.unbind("<MouseWheel>", self.wheel_binding)


class DataTable(ttk.Frame):
    def __init__(self, parent, columns, height=10, empty_text="Chưa có dữ liệu.\nThêm mới để bắt đầu."):
        super().__init__(parent, style="Card.TFrame")
        self.columns = columns
        self.data, self.sort_key, self.reverse = [], None, False
        self.tree = ttk.Treeview(self, columns=[c[0] for c in columns], show="headings",
                                 selectmode="browse", height=height)
        for key, label, width in columns:
            self.tree.heading(key, text=label, command=lambda c=key: self.sort(c))
            numeric = key in ("Gia", "TongTien", "DonGia", "ThanhTien", "DoanhThu", "SoLuong", "DiemTichLuy")
            self.tree.column(key, width=width, minwidth=50, anchor="e" if numeric else "w")
        vertical = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        horizontal = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.tree.tag_configure("even", background="#FAFBF8")
        self.tree.tag_configure("odd", background="#FFFFFF")
        self.tree.tag_configure("Đã thanh toán", foreground=COLORS["primary"])
        self.tree.tag_configure("Đang xử lý", foreground="#916024")
        self.tree.tag_configure("Đã huỷ", foreground=COLORS["danger"])
        self.empty = ttk.Label(self, text=empty_text, style="Muted.Card.TLabel", justify="center", anchor="center")

    def fill(self, data, key, formatter=None):
        self.data, self.key, self.formatter = list(data), key, formatter
        self.render()

    def sort(self, key):
        self.reverse = not self.reverse if self.sort_key == key else False
        self.sort_key = key
        self.render()

    def render(self):
        selected = self.tree.selection()
        self.tree.delete(*self.tree.get_children())
        data = self.data
        if self.sort_key:
            data = sorted(data, key=lambda row: (row.get(self.sort_key) is None, row.get(self.sort_key)), reverse=self.reverse)
        for key, label, _ in self.columns:
            arrow = (" ↓" if self.reverse else " ↑") if key == self.sort_key else ""
            self.tree.heading(key, text=label + arrow)
        for index, item in enumerate(data):
            values = [(self.formatter(c[0], item[c[0]]) if self.formatter else display(item.get(c[0])))
                      for c in self.columns]
            tags = ["even" if index % 2 == 0 else "odd"]
            tags.append(str(item.get("TrangThai", "")))
            self.tree.insert("", "end", iid=str(item[self.key]), values=values, tags=tags)
        if data:
            self.empty.place_forget()
        else:
            self.empty.place(relx=0.5, rely=0.52, anchor="center")
        if selected and self.tree.exists(selected[0]):
            self.tree.selection_set(selected[0])

    def selected_id(self):
        selection = self.tree.selection()
        if not selection:
            raise AppError("Vui lòng chọn một dòng trong danh sách.")
        return int(selection[0])


class FormDialog(tk.Toplevel):
    """Form có lựa chọn ánh xạ nhãn tiếng Việt sang giá trị dữ liệu."""
    def __init__(self, parent, title, fields, initial, on_save, note=""):
        super().__init__(parent)
        self.title(title)
        self.transient(parent.winfo_toplevel())
        self.resizable(True, False)
        self.minsize(490, 100)
        self.on_save = on_save
        self.variables = {}
        self.options = {}
        body = ttk.Frame(self, padding=28, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        ttk.Label(body, text=title, style="Heading.TLabel", font=("Segoe UI", 15, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 18))
        first = None
        for row, (key, label, options) in enumerate(fields, start=1):
            ttk.Label(body, text=label, style="Card.TLabel").grid(row=row, column=0, sticky="w", padx=(0, 16), pady=8)
            value = initial.get(key, "")
            variable = tk.StringVar(self)
            self.variables[key] = variable
            if isinstance(options, dict):
                self.options[key] = options
                variable.set(next((k for k, v in options.items() if v == value), next(iter(options), "")))
                widget = ttk.Combobox(body, textvariable=variable, values=list(options), state="readonly", style="Card.TCombobox")
            else:
                variable.set(display(value) if value is not None else "")
                widget = ttk.Entry(body, textvariable=variable, show="*" if options == "password" else "", style="Card.TEntry")
            widget.grid(row=row, column=1, sticky="ew", pady=7)
            first = first or widget
        row = len(fields) + 1
        if note:
            ttk.Label(body, text=note, style="Muted.Card.TLabel", wraplength=440).grid(
                row=row, column=0, columnspan=2, sticky="w", pady=(12, 8))
        self.error_label = ttk.Label(body, text="", foreground=COLORS["danger"], style="Card.TLabel", wraplength=430)
        self.error_label.grid(row=row + 1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        buttons = ttk.Frame(body, style="Card.TFrame")
        buttons.grid(row=row + 2, column=0, columnspan=2, sticky="e", pady=(18, 0))
        ttk.Button(buttons, text="Huỷ", command=self.destroy, style="Card.TButton").pack(side="left", padx=5)
        ttk.Button(buttons, text="Lưu", style="Card.Accent.TButton", command=self.save).pack(side="left")
        self.bind("<Return>", lambda event: self.save())
        self.bind("<Escape>", lambda event: self.destroy())
        self.grab_set()
        center_window(self)
        if first:
            first.focus_set()

    def save(self):
        try:
            data = {key: self.options[key][var.get()] if key in self.options else var.get()
                    for key, var in self.variables.items()}
            try:
                self.on_save(data)
            except (AppError, ValueError) as error:
                self.error_label.configure(text=str(error))
                return
            self.destroy()
        except Exception as error:
            report_error(self, error)
