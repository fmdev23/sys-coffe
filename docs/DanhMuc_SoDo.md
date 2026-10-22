# Danh mục sơ đồ để vẽ và đối chiếu mã nguồn

DFD mức 0 dùng đúng ảnh đã vẽ do sinh viên cung cấp, lưu tại `docs/DFD_Muc0.png`. Không vẽ lại, không đổi khối, số tiến trình, nhãn hoặc hướng mũi tên của ảnh này.

Các hình khác trong báo cáo hiện là hình tham khảo đã sinh từ mã PlantUML. Khi tự vẽ xong, thay đúng hình tương ứng và giữ tên chú thích để không làm lệch danh mục hình.

## Danh sách tổng hợp

| Hình trong báo cáo | Sơ đồ | Trạng thái và việc cần làm |
|---|---|---|
| G.1 | DFD mức 0 | Đã có bản vẽ của sinh viên, giữ nguyên |
| G.2 | Luồng lưu trữ và xuất CSV | Vẽ để giải thích SQL Server và tệp CSV |
| 2.1 | Phân rã chức năng và hàm chính | Vẽ dạng cây bốn nhóm nhiệm vụ |
| 2.2 | Kiến trúc và tổ chức mã nguồn | Vẽ ba phần trách nhiệm của ứng dụng, SQL Server và CSV |
| 2.3 | Quan hệ dữ liệu ERD | Vẽ đủ bảy bảng và sáu quan hệ |
| 2.4 | Lưu đồ lưu đơn | Vẽ điều kiện, vòng lặp kiểm tra món và giao dịch |
| 2.5 | Lưu đồ thanh toán | Vẽ kiểm tra tiền nhận, tính điểm và ghi thanh toán |

Ngoài DFD đã hoàn thành, có sáu sơ đồ để tự vẽ theo danh sách này. Bảy ảnh giao diện trong báo cáo là ảnh chụp khi chạy ứng dụng, có thể giữ lại.

## Hình G.2 Luồng lưu trữ và xuất CSV

Đối chiếu `db_connection.py`, `models/service.py` và `ui/statistics_tab.py`.

Vẽ năm khối: người sử dụng, ứng dụng Python, SQL Server, quản lý chọn kỳ báo cáo và tệp CSV. Người sử dụng gồm nhân viên và quản lý. Khối quản lý riêng ở luồng báo cáo nhằm thể hiện quyền xuất tệp.

| Từ | Đến | Nhãn đường nối |
|---|---|---|
| Người sử dụng | Ứng dụng Python | Dữ liệu nhập và thao tác |
| Ứng dụng Python | Người sử dụng | Kết quả xử lý |
| Ứng dụng Python | SQL Server | Truy vấn có tham số và cập nhật trong giao dịch |
| SQL Server | Ứng dụng Python | Bản ghi và kết quả truy vấn |
| Quản lý | Ứng dụng Python | Kỳ thống kê và vị trí lưu |
| Ứng dụng Python | Tệp CSV | Ghi báo cáo bằng csv.writer, UTF-8 có BOM |
| Tệp CSV | Quản lý | Báo cáo để đối chiếu |

SQL Server là nơi lưu dữ liệu chính. CSV chỉ là tệp xuất báo cáo, chương trình chưa nhập CSV vào danh mục. Đặt tên hình là luồng lưu trữ và xuất dữ liệu, không thay tên hoặc hình DFD mức 0 đã có.

## Hình 2.1 Phân rã chức năng và hàm chính

Đối chiếu `main.py`, `models/service.py`, `ui/dashboard.py` và `ui/statistics_tab.py`.

Khối gốc là ứng dụng quản lý quán cà phê CoffeeApp. Từ khối gốc chia thành bốn nhánh. Đường nối biểu diễn quan hệ phân rã, không dùng mũi tên để diễn giải thứ tự chạy.

