# Mã sơ đồ đối chiếu dự án Coffee

Mở [PlantUML Editor](https://editor.plantuml.com/), xoá mã mẫu và dán nguyên một khối bên dưới, từ dòng bắt đầu đến dòng kết thúc. Chọn SVG hoặc PNG để xem và tải hình. Không dán đồng thời nhiều sơ đồ vào một ô.

Các sơ đồ mô tả phiên bản mã nguồn trong dự án. Kiểm tra cú pháp sinh hình không thay thế việc đối chiếu nghiệp vụ. Các điểm cần phân biệt được ghi bên dưới từng sơ đồ.

## Quy tắc áp dụng cho báo cáo

Giữ bìa, phần giới thiệu và bốn chương của mẫu học phần Python. Không thêm trang hội đồng xét duyệt, nhận xét thực tập, lời cảm tạ hoặc cam kết. Mẫu Python yêu cầu lề trên và dưới 2 cm, nên giữ 2 cm thay vì 2,5 cm của quy định DNC. Lề trái 3,5 cm, phải 2 cm. Văn bản Times New Roman 13, giãn dòng 1,2, thụt đầu dòng 1 cm, cách trước 6 pt và sau 0 pt. Bảng, tài liệu tham khảo và phụ lục dùng giãn dòng đơn theo hướng dẫn riêng của DNC. Chương mới bắt đầu ở trang mới, tiêu đề 14 đậm và căn giữa. Các hình và bảng đánh số theo chương. Ký hiệu G dùng cho phần Giới thiệu, A dùng cho Phụ lục. Mục lục và danh mục hình/bảng là trường tự động của Word. Trích dẫn dùng tác giả và năm, nguồn không nêu năm được ghi “không ghi năm”.

Tài liệu đối chiếu: BaoCao_LapTrinhPython_Maubaocao.pdf và Quyết định 309/QĐ-ĐHNCT ngày 08/12/2016 do người dùng cung cấp. Quyết định này là tài liệu quy định được cung cấp, không khẳng định là phiên bản mới nhất đang áp dụng.

## DFD mức 0 đã hoàn thành

Giữ nguyên bản vẽ do sinh viên cung cấp trong DFD_Muc0.png. Không sinh lại sơ đồ này bằng mã. Danh sách các sơ đồ cần tự vẽ nằm trong DanhMuc_SoDo.md.

## Luồng lưu trữ và xuất tệp

Đối chiếu: `db_connection.py, ui/statistics_tab.py`.

Đây là sơ đồ luồng lưu trữ, không gọi là DFD cấp 0. SQL Server lưu dữ liệu chính. CSV chỉ xuất từ ứng dụng, không có luồng nhập CSV.

```plantuml
@startuml
skinparam backgroundColor white
skinparam dpi 200
skinparam shadowing false
skinparam defaultFontName "Times New Roman"
skinparam defaultFontSize 18
skinparam ArrowColor black
skinparam defaultTextAlignment center
skinparam rectangleBackgroundColor white
skinparam rectangleBorderColor black
skinparam roundCorner 18

top to bottom direction
rectangle "Nhân viên / Quản lý" as USER
rectangle "Ứng dụng Python\nGiao diện và xử lý nghiệp vụ" as APP
database "SQL Server\nLưu danh mục, tài khoản, đơn hàng" as SQL
rectangle "Quản lý\nChọn kỳ báo cáo và vị trí lưu" as MANAGER
file "Tệp CSV\nTổng doanh thu, số đơn\nCác món bán chạy" as CSV
USER --> APP : Dữ liệu nhập và thao tác
APP --> USER : Kết quả xử lý
APP --> SQL : Truy vấn có tham số\nCập nhật trong giao dịch
SQL --> APP : Bản ghi và kết quả truy vấn
MANAGER --> APP : Kỳ thống kê và đường dẫn
APP --> CSV : csv.writer\nUTF-8 có BOM
CSV --> MANAGER : Báo cáo để đối chiếu
@enduml
```

## Phân rã chức năng và hàm chính

Đối chiếu: `main.py, models/service.py, ui/dashboard.py, ui/statistics_tab.py`.

Đường nối WBS biểu diễn quan hệ phân rã, không biểu diễn thứ tự chạy. login, change_password, list_entities, save_entity, delete_entity, save_order, finish_order, delete_order và statistics là phương thức CoffeeService. show_login thuộc CoffeeApp, refresh thuộc Dashboard, export thuộc StatisticsTab. Các hàm tài khoản save_account, delete_account, list_accounts nằm trong nhóm danh mục, không đồng nhất với các hàm entity. Sơ đồ chọn các hàm chính, không liệt kê mọi hàm phụ.

```plantuml
@startwbs
skinparam backgroundColor white
skinparam dpi 200
skinparam shadowing false
skinparam defaultFontName "Times New Roman"
skinparam defaultFontSize 18
skinparam nodeBackgroundColor white
* CoffeeApp\nỨng dụng quản lý quán cà phê
** Phiên làm việc
*** Đăng nhập\nlogin()
*** Đổi mật khẩu\nchange_password()
*** Đăng xuất\nshow_login()
** Danh mục
*** Tra cứu\nlist_entities()
*** Thêm / sửa\nsave_entity()
*** Xoá\ndelete_entity()
** Đơn hàng
*** Tạo / sửa / chuyển bàn\nsave_order()
*** Thanh toán / huỷ\nfinish_order()
*** Xoá đơn hợp lệ\ndelete_order()
** Báo cáo
*** Tổng quan\nrefresh()
*** Thống kê\nstatistics()
*** Xuất CSV\nexport()
@endwbs
```

## Tổ chức mã nguồn

Đối chiếu: `main.py, ui/, models/service.py, security.py, db_connection.py`.

Các phần Python chạy trong cùng chương trình. SQL Server là hệ quản trị dữ liệu. Chức năng ghi CSV thuộc giao diện StatisticsTab, lấy số liệu từ CoffeeService.

```plantuml
@startuml
skinparam backgroundColor white
skinparam dpi 200
skinparam shadowing false
skinparam defaultFontName "Times New Roman"
skinparam defaultFontSize 18
skinparam ArrowColor black
skinparam defaultTextAlignment center
skinparam rectangleBackgroundColor white
skinparam rectangleBorderColor black
skinparam roundCorner 18

left to right direction
rectangle "Ứng dụng Python" {
 rectangle "Giao diện\nmain.py, ui/" as GUI
 rectangle "Nghiệp vụ\nmodels/service.py\nsecurity.py" as BUSINESS
 rectangle "Kết nối và giao dịch\ndb_connection.py" as CONNECTION
 GUI <--> BUSINESS : Gọi hàm\nKết quả / lỗi
 BUSINESS <--> CONNECTION : SQL có tham số\nBản ghi
}
database "SQL Server" as DB
file "Báo cáo CSV" as CSV
CONNECTION <--> DB : Dữ liệu
GUI --> CSV : Ghi CSV
@enduml
```

## Quan hệ dữ liệu

Đối chiếu: `database_setup.py`.

Dấu || là đúng một, |o là không hoặc một, o{ là không hoặc nhiều. Mỗi TaiKhoan bắt buộc thuộc một NhanVien, mỗi NhanVien có tối đa một TaiKhoan. MaKH của DonHang có thể NULL. Quan hệ đơn–chi tiết thể hiện ràng buộc SQL có thể không có chi tiết, trong khi save_order luôn yêu cầu giỏ không rỗng. MaDH trong ChiTietDonHang có ON DELETE CASCADE. Đơn đang xử lý có chỉ mục duy nhất theo MaBan. Sơ đồ thể hiện trường quan trọng, không phải mọi chi tiết kiểu dữ liệu.

```plantuml
@startuml
skinparam backgroundColor white
skinparam dpi 200
skinparam shadowing false
skinparam defaultFontName "Times New Roman"
skinparam defaultFontSize 18
skinparam ArrowColor black
skinparam defaultTextAlignment center
skinparam rectangleBackgroundColor white
skinparam rectangleBorderColor black
skinparam roundCorner 18

hide circle
skinparam linetype ortho
skinparam classBackgroundColor white
skinparam classAttributeIconSize 0
entity NhanVien {
 * MaNV : PK
 --
 HoTen
 SDT
 ChucVu
}
entity TaiKhoan {
 * MaTK : PK
 --
 * MaNV : FK, UNIQUE
 * TenDangNhap : UNIQUE
 MatKhauHash
 VaiTro
 HoatDong
}
entity KhachHang {
 * MaKH : PK
 --
 HoTen
 SDT
 DiemTichLuy
}
entity Ban {
 * MaBan : PK
 --
 TenBan : UNIQUE
 KhuVuc
 TrangThai
}
entity DonHang {
 * MaDH : PK
 --
 * MaNV : FK
 * MaBan : FK
 MaKH : FK, NULL
 TongTien
 DiemDaCong
 TrangThai
 PhienBan : ROWVERSION
 ThoiGianTao
 ThoiGianThanhToan : NULL
}
entity ChiTietDonHang {
 * MaCTDH : PK
 --
 * MaDH : FK
 * MaSP : FK
 TenSPLucBan
 SoLuong
 DonGia
 ThanhTien : computed
 UNIQUE(MaDH, MaSP)
}
entity SanPham {
 * MaSP : PK
 --
 TenSP
 DanhMuc
 Gia
 MoTa
 TrangThai
}
NhanVien ||--o| TaiKhoan
NhanVien ||--o{ DonHang
KhachHang |o--o{ DonHang
Ban ||--o{ DonHang
DonHang ||--o{ ChiTietDonHang
SanPham ||--o{ ChiTietDonHang
@enduml
```

## Lưu đồ lưu đơn

Đối chiếu: `CoffeeService.save_order, db_connection.transaction`.

Kiểm tra giỏ và gộp số lượng trước khi mở giao dịch. Kiểm tra từng sản phẩm bên trong vòng lặp. Món đã có trong đơn dùng tên và đơn giá lịch sử. Món ngừng bán chỉ được giữ hoặc giảm số lượng cũ. Khi đổi bàn phải đồng bộ bàn mới và bàn cũ. Mọi ngoại lệ trong khối giao dịch đều dẫn đến rollback, kể cả lỗi đọc SQL, lấy khoá hoặc kiểm tra. Các nhánh rollback trong hình là cách trình bày gọn của cơ chế ngoại lệ này.

```plantuml
@startuml
skinparam backgroundColor white
skinparam dpi 200
skinparam shadowing false
skinparam defaultFontName "Times New Roman"
skinparam defaultFontSize 18
skinparam activityBackgroundColor white
skinparam activityDiamondBackgroundColor white
skinparam ArrowColor black
start
:Kiểm tra giỏ, mã và số lượng\nGộp quantities, kiểm tra tổng mỗi món ≤ 999;
if (Dữ liệu đầu vào hợp lệ?) then (Có)
else (Không)
 :Báo lỗi, chưa mở giao dịch;
 stop
endif
:Mở giao dịch, lấy khoá CoffeeOrders;
if (Quyền, bàn, khách và đơn hợp lệ?\nĐơn sửa có đúng phiên bản?) then (Có)
 :Chuẩn bị lines và tổng tiền = 0;
else (Không)
 :Rollback, báo lỗi;
 stop
endif
while (Còn mã sản phẩm trong quantities?) is (Có)
 if (Món tồn tại và được phép bán\nhoặc giữ số lượng lịch sử?) then (Có)
  :Lấy tên và giá lịch sử nếu đã có\nThêm dòng và cộng số lượng × đơn giá;
 else (Không)
  :Rollback, báo lỗi;
  stop
 endif
endwhile (Không)
:Thêm đơn hoặc cập nhật đơn cũ\nGhi chi tiết và đồng bộ bàn;
if (Ghi SQL và commit thành công?) then (Có)
 :Trả mã đơn, làm mới giao diện;
else (Không)
 :Rollback, báo lỗi;
endif
stop
@enduml
```

## Lưu đồ thanh toán

Đối chiếu: `PaymentDialog.change_amount/confirm, CoffeeService.finish_order, db_connection.transaction`.

Số tiền nhận và tiền thừa được kiểm tra trên giao diện, không lưu vào SQL. Giao diện luôn truyền expected_version. Dịch vụ cho phép tham số này là None khi được gọi riêng. Điểm chỉ cộng cho khách được chọn, theo phép chia lấy phần nguyên. Khối giao dịch cập nhật đơn, khách và bàn cùng nhau. Mọi ngoại lệ trong khối giao dịch đều rollback. Nếu người dùng đóng hộp thoại khi đang nhập thì thao tác kết thúc và chưa ghi thanh toán. Sơ đồ mô tả nhánh thanh toán, nhánh huỷ dùng cùng finish_order nhưng không cộng điểm.

```plantuml
@startuml
skinparam backgroundColor white
skinparam dpi 200
skinparam shadowing false
skinparam defaultFontName "Times New Roman"
skinparam defaultFontSize 18
skinparam activityBackgroundColor white
skinparam activityDiamondBackgroundColor white
skinparam ArrowColor black
start
repeat
 :Nhập tiền khách đưa trên giao diện;
 :Kiểm tra số tiền và tính tiền thừa;
repeat while (Số tiền sai hoặc chưa đủ?) is (Có) not (Không)
:Nhân viên xác nhận đã nhận tiền;
:Mở giao dịch, lấy khoá CoffeeOrders;
if (Đúng quyền, đơn đang xử lý\nvà đúng phiên bản?) then (Có)
 :Tính điểm = tổng tiền // 10.000 nếu có khách\nKhông có khách thì điểm = 0;
 :Ghi trạng thái, thời gian thanh toán\nvà DiemDaCong;
 if (Điểm > 0?) then (Có)
  :Cộng điểm cho khách hàng;
 endif
 :Đồng bộ trạng thái bàn;
else (Không)
 :Rollback, báo lỗi;
 stop
endif
if (Ghi SQL và commit thành công?) then (Có)
 :Làm mới giao diện, thông báo thành công;
else (Không)
 :Rollback, báo lỗi;
endif
stop
@enduml
```
