# Yêu cầu hệ thống quản lý quán cà phê

## Công nghệ và phạm vi

- Ứng dụng desktop Python, giao diện Tkinter/ttk bằng tiếng Việt.
- Lưu dữ liệu trên Microsoft SQL Server `THINKPADX1\SQLSEVER`, database `QuanLyQuanCoffee`.
- Windows Authentication; ưu tiên ODBC Driver 17 for SQL Server, dự phòng driver SQL Server.
- Script khởi tạo database, bảng, dữ liệu mẫu; chạy lại không xoá dữ liệu hoặc đặt lại tài khoản.

## Chức năng

| Nhóm | Nội dung |
|---|---|
| Sản phẩm | Thêm, xem, sửa, xoá; tên, danh mục, giá, mô tả, còn bán/ngừng bán |
| Bàn | Thêm, xem, sửa, xoá; tên, khu vực, trống/đang phục vụ |
| Nhân viên | Thêm, xem, sửa, xoá hồ sơ; liên kết tài khoản đăng nhập |
| Khách hàng | Thêm, xem, sửa, xoá; tên, điện thoại, điểm tích luỹ |
| Đơn hàng | Chọn bàn, khách tuỳ chọn, nhiều món và số lượng; tính tổng, sửa/chuyển bàn, huỷ, thanh toán |
| Tài khoản | Đăng nhập; hash mật khẩu; vai trò Quản lý/Nhân viên; quản lý tài khoản nhân viên |
| Thống kê | Doanh thu, số đơn, món bán chạy theo ngày/khoảng ngày/tháng; chỉ Quản lý truy cập |

Quản lý có quyền quản trị các danh mục, tài khoản và báo cáo. Nhân viên chỉ xem thực đơn/bàn và xử lý đơn hàng. Quyền được kiểm tra cả ở giao diện và nghiệp vụ.

## Dữ liệu

Bảy bảng: `NhanVien`, `TaiKhoan`, `KhachHang`, `Ban`, `SanPham`, `DonHang`, `ChiTietDonHang`.

- Tài khoản liên kết một nhân viên.
- Đơn liên kết bàn, nhân viên lập đơn và khách hàng nếu có.
- Chi tiết đơn liên kết đơn hàng và sản phẩm; lưu đơn giá tại thời điểm bán.
- Một bàn có tối đa một đơn đang xử lý.
- Thanh toán/huỷ đơn cập nhật bàn về trống trong cùng giao dịch.
- Không sửa/xoá hoá đơn đã thanh toán; danh mục đang được tham chiếu được giữ lại.

## Giao diện và chất lượng

- Điều hướng riêng theo vai trò, sơ đồ bàn trực quan, chọn món cạnh giỏ hàng.
- Thống nhất màu sắc, chữ, nút; thể hiện trạng thái bằng cả chữ và màu.
- Logo riêng, nút/ô nhập/thẻ bo góc; giữ sự kiện và bàn phím của control ttk gốc.
- Nút lưu và thu tiền rõ ràng, giỏ hàng vẫn thấy các món khi thu nhỏ cửa sổ; trang dài có thể cuộn.
- Kiểm tra trường bắt buộc, giá, số lượng, điện thoại; lỗi nhập liệu được báo rõ.
- Truy vấn dùng tham số; lỗi SQL/kết nối có thông báo và hoàn tác giao dịch.
- Mã chia theo màn hình và nghiệp vụ; không thêm framework hay thư viện ngoài phạm vi.
- Tệp tạm, ảnh kiểm tra và database thử nghiệm được dọn sau kiểm tra.
