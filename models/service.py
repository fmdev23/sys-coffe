"""Nghiệp vụ, kiểm tra quyền và SQL tham số hoá cho mọi thao tác."""
import calendar
import re
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from db_connection import rows, connect
from security import hash_password, verify_password

MANAGER = "Quản lý"
STAFF = "Nhân viên"
PENDING = "Đang xử lý"
PAID = "Đã thanh toán"
CANCELLED = "Đã huỷ"


class AppError(ValueError):
    """Lỗi nghiệp vụ có thể hiển thị trực tiếp cho người dùng."""


def required(value, label, limit):
    value = str(value or "").strip()
    if not value:
        raise AppError(f"Vui lòng nhập {label.lower()}.")
    if len(value) > limit:
        raise AppError(f"{label} không được quá {limit} ký tự.")
    return value


def integer(value, label, minimum=0, maximum=1_000_000_000):
    if not re.fullmatch(r"[0-9]+", str(value).strip()):
        raise AppError(f"{label} phải là số nguyên từ {minimum:,} đến {maximum:,}.")
    result = int(str(value).strip())
    if not minimum <= result <= maximum:
        raise AppError(f"{label} phải từ {minimum:,} đến {maximum:,}.")
    return result


def price(value):
    try:
        result = Decimal(str(value).strip())
        if not result.is_finite() or not 0 < result <= 1_000_000_000:
            raise InvalidOperation
        if result != result.to_integral_value():
            raise AppError("Giá tiền phải là số nguyên đồng (ví dụ: 35000).")
        return result.quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError) as error:
        if isinstance(error, AppError):
            raise
        raise AppError("Giá phải là số lớn hơn 0 và không quá 1.000.000.000 đồng.") from error


def phone(value):
    value = str(value or "").strip().replace(" ", "")
    if value and not re.fullmatch(r"(?:0[0-9]{9}|\+84[0-9]{9})", value):
        raise AppError("Số điện thoại gồm 10 chữ số bắt đầu bằng 0 hoặc +84 và 9 chữ số.")
    return value


def report_period(mode, start, end=""):
    try:
        if mode == "Theo tháng":
            first = datetime.strptime(start.strip(), "%Y-%m").date()
            last = first.replace(day=calendar.monthrange(first.year, first.month)[1])
        else:
            first = datetime.strptime(start.strip(), "%Y-%m-%d").date()
            last = datetime.strptime(end.strip() or start.strip(), "%Y-%m-%d").date()
        if first > last:
            raise AppError("Ngày bắt đầu phải trước hoặc bằng ngày kết thúc.")
        return first, last + timedelta(days=1)
    except (ValueError, OverflowError) as error:
        if isinstance(error, AppError):
            raise
        raise AppError("Ngày dùng định dạng YYYY-MM-DD, tháng dùng YYYY-MM (ví dụ 2026-09).") from error


# Chỉ các tên bảng/cột trong danh sách cố định này mới được ghép vào SQL.
ENTITIES = {
    "products": ("SanPham", "MaSP", ("TenSP", "DanhMuc", "Gia", "MoTa", "TrangThai")),
    "tables": ("Ban", "MaBan", ("TenBan", "KhuVuc")),
    "employees": ("NhanVien", "MaNV", ("HoTen", "SDT", "ChucVu")),
    "customers": ("KhachHang", "MaKH", ("HoTen", "SDT", "DiemTichLuy")),
}


def _lock(cursor, resource):
    cursor.execute("""DECLARE @result INT;
        EXEC @result = sys.sp_getapplock @Resource = ?, @LockMode = 'Exclusive',
            @LockOwner = 'Transaction', @LockTimeout = 10000;
        IF @result < 0 THROW 50002, 'He thong dang ban. Vui long thu lai.', 1;""", resource)


