"""Chạy nhiều lần an toàn: tạo bảng còn thiếu, không ghi đè dữ liệu."""
import sys

sys.dont_write_bytecode = True

from db_connection import connect, database_name
from security import hash_password

SCHEMA = [
    """IF OBJECT_ID(N'dbo.NhanVien', N'U') IS NULL
    CREATE TABLE dbo.NhanVien (
        MaNV INT IDENTITY PRIMARY KEY, HoTen NVARCHAR(100) NOT NULL,
        SDT VARCHAR(15) NOT NULL DEFAULT '', ChucVu NVARCHAR(60) NOT NULL
    )""",
    """IF OBJECT_ID(N'dbo.TaiKhoan', N'U') IS NULL
    CREATE TABLE dbo.TaiKhoan (
        MaTK INT IDENTITY PRIMARY KEY, TenDangNhap NVARCHAR(50) NOT NULL UNIQUE,
        MatKhauHash VARCHAR(255) NOT NULL,
        VaiTro NVARCHAR(20) NOT NULL CHECK (VaiTro IN (N'Quản lý', N'Nhân viên')),
        MaNV INT NOT NULL UNIQUE REFERENCES dbo.NhanVien(MaNV),
        HoatDong BIT NOT NULL DEFAULT 1
    )""",
    """IF OBJECT_ID(N'dbo.KhachHang', N'U') IS NULL
    CREATE TABLE dbo.KhachHang (
        MaKH INT IDENTITY PRIMARY KEY, HoTen NVARCHAR(100) NOT NULL,
        SDT VARCHAR(15) NOT NULL DEFAULT '',
        DiemTichLuy INT NOT NULL DEFAULT 0 CHECK (DiemTichLuy >= 0)
    )""",
    """IF OBJECT_ID(N'dbo.Ban', N'U') IS NULL
    CREATE TABLE dbo.Ban (
        MaBan INT IDENTITY PRIMARY KEY, TenBan NVARCHAR(50) NOT NULL UNIQUE,
        KhuVuc NVARCHAR(100) NOT NULL,
        TrangThai NVARCHAR(20) NOT NULL DEFAULT N'Trống'
            CHECK (TrangThai IN (N'Trống', N'Đang phục vụ'))
    )""",
    """IF OBJECT_ID(N'dbo.SanPham', N'U') IS NULL
    CREATE TABLE dbo.SanPham (
        MaSP INT IDENTITY PRIMARY KEY, TenSP NVARCHAR(100) NOT NULL,
        DanhMuc NVARCHAR(60) NOT NULL,
        Gia DECIMAL(18,2) NOT NULL CHECK (Gia > 0),
        MoTa NVARCHAR(500) NOT NULL DEFAULT '', TrangThai BIT NOT NULL DEFAULT 1
    )""",
    """IF OBJECT_ID(N'dbo.DonHang', N'U') IS NULL
    CREATE TABLE dbo.DonHang (
        MaDH INT IDENTITY PRIMARY KEY,
        MaBan INT NOT NULL REFERENCES dbo.Ban(MaBan),
        MaKH INT NULL REFERENCES dbo.KhachHang(MaKH),
        MaNV INT NOT NULL REFERENCES dbo.NhanVien(MaNV),
        ThoiGianTao DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        ThoiGianThanhToan DATETIME2 NULL,
        TongTien DECIMAL(18,2) NOT NULL DEFAULT 0 CHECK (TongTien >= 0),
        DiemDaCong INT NOT NULL DEFAULT 0 CHECK (DiemDaCong >= 0), PhienBan ROWVERSION,
        TrangThai NVARCHAR(20) NOT NULL DEFAULT N'Đang xử lý'
            CHECK (TrangThai IN (N'Đang xử lý', N'Đã thanh toán', N'Đã huỷ'))
    )""",
    """IF OBJECT_ID(N'dbo.ChiTietDonHang', N'U') IS NULL
    CREATE TABLE dbo.ChiTietDonHang (
        MaCTDH INT IDENTITY PRIMARY KEY,
        MaDH INT NOT NULL REFERENCES dbo.DonHang(MaDH) ON DELETE CASCADE,
        MaSP INT NOT NULL REFERENCES dbo.SanPham(MaSP),
        TenSPLucBan NVARCHAR(100) NOT NULL,
        SoLuong INT NOT NULL CHECK (SoLuong > 0),
        DonGia DECIMAL(18,2) NOT NULL CHECK (DonGia > 0),
        ThanhTien AS CONVERT(DECIMAL(18,2), SoLuong * DonGia) PERSISTED,
        CONSTRAINT UQ_ChiTietDonHang_SanPham UNIQUE (MaDH, MaSP)
    )""",
    """IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UX_Ban_DonDangXuLy'
                       AND object_id = OBJECT_ID('dbo.DonHang'))
    CREATE UNIQUE INDEX UX_Ban_DonDangXuLy ON dbo.DonHang(MaBan)
        WHERE TrangThai = N'Đang xử lý'""",
    """IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DoanhThu'
                       AND object_id = OBJECT_ID('dbo.DonHang'))
    CREATE INDEX IX_DoanhThu ON dbo.DonHang(TrangThai, ThoiGianThanhToan)
        INCLUDE (TongTien)""",
]


