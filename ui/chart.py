"""Biểu đồ cột bằng Canvas, không cần thư viện vẽ bên ngoài."""
import tkinter as tk

from ui.common import money
from ui.theme import COLORS


class RevenueChart(tk.Canvas):
    def __init__(self, parent, height=210):
        super().__init__(parent, background="white", highlightthickness=0, height=height)
        self.series = []
        self.monthly = False
        self.bind("<Configure>", lambda event: self.draw())

    def set_data(self, series, monthly=False):
        self.series, self.monthly = series, monthly
        self.draw()

    def draw(self):
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        if width < 80 or height < 80:
            return
        left, right, top, bottom = 64, width - 20, 35, height - 36
        maximum = max([float(value) for _, value in self.series], default=0)
        scale = maximum * 1.18 if maximum else 100000
        for i in range(4):
            y = bottom - (bottom - top) * i / 3
            amount = scale * i / 3
            label = f"{amount / 1_000_000:.1f}tr" if scale >= 1_000_000 else f"{amount / 1000:.0f}k"
            self.create_line(left, y, right, y, fill=COLORS["line"], dash=(3, 4))
            self.create_text(left - 12, y, text=label, anchor="e", font=("Segoe UI", 9), fill=COLORS["muted"])
        if not self.series:
            return
        step = (right - left) / len(self.series)
        bar_width = min(44, step * 0.55)
        for index, (day, value) in enumerate(self.series):
            x = left + step * (index + 0.5)
            bar_top = bottom - (bottom - top) * float(value) / scale
            tag = f"bar_{index}"
            if value:
                self.create_rectangle(x - bar_width / 2, bar_top, x + bar_width / 2, bottom,
                                      fill=COLORS["primary"], outline="", tags=tag)
            else:
                self.create_rectangle(x - bar_width / 2, bottom - 2, x + bar_width / 2, bottom,
                                      fill=COLORS["line"], outline="", tags=tag)
            if len(self.series) <= 12 or index % 3 == 0 or index == len(self.series) - 1:
                self.create_text(x, bottom + 18, text=day.strftime("%m/%y" if self.monthly else "%d/%m"),
                                 font=("Segoe UI", 9), fill=COLORS["muted"])
            self.tag_bind(tag, "<Enter>", lambda event, d=day, v=value: self.show_value(d, v))
            self.tag_bind(tag, "<Leave>", lambda event: self.delete("tooltip"))
        if maximum == 0:
            self.create_text((left + right) / 2, (top + bottom) / 2,
                             text="Chưa có doanh thu trong kỳ",
                             fill=COLORS["muted"], font=("Segoe UI", 11))

    def show_value(self, day, value):
        self.delete("tooltip")
        text = f"{day.strftime('%m/%Y' if self.monthly else '%d/%m/%Y')}  -  {money(value)}"
        x, y = self.winfo_width() - 24, 14
        bbox_id = self.create_text(x, y, anchor="ne", text=text, fill=COLORS["primary"],
                                   font=("Segoe UI", 10, "bold"), tags="tooltip")
        bbox = self.bbox(bbox_id)
        if bbox:
            pad = 6
            background = self.create_rectangle(bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad,
                                  fill=COLORS["green_light"], outline=COLORS["line"], tags="tooltip")
            self.tag_lower(background, bbox_id)
