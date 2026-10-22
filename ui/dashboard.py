from datetime import date, timedelta
from tkinter import ttk

from models.service import PENDING
from ui.chart import RevenueChart
from ui.common import DataTable, MetricCard, ScrollFrame, display, greeting, report_error, money


class Dashboard(ttk.Frame):
    def __init__(self, parent, service, navigate, create_order):
        super().__init__(parent, padding=24)
        self.service = service
        scroll = ScrollFrame(self)
        scroll.pack(fill="both", expand=True)
        content = scroll.body
        content.columnconfigure(0, weight=1)

        greeting_label = ttk.Label(
            content,
            text=f"{greeting()}, {self.service.profile()['HoTen']}!",
            style="Subtitle.TLabel"
        )
        greeting_label.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        heading = ttk.Frame(content)
        heading.grid(row=1, column=0, sticky="ew", pady=(0, 18))
        ttk.Label(heading, text="Tổng quan hôm nay", style="Title.TLabel").pack(side="left")
        ttk.Button(heading, text="+ Tạo đơn hàng", style="Accent.TButton", command=create_order).pack(side="right")

        metrics = ttk.Frame(content)
        metrics.grid(row=2, column=0, sticky="ew", pady=(0, 18))
        self.cards = []
        for index, (title, hint, color) in enumerate([
            ("Doanh thu", "Đơn thanh toán hôm nay", "primary"),
            ("Hoá đơn", "Đã thanh toán hôm nay", "primary"),
            ("Đang phục vụ", "Đơn hàng cần xử lý", "gold"),
            ("Bàn trống", "Sẵn sàng đón khách", "primary"),
        ]):
            metrics.columnconfigure(index, weight=1, uniform="metrics")
            card = MetricCard(metrics, title, hint, color)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 10, 0))
            self.cards.append(card)

        charts = ttk.Frame(content)
        charts.grid(row=3, column=0, sticky="nsew", pady=(0, 18))
        charts.columnconfigure(0, weight=3, uniform="chart")
        charts.columnconfigure(1, weight=2, uniform="chart")

        chart_card = ttk.Frame(charts, style="Panel.TFrame", padding=16)
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        ttk.Label(chart_card, text="Doanh thu 7 ngày", style="Heading.TLabel").pack(anchor="w")
        self.chart = RevenueChart(chart_card, height=170)
        self.chart.pack(fill="both", expand=True)

        top_card = ttk.Frame(charts, style="Panel.TFrame", padding=16)
        top_card.grid(row=0, column=1, sticky="nsew")
        ttk.Label(top_card, text="Món bán chạy hôm nay", style="Heading.TLabel").pack(anchor="w", pady=(0, 14))
        self.top_items = ttk.Frame(top_card, style="Card.TFrame")
        self.top_items.pack(fill="both", expand=True)
        ttk.Button(top_card, text="Xem báo cáo", style="Card.TButton", command=lambda: navigate("statistics")).pack(anchor="w", pady=(8, 0))

        pending_card = ttk.Frame(content, style="Panel.TFrame", padding=14)
        pending_card.grid(row=4, column=0, sticky="nsew")
        heading = ttk.Frame(pending_card, style="Card.TFrame")
        heading.pack(fill="x", pady=(0, 10))
        ttk.Label(heading, text="Đơn đang phục vụ", style="Heading.TLabel").pack(side="left")
        ttk.Button(heading, text="Quản lý đơn", style="Card.TButton", command=lambda: navigate("orders")).pack(side="right")
        self.pending = DataTable(pending_card, [("MaDH", "Mã đơn", 65), ("TenBan", "Bàn", 125),
            ("KhachHang", "Khách hàng", 190), ("ThoiGianTao", "Giờ vào", 160), ("TongTien", "Tạm tính", 130)],
            height=3, empty_text="Chưa có đơn đang phục vụ.\nChọn Tạo đơn hàng để bắt đầu.")
        self.pending.pack(fill="both", expand=True)

    def refresh(self):
        try:
            today = date.today()
            total, count, products = self.service.statistics(today, today + timedelta(days=1))
            pending = self.service.list_orders(PENDING)
            tables = self.service.list_entities("tables")
            free = 0
            for table in tables:
                if table["TrangThai"] == "Trống":
                    free += 1
            for card, value in zip(self.cards, [money(total), str(count), str(len(pending)), f"{free} / {len(tables)}"]):
                card.set(value)
            self.chart.set_data(self.service.revenue_series(today - timedelta(days=6), today + timedelta(days=1)))

            for widget in self.top_items.winfo_children():
                widget.destroy()

            if not products:
                ttk.Label(self.top_items, text="Chưa có món được thanh toán.\nKết quả xuất hiện khi có doanh thu.",
                          style="Muted.Card.TLabel", justify="left").pack(anchor="w", pady=15)

            for index, product in enumerate(products[:3]):
                row = ttk.Frame(self.top_items, style="Card.TFrame")
                row.pack(fill="x", pady=(0, 12))
                ttk.Label(row, text=f"{index + 1:02}", style="Muted.Card.TLabel", width=4).pack(side="left")
                ttk.Label(row, text=product["TenSP"][:24], style="Card.TLabel").pack(side="left")
                ttk.Label(row, text=f"{product['SoLuong']} ly", style="Heading.TLabel").pack(side="right")

            self.pending.fill(pending, "MaDH", lambda key, value: money(value) if key == "TongTien" else
                              (value or "Khách lẻ") if key == "KhachHang" else display(value))
        except Exception as error:
            report_error(self, error)