def setup(seed=True):
    name = database_name()
    master = connect("master", autocommit=True)
    try:
        if not master.execute("SELECT 1 FROM sys.databases WHERE name = ?", name).fetchone():
            master.execute(f"CREATE DATABASE [{name}]")
    finally:
        master.close()
    created_admin = False
    connection = connect()
    try:
        connection.execute("SET XACT_ABORT ON")
        cursor = connection.cursor()
        # Tránh hai tiến trình thiết lập cùng chèn dữ liệu mẫu.
        cursor.execute("""DECLARE @result INT;
            EXEC @result = sys.sp_getapplock @Resource = 'CoffeeSetup',
                @LockMode = 'Exclusive', @LockOwner = 'Transaction', @LockTimeout = 15000;
            IF @result < 0 THROW 50001, 'Khong the khoa thiet lap du lieu', 1;""")
        for statement in SCHEMA:
            cursor.execute(statement)
        if seed:
            if not cursor.execute("SELECT TOP 1 MaTK FROM dbo.TaiKhoan").fetchone():
                employee = cursor.execute(
                    "INSERT dbo.NhanVien (HoTen, SDT, ChucVu) OUTPUT INSERTED.MaNV VALUES (?, ?, ?)",
                    "Quản trị viên", "", "Quản lý").fetchval()
                cursor.execute("""INSERT dbo.TaiKhoan
                    (TenDangNhap, MatKhauHash, VaiTro, MaNV) VALUES (?, ?, ?, ?)""",
                    "admin", hash_password("Admin@123"), "Quản lý", employee)
                created_admin = True
            if not cursor.execute("SELECT TOP 1 MaSP FROM dbo.SanPham").fetchone():
                cursor.executemany("""INSERT dbo.SanPham
                    (TenSP, DanhMuc, Gia, MoTa) VALUES (?, ?, ?, ?)""", [
                    ("Cà phê đen", "Cà phê", 25000, "Cà phê phin truyền thống"),
                    ("Cà phê sữa", "Cà phê", 30000, "Cà phê phin và sữa đặc"),
                    ("Bạc xỉu", "Cà phê", 35000, "Sữa béo, cà phê nhẹ"),
                    ("Trà đào", "Trà", 40000, "Trà đào cam sả"),
                    ("Ca cao", "Đồ uống khác", 35000, "Ca cao nóng hoặc đá"),
                ])
            if not cursor.execute("SELECT TOP 1 MaBan FROM dbo.Ban").fetchone():
                cursor.executemany("INSERT dbo.Ban (TenBan, KhuVuc) VALUES (?, ?)",
                                   [(f"Bàn {i:02}", "Tầng trệt" if i <= 4 else "Sân vườn")
                                    for i in range(1, 9)])
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return created_admin


if __name__ == "__main__":
    # Windows có thể dùng code page không hỗ trợ tiếng Việt khi chuyển hướng output.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        created = setup()
        print(f"Đã chuẩn bị xong cơ sở dữ liệu {database_name()}.")
        if created:
            print("Tài khoản: admin | Mật khẩu: Admin@123 (hãy đổi sau khi đăng nhập).")
        else:
            print("Giữ nguyên tài khoản và dữ liệu hiện có.")
    except Exception as error:
        print(f"Không thể thiết lập cơ sở dữ liệu: {error}", file=sys.stderr)
        sys.exit(1)