def login(username, password):
    connection = connect()
    try:
        connection.execute("SET XACT_ABORT ON")
        cursor = connection.cursor()
        result = cursor.execute("""SELECT MaTK, MatKhauHash, HoatDong
            FROM dbo.TaiKhoan WHERE TenDangNhap = ?""", str(username).strip()).fetchone()
        if not result or not verify_password(password, result.MatKhauHash) or not result.HoatDong:
            raise AppError("Tên đăng nhập hoặc mật khẩu không đúng, hoặc tài khoản đã bị khoá.")
        result = (CoffeeService(result.MaTK))
        connection.commit()
        return result
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


class CoffeeService:
    def __init__(self, account_id):
        self.account_id = account_id

    def _authorize(self, cursor, manager=False):
        cursor.execute("""SELECT t.MaTK, t.TenDangNhap, t.VaiTro, t.MaNV, n.HoTen
            FROM dbo.TaiKhoan t JOIN dbo.NhanVien n ON n.MaNV = t.MaNV
            WHERE t.MaTK = ? AND t.HoatDong = 1""", self.account_id)
        result = rows(cursor)
        if not result:
            raise AppError("Tài khoản không còn hoạt động. Vui lòng đăng nhập lại.")
        if manager and result[0]["VaiTro"] != MANAGER:
            raise AppError("Chỉ Quản lý mới có quyền thực hiện thao tác này.")
        return result[0]

    def profile(self):
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            result = (self._authorize(cursor))
            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def list_entities(self, entity):
        table, key, _ = ENTITIES[entity]
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            self._authorize(cursor, manager=entity in ("employees", "customers"))
            if entity == "employees":
                cursor.execute("""SELECT n.*, t.TenDangNhap FROM dbo.NhanVien n
                    LEFT JOIN dbo.TaiKhoan t ON n.MaNV = t.MaNV ORDER BY n.MaNV""")
            else:
                cursor.execute(f"SELECT * FROM dbo.{table} ORDER BY {key}")
            result = (rows(cursor))
            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def save_entity(self, entity, values, record_id=None):
        table, key, columns = ENTITIES[entity]
        data = dict(values)
        if entity == "products":
            data["TenSP"] = required(data.get("TenSP"), "Tên sản phẩm", 100)
            data["DanhMuc"] = required(data.get("DanhMuc"), "Danh mục", 60)
            data["Gia"] = price(data.get("Gia"))
            data["MoTa"] = str(data.get("MoTa", "")).strip()
            if len(data["MoTa"]) > 500:
                raise AppError("Mô tả không được quá 500 ký tự.")
            data["TrangThai"] = integer(data.get("TrangThai", 1), "Trạng thái bán", 0, 1)
        elif entity == "tables":
            data["TenBan"] = required(data.get("TenBan"), "Tên bàn", 50)
            data["KhuVuc"] = required(data.get("KhuVuc"), "Khu vực", 100)
        else:
            data["HoTen"] = required(data.get("HoTen"), "Họ tên", 100)
            data["SDT"] = phone(data.get("SDT"))
            if entity == "employees":
                data["ChucVu"] = required(data.get("ChucVu"), "Chức vụ", 60)
            else:
                data["DiemTichLuy"] = integer(data.get("DiemTichLuy", 0), "Điểm tích luỹ")
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            self._authorize(cursor, manager=True)
            params = [data[c] for c in columns]
            if record_id is None:
                placeholders = ", ".join(['?' for _ in columns])
                result = (cursor.execute(
                    f"INSERT dbo.{table} ({', '.join(columns)}) OUTPUT INSERTED.{key} "
                    f"VALUES ({placeholders})", *params).fetchval())
                connection.commit()
                return result
            cursor.execute(f"UPDATE dbo.{table} SET {', '.join([c + ' = ?' for c in columns])} "
                           f"WHERE {key} = ?", *params, record_id)
            if cursor.rowcount != 1:
                raise AppError("Bản ghi đã bị xoá. Vui lòng làm mới danh sách.")
            result = (record_id)
            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def delete_entity(self, entity, record_id):
        table, key, _ = ENTITIES[entity]
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            self._authorize(cursor, manager=True)
            cursor.execute(f"DELETE FROM dbo.{table} WHERE {key} = ?", record_id)
            if cursor.rowcount != 1:
                raise AppError("Bản ghi không còn tồn tại.")
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def list_accounts(self):
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            self._authorize(cursor, manager=True)
            cursor.execute("""SELECT t.MaTK, t.TenDangNhap, t.MaNV, n.HoTen, t.VaiTro, t.HoatDong
                FROM dbo.TaiKhoan t JOIN dbo.NhanVien n ON n.MaNV = t.MaNV ORDER BY t.MaTK""")
            result = (rows(cursor))
            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def save_account(self, username, password, role, employee_id, active=1, account_id=None):
        username = required(username, "Tên đăng nhập", 50)
        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,50}", username):
            raise AppError("Tên đăng nhập dài 3–50 ký tự, chỉ gồm chữ không dấu, số, _, . hoặc -.")
        if role not in (MANAGER, STAFF):
            raise AppError("Vai trò không hợp lệ.")
        active = integer(active, "Trạng thái hoạt động", 0, 1)
        password_hash = hash_password(password) if password else None
        if account_id is None and not password_hash:
            raise AppError("Vui lòng nhập mật khẩu cho tài khoản mới.")
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            _lock(cursor, "CoffeeAccounts")
            self._authorize(cursor, manager=True)
            if account_id is not None:
                current = cursor.execute("SELECT VaiTro, HoatDong FROM dbo.TaiKhoan WHERE MaTK = ?",
                                         account_id).fetchone()
                if not current:
                    raise AppError("Tài khoản không còn tồn tại.")
                if account_id == self.account_id and (role != MANAGER or not active):
                    raise AppError("Không thể tự khoá hoặc hạ quyền tài khoản đang đăng nhập.")
                if current.VaiTro == MANAGER and current.HoatDong and (role != MANAGER or not active):
                    self._ensure_other_manager(cursor, account_id)
                cursor.execute("""UPDATE dbo.TaiKhoan SET TenDangNhap = ?, VaiTro = ?,
                    MaNV = ?, HoatDong = ?, MatKhauHash = COALESCE(?, MatKhauHash) WHERE MaTK = ?""",
                    username, role, employee_id, active, password_hash, account_id)
                result = (account_id)
                connection.commit()
                return result
            result = (cursor.execute("""INSERT dbo.TaiKhoan
                (TenDangNhap, MatKhauHash, VaiTro, MaNV, HoatDong)
                OUTPUT INSERTED.MaTK VALUES (?, ?, ?, ?, ?)""",
                username, password_hash, role, employee_id, active).fetchval())
            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _ensure_other_manager(self, cursor, account_id):
        count = cursor.execute("""SELECT COUNT(*) FROM dbo.TaiKhoan
            WHERE VaiTro = ? AND HoatDong = 1 AND MaTK <> ?""", MANAGER, account_id).fetchval()
        if not count:
            raise AppError("Phải giữ ít nhất một tài khoản Quản lý đang hoạt động.")

    def delete_account(self, account_id):
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            _lock(cursor, "CoffeeAccounts")
            self._authorize(cursor, manager=True)
            if account_id == self.account_id:
                raise AppError("Không thể xoá tài khoản đang đăng nhập.")
            self._ensure_other_manager(cursor, account_id)
            cursor.execute("DELETE FROM dbo.TaiKhoan WHERE MaTK = ?", account_id)
            if cursor.rowcount != 1:
                raise AppError("Tài khoản không còn tồn tại.")
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def change_password(self, old_password, new_password):
        new_hash = hash_password(new_password)
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            _lock(cursor, "CoffeeAccounts")
            self._authorize(cursor)
            current = cursor.execute("SELECT MatKhauHash FROM dbo.TaiKhoan WHERE MaTK = ?",
                                     self.account_id).fetchval()
            if not verify_password(old_password, current):
                raise AppError("Mật khẩu hiện tại không đúng.")
            cursor.execute("UPDATE dbo.TaiKhoan SET MatKhauHash = ? WHERE MaTK = ?",
                           new_hash, self.account_id)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def order_options(self):
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            self._authorize(cursor)
            cursor.execute("SELECT * FROM dbo.Ban ORDER BY MaBan")
            tables = rows(cursor)
            cursor.execute("SELECT MaKH, HoTen, SDT FROM dbo.KhachHang ORDER BY HoTen")
            customers = rows(cursor)
            cursor.execute("SELECT * FROM dbo.SanPham WHERE TrangThai = 1 ORDER BY TenSP")
            result = (tables, customers, rows(cursor))
            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def list_orders(self, status="Tất cả"):
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            self._authorize(cursor)
            query = """SELECT d.*, b.TenBan, k.HoTen AS KhachHang, n.HoTen AS NhanVien
                FROM dbo.DonHang d JOIN dbo.Ban b ON b.MaBan = d.MaBan
                LEFT JOIN dbo.KhachHang k ON k.MaKH = d.MaKH
                JOIN dbo.NhanVien n ON n.MaNV = d.MaNV"""
            if status != "Tất cả":
                cursor.execute(query + " WHERE d.TrangThai = ? ORDER BY d.MaDH DESC", status)
            else:
                cursor.execute(query + " ORDER BY d.MaDH DESC")
            result = (rows(cursor))
            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def get_order(self, order_id):
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            self._authorize(cursor)
            cursor.execute("SELECT * FROM dbo.DonHang WHERE MaDH = ?", order_id)
            order = rows(cursor)
            if not order:
                raise AppError("Đơn hàng không còn tồn tại.")
            cursor.execute("SELECT * FROM dbo.ChiTietDonHang WHERE MaDH = ? ORDER BY MaCTDH", order_id)
            result = (order[0], rows(cursor))
            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def save_order(self, table_id, customer_id, cart, order_id=None, expected_version=None):
        if not cart:
            raise AppError("Đơn hàng phải có ít nhất một sản phẩm.")
        quantities = {}
        for product_id, quantity in cart:
            product_id = integer(product_id, "Mã sản phẩm", 1)
            quantity = integer(quantity, "Số lượng", 1, 999)
            quantities[product_id] = integer(quantities.get(product_id, 0) + quantity,
                                            "Số lượng mỗi sản phẩm", 1, 999)
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            # Mọi thay đổi đơn/bàn được tuần tự hoá và commit trong cùng giao dịch.
            _lock(cursor, "CoffeeOrders")
            actor = self._authorize(cursor)
            old = None
            existing_lines = {}
            if order_id is not None:
                old = self._pending_order(cursor, order_id)
                if expected_version is None or bytes(old["PhienBan"]) != bytes(expected_version):
                    raise AppError("Đơn đã thay đổi ở cửa sổ khác. Hãy đóng và mở lại đơn.")
                cursor.execute("SELECT * FROM dbo.ChiTietDonHang WHERE MaDH = ?", order_id)
                existing_lines = {r["MaSP"]: r for r in rows(cursor)}
            if not cursor.execute("SELECT 1 FROM dbo.Ban WHERE MaBan = ?", table_id).fetchone():
                raise AppError("Vui lòng chọn bàn hợp lệ.")
            busy = cursor.execute("""SELECT MaDH FROM dbo.DonHang WHERE MaBan = ?
                AND TrangThai = ? AND MaDH <> ?""", table_id, PENDING, order_id or 0).fetchone()
            if busy:
                raise AppError("Bàn này đang có đơn xử lý. Vui lòng chọn bàn khác hoặc mở đơn hiện có.")
            if customer_id is not None and not cursor.execute(
                    "SELECT 1 FROM dbo.KhachHang WHERE MaKH = ?", customer_id).fetchone():
                raise AppError("Khách hàng không còn tồn tại.")
            lines = []
            total = Decimal("0.00")
            for product_id, quantity in quantities.items():
                product = cursor.execute("SELECT TenSP, Gia, TrangThai FROM dbo.SanPham WHERE MaSP = ?",
                                         product_id).fetchone()
                if not product:
                    raise AppError("Sản phẩm không còn tồn tại. Hãy làm mới menu.")
                existing = existing_lines.get(product_id)
                if not product.TrangThai and (not existing or quantity > existing["SoLuong"]):
                    raise AppError(f"Sản phẩm {product.TenSP} đã ngừng bán; không thể thêm số lượng.")
                # Giữ nguyên đơn giá đã lưu cho món có sẵn trong đơn.
                unit_price = existing["DonGia"] if existing else product.Gia
                name = existing["TenSPLucBan"] if existing else product.TenSP
                lines.append((product_id, name, quantity, unit_price))
                total += unit_price * quantity
            if old:
                cursor.execute("UPDATE dbo.DonHang SET MaBan = ?, MaKH = ?, TongTien = ? WHERE MaDH = ?",
                               table_id, customer_id, total, order_id)
                cursor.execute("DELETE FROM dbo.ChiTietDonHang WHERE MaDH = ?", order_id)
            else:
                order_id = cursor.execute("""INSERT dbo.DonHang (MaBan, MaKH, MaNV, TongTien)
                    OUTPUT INSERTED.MaDH VALUES (?, ?, ?, ?)""",
                    table_id, customer_id, actor["MaNV"], total).fetchval()
            cursor.executemany("""INSERT dbo.ChiTietDonHang
                (MaDH, MaSP, TenSPLucBan, SoLuong, DonGia) VALUES (?, ?, ?, ?, ?)""",
                [(order_id, *line) for line in lines])
            self._sync_table(cursor, table_id)
            if old and old["MaBan"] != table_id:
                self._sync_table(cursor, old["MaBan"])
            result = (order_id)
            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _pending_order(self, cursor, order_id):
        cursor.execute("SELECT * FROM dbo.DonHang WITH (UPDLOCK) WHERE MaDH = ?", order_id)
        result = rows(cursor)
        if not result:
            raise AppError("Đơn hàng không còn tồn tại.")
        if result[0]["TrangThai"] != PENDING:
            raise AppError("Chỉ có thể sửa, thanh toán hoặc huỷ đơn đang xử lý.")
        return result[0]

    def _sync_table(self, cursor, table_id):
        cursor.execute("""UPDATE dbo.Ban SET TrangThai = CASE WHEN EXISTS
            (SELECT 1 FROM dbo.DonHang WHERE MaBan = ? AND TrangThai = ?)
            THEN N'Đang phục vụ' ELSE N'Trống' END WHERE MaBan = ?""", table_id, PENDING, table_id)

    def finish_order(self, order_id, pay=True, expected_version=None):
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            _lock(cursor, "CoffeeOrders")
            self._authorize(cursor)
            order = self._pending_order(cursor, order_id)
            if expected_version is not None and bytes(order["PhienBan"]) != bytes(expected_version):
                raise AppError("Đơn vừa được thay đổi. Vui lòng làm mới và kiểm tra lại số tiền.")
            points = int(order["TongTien"] // 10000) if pay and order["MaKH"] else 0
            cursor.execute("""UPDATE dbo.DonHang SET TrangThai = ?, DiemDaCong = ?,
                ThoiGianThanhToan = CASE WHEN ? = 1 THEN SYSDATETIME() ELSE NULL END WHERE MaDH = ?""",
                PAID if pay else CANCELLED, points, int(pay), order_id)
            if points:
                cursor.execute("UPDATE dbo.KhachHang SET DiemTichLuy = DiemTichLuy + ? WHERE MaKH = ?",
                               points, order["MaKH"])
            self._sync_table(cursor, order["MaBan"])
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def delete_order(self, order_id, expected_version=None):
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            _lock(cursor, "CoffeeOrders")
            self._authorize(cursor, manager=True)
            cursor.execute("SELECT * FROM dbo.DonHang WITH (UPDLOCK) WHERE MaDH = ?", order_id)
            orders = rows(cursor)
            if not orders:
                raise AppError("Đơn hàng không còn tồn tại.")
            order = orders[0]
            if expected_version is not None and bytes(order["PhienBan"]) != bytes(expected_version):
                raise AppError("Đơn vừa được thay đổi. Vui lòng làm mới danh sách.")
            if order["TrangThai"] == PAID:
                raise AppError("Không xoá hoá đơn đã thanh toán để giữ lịch sử doanh thu.")
            cursor.execute("DELETE FROM dbo.DonHang WHERE MaDH = ?", order_id)
            self._sync_table(cursor, order["MaBan"])
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def statistics(self, first, until):
        if not isinstance(first, date) or not isinstance(until, date) or first >= until:
            raise AppError("Khoảng thời gian không hợp lệ.")
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            self._authorize(cursor, manager=True)
            # Cùng một ảnh dữ liệu khi thanh toán diễn ra song song với báo cáo.
            _lock(cursor, "CoffeeOrders")
            summary = cursor.execute("""SELECT COALESCE(SUM(TongTien), 0), COUNT(*) FROM dbo.DonHang
                WHERE TrangThai = ? AND ThoiGianThanhToan >= ? AND ThoiGianThanhToan < ?""",
                PAID, first, until).fetchone()
            cursor.execute("""SELECT TOP 10 ct.MaSP, sp.TenSP, SUM(CAST(ct.SoLuong AS BIGINT)) AS SoLuong,
                SUM(ct.ThanhTien) AS DoanhThu FROM dbo.ChiTietDonHang ct
                JOIN dbo.DonHang d ON d.MaDH = ct.MaDH JOIN dbo.SanPham sp ON sp.MaSP = ct.MaSP
                WHERE d.TrangThai = ? AND d.ThoiGianThanhToan >= ? AND d.ThoiGianThanhToan < ?
                GROUP BY ct.MaSP, sp.TenSP ORDER BY SoLuong DESC, DoanhThu DESC, ct.MaSP""",
                PAID, first, until)
            result = (summary[0], summary[1], rows(cursor))
            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def revenue_series(self, first, until):
        """Dữ liệu biểu đồ: từng ngày cho kỳ ngắn, từng tháng cho kỳ dài."""
        if not isinstance(first, date) or not isinstance(until, date) or first >= until:
            raise AppError("Khoảng thời gian không hợp lệ.")
        daily = (until - first).days <= 31
        group = ("CAST(ThoiGianThanhToan AS DATE)" if daily else
                 "DATEFROMPARTS(YEAR(ThoiGianThanhToan), MONTH(ThoiGianThanhToan), 1)")
        connection = connect()
        try:
            connection.execute("SET XACT_ABORT ON")
            cursor = connection.cursor()
            self._authorize(cursor, manager=True)
            cursor.execute(f"""SELECT {group} AS Ngay, SUM(TongTien) AS DoanhThu
                FROM dbo.DonHang WHERE TrangThai = ?
                AND ThoiGianThanhToan >= ? AND ThoiGianThanhToan < ?
                GROUP BY {group} ORDER BY Ngay""", PAID, first, until)
            amounts = {row["Ngay"]: row["DoanhThu"] for row in rows(cursor)}
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        result = []
        current = first if daily else first.replace(day=1)
        while current < until:
            result.append((current, amounts.get(current, Decimal(0))))
            current = current + timedelta(days=1) if daily else (current.replace(day=28) + timedelta(days=4)).replace(day=1)
        return result if daily else result[-12:]
