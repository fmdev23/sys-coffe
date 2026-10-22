"""Điểm chạy: python main.py."""
import sys

sys.dont_write_bytecode = True

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import tkinter as tk

from ui.common import report_error
from ui.theme import configure_style
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


class CoffeeApp(tk.Tk):
    def __init__(self):
        # Giữ chữ sắc nét khi Windows đặt tỉ lệ màn hình 125% hoặc 150%.
        if sys.platform == "win32":
            import ctypes
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except (OSError, AttributeError):
                pass
        super().__init__()
        configure_style(self)
        self.screen = None
        self.show_login()

    def clear(self):
        for child in self.winfo_children():
            if isinstance(child, tk.Toplevel):
                child.destroy()
        if self.screen is not None:
            self.screen.destroy()

    def show_login(self):
        self.clear()
        self.screen = LoginWindow(self, self.show_main)

    def show_main(self, service):
        # Xác nhận phiên trước khi thay màn hình.
        service.profile()
        self.clear()
        try:
            self.screen = MainWindow(self, service, self.show_login)
        except Exception:
            self.show_login()
            raise

    def report_callback_exception(self, exc_type, value, traceback):
        logging.error("Lỗi sự kiện giao diện", exc_info=(exc_type, value, traceback))
        report_error(self, value)


def main():
    # Chỉ tạo log khi có lỗi, giới hạn kích thước ngay trong thư mục dự án.
    handler = RotatingFileHandler(Path(__file__).with_name("coffee.log"), maxBytes=256_000,
                                  backupCount=1, encoding="utf-8", delay=True)
    logging.basicConfig(handlers=[handler], level=logging.ERROR,
                        format="%(asctime)s %(levelname)s %(message)s")
    app = CoffeeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