| Nhánh | Chức năng con | Hàm chính để tra cứu |
|---|---|---|
| Phiên làm việc | Đăng nhập | CoffeeService.login |
| Phiên làm việc | Đổi mật khẩu | CoffeeService.change_password |
| Phiên làm việc | Đăng xuất về màn hình đăng nhập | CoffeeApp.show_login |
| Danh mục | Tra cứu dữ liệu | CoffeeService.list_entities |
| Danh mục | Thêm hoặc sửa dữ liệu | CoffeeService.save_entity |
| Danh mục | Xoá dữ liệu | CoffeeService.delete_entity |
| Đơn hàng | Tạo, sửa và chuyển bàn | CoffeeService.save_order |
| Đơn hàng | Thanh toán hoặc huỷ | CoffeeService.finish_order |
| Đơn hàng | Xoá đơn hợp lệ | CoffeeService.delete_order |
| Báo cáo | Tổng quan | Dashboard.refresh |
| Báo cáo | Thống kê | CoffeeService.statistics |
| Báo cáo | Xuất CSV | StatisticsTab.export |

Danh mục tài khoản dùng các hàm riêng `list_accounts`, `save_account` và `delete_account`. Có thể thêm một ô “Quản lý tài khoản” trong nhánh danh mục nếu muốn thể hiện rõ phần này. Không ghi tên hàm không tồn tại như `CoffeeService.dashboard` hoặc `CoffeeApp.logout`.

## Hình 2.2 Kiến trúc và tổ chức mã nguồn

Đối chiếu `main.py`, thư mục `ui/`, `models/service.py`, `security.py` và `db_connection.py`.

Vẽ một khung lớn “Ứng dụng Python”. Bên trong có ba khối:

1. Giao diện: `main.py` và `ui/`.
2. Xử lý nghiệp vụ: `models/service.py`, hỗ trợ xác thực từ `security.py`.
3. Kết nối và giao dịch: `db_connection.py`.

Bên ngoài khung có SQL Server và tệp CSV. Nối các khối theo các quan hệ:

| Hai khối | Nội dung trao đổi |
|---|---|
| Giao diện và nghiệp vụ | Gọi phương thức, trả kết quả hoặc báo lỗi |
| Nghiệp vụ và kết nối | Câu SQL có tham số, bản ghi truy vấn |
| Kết nối và SQL Server | Đọc, ghi dữ liệu, commit hoặc rollback |
| Giao diện đến CSV | StatisticsTab.export ghi tệp từ số liệu thống kê |

Ba phần Python chạy trong cùng một chương trình trên máy tính. Không vẽ thành ba máy chủ hoặc ba dịch vụ mạng. Chức năng ghi CSV nằm ở giao diện báo cáo, còn dữ liệu thống kê được lấy từ dịch vụ nghiệp vụ.

## Hình 2.3 Quan hệ dữ liệu ERD

Đối chiếu toàn bộ phần `SCHEMA` trong `database_setup.py`.

Vẽ bảy bảng, mỗi bảng có tên, khoá chính và những khoá ngoại sau:

| Bảng | Khoá chính | Khoá ngoại và ràng buộc đáng chú ý |
|---|---|---|
| NhanVien | MaNV | Không có khoá ngoại |
| TaiKhoan | MaTK | MaNV bắt buộc và duy nhất, TenDangNhap duy nhất |
| KhachHang | MaKH | Không có khoá ngoại |
| Ban | MaBan | TenBan duy nhất |
| SanPham | MaSP | Không có khoá ngoại |
| DonHang | MaDH | MaBan và MaNV bắt buộc, MaKH có thể NULL |
| ChiTietDonHang | MaCTDH | MaDH và MaSP bắt buộc, cặp MaDH–MaSP duy nhất |

Vẽ đúng sáu quan hệ. Khi dùng ký hiệu chân quạ, phía “một” dùng hai vạch, phía “không hoặc một” dùng vòng tròn và một vạch, phía “không hoặc nhiều” dùng vòng tròn và chân quạ.

