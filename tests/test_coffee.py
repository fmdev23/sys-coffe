"""Kiểm thử SQL Server thật trong database riêng, không chạm dữ liệu ứng dụng."""
import concurrent.futures
from datetime import date, timedelta
from decimal import Decimal
import re
import unittest
from unittest.mock import patch
import uuid

import pyodbc

import database_setup
import db_connection
from db_connection import connect
from models.service import login, AppError, CoffeeService, MANAGER, STAFF, PAID, PENDING, CANCELLED, phone, price, report_period
from security import hash_password, verify_password


def setUpModule():
    CoffeeTests.original_database = db_connection.DATABASE
    CoffeeTests.test_database = "CoffeeTest_" + uuid.uuid4().hex
    db_connection.DATABASE = CoffeeTests.test_database
    unittest.addModuleCleanup(cleanup_database)
    database_setup.setup()
    CoffeeTests.admin = login("admin", "Admin@123")


def cleanup_database():
    name = CoffeeTests.test_database
    # Chỉ tên ngẫu nhiên chính lớp này đã cấp phát mới được xoá.
    if not re.fullmatch(r"CoffeeTest_[0-9a-f]{32}", name) or name == CoffeeTests.original_database:
        raise RuntimeError("Unsafe test database cleanup")
    try:
        connection = db_connection.connect("master", autocommit=True)
        try:
            if connection.execute("SELECT 1 FROM sys.databases WHERE name = ?", name).fetchone():
                connection.execute(f"ALTER DATABASE [{name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
                connection.execute(f"DROP DATABASE [{name}]")
        finally:
            connection.close()
    finally:
        db_connection.DATABASE = CoffeeTests.original_database



class CoffeeTests(unittest.TestCase):


    def setUp(self):
        self.suffix = uuid.uuid4().hex[:10]

    def fixture(self):
        product = self.admin.save_entity("products", {"TenSP": "Món thử " + self.suffix,
            "DanhMuc": "Kiểm thử", "Gia": 35000, "MoTa": "Mô tả tiếng Việt", "TrangThai": 1})
        table = self.admin.save_entity("tables", {"TenBan": "Bàn thử " + self.suffix, "KhuVuc": "Sân vườn"})
        customer = self.admin.save_entity("customers", {"HoTen": "Khách " + self.suffix,
            "SDT": "0912345678", "DiemTichLuy": 0})
        return product, table, customer

    def employee_account(self, role=STAFF):
        employee = self.admin.save_entity("employees", {"HoTen": "Nhân viên " + self.suffix,
            "SDT": "+84912345678", "ChucVu": "Pha chế"})
        username = "nv_" + self.suffix
        account = self.admin.save_account(username, "NhanVien@123", role, employee)
        return employee, account, login(username, "NhanVien@123")

    def table_state(self, table):
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            result = (cursor.execute("SELECT TrangThai FROM dbo.Ban WHERE MaBan = ?", table).fetchval())
            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def test_password_hash_and_login(self):
        first = hash_password("Abcd@123")
        second = hash_password("Abcd@123")
        self.assertNotEqual(first, second)
        self.assertTrue(verify_password("Abcd@123", first))
        self.assertFalse(verify_password("wrong", first))
        self.assertFalse(verify_password("wrong", "malformed"))
        with self.assertRaises(ValueError):
            hash_password("short")
        with self.assertRaises(AppError):
            login("admin", "wrong")
        with self.assertRaises(AppError):
            login("admin' OR 1=1--", "wrong")

    def test_setup_idempotent(self):
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            before = [cursor.execute(f"SELECT COUNT(*) FROM dbo.{table}").fetchval()
                      for table in ("TaiKhoan", "SanPham", "Ban", "NhanVien")]
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        self.assertFalse(database_setup.setup())
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            after = [cursor.execute(f"SELECT COUNT(*) FROM dbo.{table}").fetchval()
                     for table in ("TaiKhoan", "SanPham", "Ban", "NhanVien")]
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        self.assertEqual(before, after)
        self.assertEqual(login("admin", "Admin@123").profile()["VaiTro"], MANAGER)

    def test_validation(self):
        for invalid in ("0", "-1", "abc", "NaN", "Infinity", "1.23", "1000000001"):
            with self.subTest(invalid=invalid), self.assertRaises(AppError):
                price(invalid)
        self.assertEqual(price("35000"), Decimal("35000.00"))
        with self.assertRaises(AppError):
            phone("1234")
        self.assertEqual(phone("0912 345678"), "0912345678")
        with self.assertRaises(AppError):
            self.admin.save_entity("products", {"TenSP": "", "Gia": 10})
        with self.assertRaises(AppError):
            self.admin.save_entity("customers", {"HoTen": "Khách", "DiemTichLuy": "1.5"})

    def test_crud_all_entities(self):
        data = {
            "products": ("MaSP", {"TenSP": "Trà ' Việt " + self.suffix, "DanhMuc": "Trà", "Gia": 27000,
                                   "MoTa": "Có dấu", "TrangThai": 1}, "TenSP"),
            "tables": ("MaBan", {"TenBan": "Bàn " + self.suffix, "KhuVuc": "Ngoài trời"}, "KhuVuc"),
            "employees": ("MaNV", {"HoTen": "Nhân viên thử", "SDT": "0912345678", "ChucVu": "Phục vụ"}, "HoTen"),
            "customers": ("MaKH", {"HoTen": "Khách thử", "SDT": "", "DiemTichLuy": 0}, "HoTen"),
        }
        for entity, (key, values, field) in data.items():
            with self.subTest(entity=entity):
                record = self.admin.save_entity(entity, values)
                self.assertIn(record, [r[key] for r in self.admin.list_entities(entity)])
                values[field] = "Đã cập nhật " + self.suffix
                self.admin.save_entity(entity, values, record)
                saved = next(r for r in self.admin.list_entities(entity) if r[key] == record)
                self.assertEqual(saved[field], values[field])
                self.admin.delete_entity(entity, record)
                self.assertNotIn(record, [r[key] for r in self.admin.list_entities(entity)])

    def test_account_crud_password_and_disabled_session(self):
        employee, account, staff = self.employee_account()
        staff.change_password("NhanVien@123", "NewPass@123")
        with self.assertRaises(AppError):
            login("nv_" + self.suffix, "NhanVien@123")
        login("nv_" + self.suffix, "NewPass@123")
        self.admin.save_account("nv_" + self.suffix, "", STAFF, employee, 0, account)
        with self.assertRaises(AppError):
            staff.order_options()
        self.admin.save_account("nv_" + self.suffix, "Reset@123", STAFF, employee, 1, account)
        login("nv_" + self.suffix, "Reset@123")
        self.admin.delete_account(account)
        self.admin.delete_entity("employees", employee)

    def test_protect_current_manager(self):
        profile = self.admin.profile()
        with self.assertRaises(AppError):
            self.admin.delete_account(profile["MaTK"])
        with self.assertRaises(AppError):
            self.admin.save_account("admin", "", STAFF, profile["MaNV"], 1, profile["MaTK"])
        with self.assertRaises(AppError):
            self.admin.save_account("admin", "", MANAGER, profile["MaNV"], 0, profile["MaTK"])

    def test_staff_permissions_enforced_in_service(self):
        _, _, staff = self.employee_account()
        product, table, customer = self.fixture()
        self.assertTrue(staff.list_entities("products"))
        self.assertTrue(staff.list_entities("tables"))
        denied = [lambda: staff.list_entities("employees"), lambda: staff.list_entities("customers"),
            lambda: staff.list_accounts(), lambda: staff.statistics(date.today(), date.today() + timedelta(days=1)),
            lambda: staff.revenue_series(date.today(), date.today() + timedelta(days=1)),
            lambda: staff.delete_entity("products", product),
            lambda: staff.save_entity("tables", {"TenBan": "Forbidden", "KhuVuc": "Test"}),
            lambda: staff.save_account("forbidden", "Password@123", MANAGER, 1)]
        for action in denied:
            with self.assertRaises(AppError):
                action()
        order = staff.save_order(table, customer, [(product, 2)])
        with self.assertRaises(AppError):
            staff.delete_order(order)
        staff.finish_order(order, pay=False)
        self.assertEqual(staff.get_order(order)[0]["TrangThai"], CANCELLED)

    def test_order_create_edit_move_and_delete(self):
        product, table, customer = self.fixture()
        order = self.admin.save_order(table, customer, [(product, 1), (product, 2)])
        saved, items = self.admin.get_order(order)
        self.assertEqual(saved["TongTien"], Decimal(105000))
        self.assertEqual(items[0]["SoLuong"], 3)
        self.assertEqual(self.table_state(table), "Đang phục vụ")
        second_table = self.admin.save_entity("tables", {"TenBan": "Chuyển " + self.suffix, "KhuVuc": "Tầng 2"})
        self.admin.save_order(second_table, None, [(product, 4)], order, saved["PhienBan"])
        updated, _ = self.admin.get_order(order)
        self.assertEqual(updated["TongTien"], Decimal(140000))
        self.assertIsNone(updated["MaKH"])
        self.assertEqual(self.table_state(table), "Trống")
        self.assertEqual(self.table_state(second_table), "Đang phục vụ")
        self.admin.delete_order(order)
        self.assertEqual(self.table_state(second_table), "Trống")
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            self.assertEqual(cursor.execute("SELECT COUNT(*) FROM dbo.ChiTietDonHang WHERE MaDH = ?", order).fetchval(), 0)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def test_order_failure_rolls_back(self):
        product, table, customer = self.fixture()
        for cart in ([], [(product, 0)], [(product, "1.5")], [(product, 1000)], [(product, 1), (2147483647, 1)]):
            with self.assertRaises(AppError):
                self.admin.save_order(table, customer, cart)
            self.assertEqual(self.table_state(table), "Trống")
        order = self.admin.save_order(table, customer, [(product, 1)])
        before, _ = self.admin.get_order(order)
        with self.assertRaises(AppError):
            self.admin.save_order(table, customer, [(product, 2), (999999999, 1)], order, before["PhienBan"])
        after, lines = self.admin.get_order(order)
        self.assertEqual(after["TongTien"], before["TongTien"])
        self.assertEqual(lines[0]["SoLuong"], 1)

    def test_snapshot_price_and_discontinued_product(self):
        product, table, customer = self.fixture()
        order = self.admin.save_order(table, customer, [(product, 2)])
        self.admin.save_entity("products", {"TenSP": "Giá mới", "DanhMuc": "Cà phê", "Gia": 99000,
                                           "MoTa": "", "TrangThai": 1}, product)
        saved, _ = self.admin.get_order(order)
        self.admin.save_order(table, customer, [(product, 3)], order, saved["PhienBan"])
        updated, lines = self.admin.get_order(order)
        self.assertEqual(updated["TongTien"], Decimal(105000))
        self.assertEqual(lines[0]["DonGia"], Decimal(35000))
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            cursor.execute("UPDATE dbo.SanPham SET TrangThai = 0 WHERE MaSP = ?", product)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        with self.assertRaises(AppError):
            self.admin.save_order(table, customer, [(product, 4)], order, updated["PhienBan"])
        self.admin.save_order(table, customer, [(product, 1)], order, updated["PhienBan"])

    def test_payment_points_and_preserve_history(self):
        product, table, customer = self.fixture()
        order = self.admin.save_order(table, customer, [(product, 3)])
        self.admin.finish_order(order)
        saved, _ = self.admin.get_order(order)
        self.assertEqual(saved["TrangThai"], PAID)
        self.assertIsNotNone(saved["ThoiGianThanhToan"])
        self.assertEqual(self.table_state(table), "Trống")
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            self.assertEqual(cursor.execute("SELECT DiemTichLuy FROM dbo.KhachHang WHERE MaKH = ?", customer).fetchval(), 10)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        with self.assertRaises(AppError):
            self.admin.finish_order(order)
        with self.assertRaises(AppError):
            self.admin.delete_order(order)
        with self.assertRaises(pyodbc.IntegrityError):
            self.admin.delete_entity("products", product)

    def test_cancel_and_delete(self):
        product, table, customer = self.fixture()
        order = self.admin.save_order(table, customer, [(product, 2)])
        self.admin.finish_order(order, pay=False)
        self.assertEqual(self.table_state(table), "Trống")
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            self.assertEqual(cursor.execute("SELECT DiemTichLuy FROM dbo.KhachHang WHERE MaKH = ?", customer).fetchval(), 0)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        self.admin.delete_order(order)
        with self.assertRaises(AppError):
            self.admin.get_order(order)

    def test_payment_database_failure_rolls_back_all_changes(self):
        product, table, customer = self.fixture()
        order = self.admin.save_order(table, customer, [(product, 2)])
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            cursor.execute("UPDATE dbo.KhachHang SET DiemTichLuy = 2147483647 WHERE MaKH = ?", customer)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        # Lỗi SQL xảy ra sau UPDATE trạng thái đơn phải hoàn tác cả giao dịch.
        with self.assertRaises(pyodbc.Error):
            self.admin.finish_order(order)
        saved, _ = self.admin.get_order(order)
        self.assertEqual(saved["TrangThai"], PENDING)
        self.assertIsNone(saved["ThoiGianThanhToan"])
        self.assertEqual(saved["DiemDaCong"], 0)
        self.assertEqual(self.table_state(table), "Đang phục vụ")
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            self.assertEqual(cursor.execute("SELECT DiemTichLuy FROM dbo.KhachHang WHERE MaKH = ?", customer).fetchval(),
                             2147483647)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def test_stale_order_cannot_overwrite_or_pay(self):
        product, table, customer = self.fixture()
        order = self.admin.save_order(table, customer, [(product, 1)])
        version = self.admin.get_order(order)[0]["PhienBan"]
        self.admin.save_order(table, customer, [(product, 2)], order, version)
        with self.assertRaises(AppError):
            self.admin.save_order(table, customer, [(product, 3)], order, version)
        with self.assertRaises(AppError):
            self.admin.finish_order(order, expected_version=version)
        with self.assertRaises(AppError):
            self.admin.delete_order(order, expected_version=version)

    def test_concurrent_table_reservation(self):
        product, table, customer = self.fixture()

        def create():
            try:
                return self.admin.save_order(table, customer, [(product, 1)])
            except AppError:
                return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: create(), range(2)))
        self.assertEqual(sum(result is not None for result in results), 1)
        self.assertEqual(self.table_state(table), "Đang phục vụ")

    def test_concurrent_payment_only_once(self):
        product, table, customer = self.fixture()
        order = self.admin.save_order(table, customer, [(product, 2)])

        def pay():
            try:
                self.admin.finish_order(order)
                return True
            except AppError:
                return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: pay(), range(2)))
        self.assertEqual(results.count(True), 1)
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            self.assertEqual(cursor.execute("SELECT DiemTichLuy FROM dbo.KhachHang WHERE MaKH = ?", customer).fetchval(), 7)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def test_statistics_dates_month_and_excluded_statuses(self):
        product, table, customer = self.fixture()
        order = self.admin.save_order(table, customer, [(product, 2)])
        self.admin.finish_order(order)
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            cursor.execute("""UPDATE dbo.DonHang SET ThoiGianTao = '20400101',
                ThoiGianThanhToan = '20400229 23:59:59' WHERE MaDH = ?""", order)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        first, until = report_period("Theo tháng", "2040-02")
        self.assertEqual(until, date(2040, 3, 1))
        total, count, products = self.admin.statistics(first, until)
        self.assertEqual((total, count), (Decimal(70000), 1))
        self.assertEqual(products[0]["SoLuong"], 2)
        series = self.admin.revenue_series(first, until)
        self.assertEqual(len(series), 29)
        self.assertEqual(sum(amount for _, amount in series), total)
        self.assertEqual(series[0][1], Decimal(0))
        self.assertEqual(series[-1][1], Decimal(70000))
        monthly = self.admin.revenue_series(date(2040, 1, 1), date(2040, 4, 1))
        self.assertEqual(monthly, [(date(2040, 1, 1), Decimal(0)), (date(2040, 2, 1), Decimal(70000)),
                                   (date(2040, 3, 1), Decimal(0))])
        day = report_period("Theo ngày", "2040-02-29", "2040-02-29")
        self.assertEqual(self.admin.statistics(*day)[:2], (Decimal(70000), 1))
        self.assertEqual(self.admin.statistics(*report_period("Theo tháng", "2040-01"))[:2], (Decimal(0), 0))
        pending = self.admin.save_order(table, None, [(product, 10)])
        self.assertEqual(self.admin.statistics(first, until)[:2], (Decimal(70000), 1))
        self.admin.finish_order(pending, pay=False)
        self.assertEqual(self.admin.statistics(first, until)[:2], (Decimal(70000), 1))
        with self.assertRaises(AppError):
            report_period("Theo ngày", "2040-02-30", "2040-03-01")
        with self.assertRaises(AppError):
            report_period("Theo ngày", "2040-03-02", "2040-03-01")

    def test_rounded_controls_mouse_keyboard_and_disabled_state(self):
        import tkinter as tk
        from tkinter import ttk
        from main import CoffeeApp

        app = CoffeeApp()
        app.screen.destroy()
        app.geometry("700x580")
        clicked = []
        checked = tk.BooleanVar(app, False)
        button = ttk.Button(app, text="Lưu", style="Accent.TButton", command=lambda: clicked.append(True))
        combo = ttk.Combobox(app, values=["Một", "Hai"])
        spin = ttk.Spinbox(app, from_=1, to=9)
        check = ttk.Checkbutton(app, text="Hiện mật khẩu", variable=checked)
        for widget in (button, combo, spin, check):
            widget.pack(pady=8)
        spin.set("1")

        def click(widget, element=None):
            app.update()
            x, y = widget.winfo_width() // 2, widget.winfo_height() // 2
            if element:
                point = next(((px, py) for px in range(widget.winfo_width())
                              for py in range(widget.winfo_height())
                              if widget.identify(px, py).endswith(element)), None)
                self.assertIsNotNone(point, element)
                x, y = point
            widget.event_generate("<ButtonPress-1>", x=x, y=y)
            widget.event_generate("<ButtonRelease-1>", x=x, y=y)
            app.update()

        try:
            click(button)
            self.assertEqual(len(clicked), 1)
            button.focus_force()
            app.update()
            button.event_generate("<KeyPress-space>")
            button.event_generate("<KeyRelease-space>")
            app.update()
            self.assertEqual(len(clicked), 2)
            button.state(["disabled"])
            click(button)
            self.assertEqual(len(clicked), 2)
            click(combo, "downarrow")
            popup = app.tk.call("ttk::combobox::PopdownWindow", str(combo))
            self.assertTrue(app.tk.getboolean(app.tk.call("winfo", "viewable", popup)))
            app.tk.call("ttk::combobox::Unpost", str(combo))
            click(spin, "uparrow")
            self.assertEqual(spin.get(), "2")
            click(spin, "downarrow")
            self.assertEqual(spin.get(), "1")
            spin.state(["disabled"])
            click(spin, "uparrow")
            self.assertEqual(spin.get(), "1")
            click(check)
            self.assertTrue(checked.get())
            check.state(["disabled"])
            click(check)
            self.assertTrue(checked.get())
        finally:
            app.destroy()

    def test_tkinter_login_pages_forms_and_order_flow(self):
        from main import CoffeeApp
        from ui.main_window import MainWindow
        from ui.order_tab import OrderEditor

        product, table, customer = self.fixture()
        _, _, staff = self.employee_account()
        app = CoffeeApp()
        errors = []
        with patch("tkinter.messagebox.showerror", side_effect=lambda *args, **kwargs: errors.append(args)), \
             patch("tkinter.messagebox.showinfo"), patch("tkinter.messagebox.askyesno", return_value=True):
            try:
                app.update()
                app.screen.username.set("admin")
                app.screen.password.set("Admin@123")
                app.screen.login()
                app.update()
                self.assertIsInstance(app.screen, MainWindow)
                self.assertEqual(len(app.screen.pages), 8)
                app.geometry("1140x730")
                app.update()
                for button in app.screen.nav_buttons.values():
                    self.assertTrue(button.winfo_ismapped(), button.cget("text"))
                    self.assertLess(button.winfo_rooty() + button.winfo_height(),
                                    app.winfo_rooty() + app.winfo_height())
                for name, tab in app.screen.pages.items():
                    app.screen.show_page(name)
                    app.update()
                    from tkinter import ttk
                    for widget in tab.winfo_children():
                        if isinstance(widget, ttk.Label):
                            self.assertTrue(widget.winfo_ismapped(), widget.cget("text"))
                app.screen.show_page("products")
                product_tab = app.screen.pages["products"]
                dialog = product_tab.add()
                dialog.variables["TenSP"].set("Món từ giao diện")
                dialog.variables["DanhMuc"].set("Thử giao diện")
                dialog.variables["Gia"].set("45000")
                dialog.save()
                app.update()
                product_tab.table.tree.selection_set(str(product))
                dialog = product_tab.edit()
                dialog.variables["MoTa"].set("Đã sửa trên giao diện")
                dialog.save()
                app.screen.show_page("orders")
                order_tab = app.screen.pages["orders"]
                editor = order_tab.add()
                app.update()
                self.assertTrue(editor.total_label.winfo_ismapped())
                self.assertTrue(editor.save_button.instate(["disabled"]))
                self.assertTrue(editor.pay_button.instate(["disabled"]))
                editor.table_var.set(next(k for k, v in editor.table_options.items() if v == table))
                editor.customer_var.set(next(k for k, v in editor.customer_options.items() if v == customer))
                editor.add_item(product)
                editor.add_item(product)
                self.assertIn("70.000", editor.total_label.cget("text"))
                second = next(key for key in editor.products if key != product)
                editor.add_item(second)
                editor.geometry("1050x660")
                app.update()
                for key in (product, second):
                    bounds = editor.cart_table.tree.bbox(str(key))
                    self.assertTrue(bounds, "Món bị che ở cửa sổ nhỏ")
                    self.assertLessEqual(bounds[1] + bounds[3], editor.cart_table.tree.winfo_height())
                self.assertTrue(editor.save_button.winfo_ismapped())
                self.assertTrue(editor.pay_button.winfo_ismapped())
                editor.remove_item()
                editor.search.set("mon thu")
                self.assertTrue(editor.menu_cards.body.winfo_children())
                editor.save()
                app.update()
                saved = next(r for r in order_tab.data if r["MaBan"] == table)
                order_tab.table.tree.selection_set(str(saved["MaDH"]))
                payment = order_tab.pay()
                payment.received.set("50000")
                self.assertTrue(payment.confirm_button.instate(["disabled"]))
                payment.received.set("100000")
                self.assertIn("30.000", payment.change_label.cget("text"))
                payment.confirm()
                app.update()
                editor = OrderEditor(order_tab, self.admin, app.screen.refresh_all, saved["MaDH"])
                self.assertFalse(editor.editable)
                app.update()
                editor.destroy()
                app.screen.show_page("accounts")
                account_tab = app.screen.pages["accounts"]
                account_tab.table.tree.selection_set(str(self.admin.account_id))
                dialog = account_tab.edit()
                app.update()
                dialog.destroy()
                dialog = app.screen.change_password()
                app.update()
                dialog.destroy()
                app.screen.show_page("statistics")
                app.screen.pages["statistics"].mode.set("Theo tháng")
                app.screen.pages["statistics"].mode_changed()
                app.screen.logout()
                app.update()
                app.show_main(staff)
                app.update()
                self.assertEqual(set(app.screen.pages), {"orders", "products", "tables"})
                self.assertEqual(app.screen.current_page, "tables")
                employee_editor = app.screen.open_table(table)
                self.assertEqual(employee_editor.table_options[employee_editor.table_var.get()], table)
                employee_editor.destroy()
                self.assertEqual(errors, [])
            finally:
                app.destroy()


if __name__ == "__main__":
    unittest.main(verbosity=2)
