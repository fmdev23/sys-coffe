import csv
from datetime import date, timedelta
import tkinter as tk
from tkinter import filedialog, ttk

from models.service import report_period
from ui.chart import RevenueChart
from ui.common import DataTable, MetricCard, ScrollFrame, display, report_error, money, notify


class StatisticsTab(ttk.Frame):
    def __init__(self, parent, service):
        super().__init__(parent, padding=24)
        self.service = service
        self.result = None
        scroll = ScrollFrame(self)
        scroll.pack(fill="both", expand=True)
        content = scroll.body
        content.columnconfigure(0, weight=1)
        heading = ttk.Frame(content)
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        ttk.Label(heading, text="Báo cáo doanh thu", style="Title.TLabel").pack(side="left")
        ttk.Button(heading, text="Xuất CSV", command=self.export).pack(side="right")
        filters = ttk.Frame(content)
        filters.grid(row=1, column=0, sticky="ew")
        self.mode = tk.StringVar(self, "Theo ngày")
        self.start = tk.StringVar(self, date.today().isoformat())
        self.end = tk.StringVar(self, date.today().isoformat())
        combo = ttk.Combobox(filters, textvariable=self.mode, values=["Theo ngày", "Theo tháng"], state="readonly", width=12)
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", self.mode_changed)
        self.start_label = ttk.Label(filters, text="  Từ  ")
        self.start_label.pack(side="left")
        ttk.Entry(filters, textvariable=self.start, width=12).pack(side="left")
        self.end_label = ttk.Label(filters, text="  Đến  ")
        self.end_label.pack(side="left")
        self.end_entry = ttk.Entry(filters, textvariable=self.end, width=12)
        self.end_entry.pack(side="left")
        ttk.Button(filters, text="Xem báo cáo", style="Accent.TButton", command=self.refresh).pack(side="left", padx=10)
        shortcuts = ttk.Frame(content)
        shortcuts.grid(row=2, column=0, sticky="ew", pady=(10, 16))
        for label, period in [("Hôm nay", "today"), ("7 ngày qua", "week"), ("Tháng này", "month")]:
            ttk.Button(shortcuts, text=label, style="Soft.TButton",
                       command=lambda p=period: self.quick_period(p)).pack(side="left", padx=(0, 8))
        ttk.Label(shortcuts, text="Ngày: YYYY-MM-DD - Tháng: YYYY-MM", style="Subtitle.TLabel").pack(side="right")
        metrics = ttk.Frame(content)
        metrics.grid(row=3, column=0, sticky="ew", pady=(0, 18))
        self.cards = []
        for index, (label, hint) in enumerate([
                ("Doanh thu", "Chỉ tính đơn đã thanh toán"),
                ("Hoá đơn", "Số đơn thanh toán trong kỳ"),
                ("Trung bình / đơn", "Doanh thu chia số hoá đơn")]):
            metrics.columnconfigure(index, weight=1, uniform="stats")
            card = MetricCard(metrics, label, hint)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 12, 0))
            self.cards.append(card)
        panels = ttk.Frame(content)
        panels.grid(row=4, column=0, sticky="nsew")
        panels.rowconfigure(0, weight=1)
        panels.columnconfigure(0, weight=1, uniform="panels")
        panels.columnconfigure(1, weight=1, uniform="panels")
        chart_panel = ttk.Frame(panels, style="Panel.TFrame", padding=15)
        chart_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self.chart_title = ttk.Label(chart_panel, text="Doanh thu theo ngày", style="Heading.TLabel")
        self.chart_title.pack(anchor="w")
        ttk.Label(chart_panel, text="Rê chuột lên cột để xem số tiền.", style="Muted.Card.TLabel").pack(anchor="w", pady=(5, 0))
        self.chart = RevenueChart(chart_panel)
        self.chart.pack(fill="both", expand=True)
        top_panel = ttk.Frame(panels, style="Panel.TFrame", padding=15)
        top_panel.grid(row=0, column=1, sticky="nsew")
        ttk.Label(top_panel, text="10 món bán chạy nhất", style="Heading.TLabel").pack(anchor="w", pady=(0, 12))
        self.table = DataTable(top_panel, [("TenSP", "Sản phẩm", 155), ("SoLuong", "SL", 50), ("DoanhThu", "Doanh thu", 115)],
            height=4, empty_text="Chưa có món bán ra trong kỳ.")
        self.table.pack(fill="both", expand=True)
        self.period_label = ttk.Label(content, style="Subtitle.TLabel")
        self.period_label.grid(row=5, column=0, sticky="w", pady=(12, 0))

    def mode_changed(self, event=None):
        monthly = self.mode.get() == "Theo tháng"
        self.start.set(date.today().strftime("%Y-%m") if monthly else date.today().isoformat())
        self.end.set(date.today().isoformat())
        self.start_label.configure(text="  Tháng  " if monthly else "  Từ  ")
        self.end_entry.configure(state="disabled" if monthly else "normal")
        self.refresh()

    def quick_period(self, period):
        today = date.today()
        self.mode.set("Theo tháng" if period == "month" else "Theo ngày")
        self.start.set(today.strftime("%Y-%m") if period == "month" else
                       (today - timedelta(days=6) if period == "week" else today).isoformat())
        self.end.set(today.isoformat())
        self.start_label.configure(text="  Tháng  " if period == "month" else "  Từ  ")
        self.end_entry.configure(state="disabled" if period == "month" else "normal")
        self.refresh()

    def refresh(self):
        try:
            first, until = report_period(self.mode.get(), self.start.get(), self.end.get())
            total, count, products = self.service.statistics(first, until)
            series = self.service.revenue_series(first, until)
            self.result = (first, until, total, count, products)
            for card, value in zip(self.cards, [money(total), str(count), money(total / count if count else 0)]):
                card.set(value)
            monthly = (until - first).days > 31
            self.chart_title.configure(text="Doanh thu theo tháng (12 tháng cuối)" if monthly else "Doanh thu theo ngày", wraplength=390)
            self.chart.set_data(series, monthly)
            self.table.fill(products, "MaSP", lambda key, value: money(value) if key == "DoanhThu" else display(value))
            self.period_label.configure(text=f"{first:%d/%m/%Y} - {until - timedelta(days=1):%d/%m/%Y} - Tính theo ngày thanh toán, gồm trọn ngày cuối.")
        except Exception as error:
            report_error(self, error)

    def export(self):
        try:
            first, until = report_period(self.mode.get(), self.start.get(), self.end.get())
            total, count, products = self.service.statistics(first, until)
            filename = filedialog.asksaveasfilename(parent=self, title="Lưu báo cáo doanh thu", defaultextension=".csv",
                initialfile=f"doanh_thu_{first}.csv", filetypes=[("Tệp CSV", "*.csv")])
            if not filename:
                return
            with open(filename, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(["Từ ngày", str(first), "Đến ngày", str(until - timedelta(days=1))])
                writer.writerow(["Tổng doanh thu (đồng)", str(total), "Đơn đã thanh toán", count])
                writer.writerow([])
                writer.writerow(["Mã sản phẩm", "Sản phẩm", "Số lượng", "Doanh thu (đồng)"])
                for row in products:
                    name = row["TenSP"]
                    if name.lstrip().startswith(("=", "+", "-", "@")):
                        name = "'" + name
                    writer.writerow([row["MaSP"], name, row["SoLuong"], str(row["DoanhThu"])])
            notify(self, "Đã xuất báo cáo CSV.")
        except Exception as error:
            report_error(self, error)