| Quan hệ | Số lượng và ý nghĩa |
|---|---|
| NhanVien – TaiKhoan | Một nhân viên có 0 hoặc 1 tài khoản. Mỗi tài khoản thuộc đúng 1 nhân viên |
| NhanVien – DonHang | Một nhân viên có 0 đến nhiều đơn. Mỗi đơn thuộc đúng 1 nhân viên |
| Ban – DonHang | Một bàn có 0 đến nhiều đơn trong lịch sử. Mỗi đơn thuộc đúng 1 bàn |
| KhachHang – DonHang | Một khách có 0 đến nhiều đơn. Mỗi đơn có 0 hoặc 1 khách |
| DonHang – ChiTietDonHang | Mỗi chi tiết thuộc đúng 1 đơn. Riêng ràng buộc SQL cho phép một đơn có 0 đến nhiều chi tiết |
| SanPham – ChiTietDonHang | Một món có 0 đến nhiều chi tiết bán hàng. Mỗi chi tiết thuộc đúng 1 món |

Ở mức nghiệp vụ, `save_order` chỉ lưu đơn có ít nhất một món. Nếu vẽ ERD theo nghiệp vụ và dùng 1 đến nhiều chi tiết, cần ghi rõ quy tắc này do hàm lưu đơn kiểm tra. Nếu vẽ mô hình ràng buộc SQL, giữ 0 đến nhiều ở phía chi tiết như hình hiện có.

Các trường nên đưa vào hình:

- NhanVien: HoTen, SDT, ChucVu.
- TaiKhoan: TenDangNhap, MatKhauHash, VaiTro, HoatDong.
- KhachHang: HoTen, SDT, DiemTichLuy.
- Ban: TenBan, KhuVuc, TrangThai.
- SanPham: TenSP, DanhMuc, Gia, MoTa, TrangThai.
- DonHang: ThoiGianTao, ThoiGianThanhToan, TongTien, DiemDaCong, TrangThai, PhienBan.
- ChiTietDonHang: TenSPLucBan, SoLuong, DonGia, ThanhTien.

Ghi chú cạnh hình: `PhienBan` là ROWVERSION, không phải ngày giờ. `ThanhTien` là cột tính từ số lượng nhân đơn giá. MaDH trong chi tiết có ON DELETE CASCADE. Chỉ mục duy nhất có điều kiện bảo đảm mỗi bàn có tối đa một đơn đang xử lý, không giới hạn số đơn trong lịch sử của bàn.

## Hình 2.4 Lưu đồ lưu đơn

Đối chiếu `CoffeeService.save_order` và `db_connection.transaction`.

Dùng hình bắt đầu/kết thúc, hình chữ nhật cho xử lý, hình thoi cho điều kiện. Các nhánh điều kiện phải có nhãn Có hoặc Không.

Thứ tự cần vẽ:

1. Bắt đầu lưu đơn.
2. Kiểm tra giỏ không rỗng, mã sản phẩm và số lượng hợp lệ. Gộp các dòng trùng mã bằng dict quantities và kiểm tra tổng số lượng mỗi món không vượt 999.
3. Dữ liệu đầu vào hợp lệ? Nếu không, báo lỗi và kết thúc, chưa mở giao dịch.
4. Mở giao dịch và lấy khoá CoffeeOrders.
5. Kiểm tra quyền, bàn tồn tại, bàn chưa bị đơn khác chiếm và khách tồn tại nếu được chọn. Nếu sửa đơn, kiểm tra đơn đang xử lý và đúng PhienBan.
6. Các điều kiện hợp lệ? Nếu không, rollback, báo lỗi và kết thúc.
7. Chuẩn bị list lines và tổng tiền bằng 0.
8. Còn sản phẩm trong quantities? Nếu có, lấy sản phẩm hiện tại.
9. Sản phẩm tồn tại và được phép bán? Với món ngừng bán đã có trong đơn, chỉ được giữ hoặc giảm số lượng cũ. Nếu không hợp lệ, rollback và báo lỗi.
10. Nếu món đã có trong đơn, lấy tên và đơn giá lịch sử. Nếu là món mới, lấy tên và giá hiện tại. Thêm dòng chi tiết và cộng số lượng nhân đơn giá vào tổng.
11. Quay lại điều kiện “Còn sản phẩm trong quantities?”.
12. Khi hết sản phẩm, thêm đơn mới hoặc cập nhật đơn cũ. Với đơn cũ, xoá các chi tiết cũ trước khi ghi lại.
13. Ghi các dòng chi tiết. Đồng bộ trạng thái bàn mới. Nếu chuyển bàn, đồng bộ cả bàn cũ.
14. Ghi SQL và commit thành công? Nếu không, rollback và báo lỗi.
15. Trả mã đơn, giao diện làm mới, kết thúc.

Ghi một chú thích bên cạnh khối giao dịch: mọi ngoại lệ trong khối này đều dẫn tới rollback, kể cả lỗi truy vấn hoặc lấy khoá. Nhánh kiểm tra lỗi ở cuối không có nghĩa chỉ lỗi ghi mới được hoàn tác.

## Hình 2.5 Lưu đồ thanh toán

Đối chiếu `ui/payment_dialog.py`, `CoffeeService.finish_order` và `db_connection.transaction`.

Thứ tự cần vẽ:

1. Bắt đầu, mở hộp thoại thu tiền của đơn đang xử lý.
2. Nhập tiền khách đưa. Giao diện loại dấu chấm và khoảng trắng, kiểm tra chuỗi số hợp lệ, tối đa 15 chữ số.
3. Tính tiền thừa bằng tiền nhận trừ tổng đơn.
4. Tiền nhận hợp lệ và đủ? Nếu không, hiển thị lỗi hoặc số còn thiếu, khoá nút hoàn tất và quay lại nhập tiền.
5. Nhân viên xác nhận đã nhận đủ tiền. Nếu đóng hộp thoại trước bước này, kết thúc và chưa ghi thanh toán.
6. Mở giao dịch, lấy khoá CoffeeOrders.
7. Kiểm tra quyền, đơn đang xử lý và đúng phiên bản được giao diện truyền vào.
8. Điều kiện hợp lệ? Nếu không, rollback, báo lỗi và kết thúc.
9. Tính điểm bằng phần nguyên của tổng tiền chia 10.000 nếu đơn có khách. Không có khách thì điểm bằng 0.
10. Ghi trạng thái đã thanh toán, thời gian thanh toán và DiemDaCong vào đơn.
11. Điểm lớn hơn 0? Nếu có, cộng điểm vào KhachHang. Nếu không, bỏ qua cập nhật điểm khách.
12. Đồng bộ trạng thái bàn.
13. Ghi SQL và commit thành công? Nếu không, rollback và báo lỗi.
14. Làm mới giao diện, thông báo thành công và kết thúc.

Tiền khách đưa và tiền thừa chỉ tồn tại trên giao diện, không có cột lưu trong SQL. Giao diện luôn truyền expected_version khi thu tiền. Hàm finish_order khi được gọi riêng cho phép tham số phiên bản là None. Sơ đồ này mô tả thanh toán, không vẽ nhánh huỷ như một lần cộng điểm.

## Nơi tự vẽ và mã tham khảo

- [diagrams.net](https://app.diagrams.net/) để kéo thả khối và đường nối.
- [PlantUML Editor](https://editor.plantuml.com/) để dán mã trong `SoDo_PlantUML.md` và xem hình tham khảo.

Khi hoàn tất bản vẽ, xuất SVG hoặc PNG đủ rõ chữ. Dùng đúng tên hình trong bảng tổng hợp để thay vào báo cáo. DFD mức 0 vẫn giữ nguyên ảnh đã cung cấp.
