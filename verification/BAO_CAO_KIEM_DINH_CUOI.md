# Biên bản kiểm định cuối dự án sys-coffe

Thời điểm chốt: 2026-10-22T23:12:04+07:00. Múi giờ UTC+7.

Kết luận: SẴN SÀNG NỘP trong phạm vi các điều kiện A–E bên dưới. Không cam kết điểm số, không coi các giới hạn chưa thử là kết quả đạt.

## Phạm vi và bảo toàn

Nhánh main, commit 7af74062bae32226ce0f14c11df0c60af213eab0. Repository https://github.com/fmdev23/sys-coffe. Không push, reset, commit hoặc sửa mã ứng dụng. Đã đọc 21 tệp Python, cấu trúc SQL, 19 phương thức test, README, bốn tài liệu MD được chỉ định, cả hai PDF và toàn bộ Word đầu vào.

Lệnh Git được thực hiện đầu tiên trước khi tạo thư mục kiểm định. Ban đầu chỉ có tệp chưa theo dõi docs/BaoCao_QuanLyQuanCaPhe_DoiChieu_GitHub.docx. git_ban_dau.json được ghi sau khi tạo verification nên có thêm thư mục này. Không sửa tệp chưa theo dõi của người dùng.

Đối chiếu SHA-256 xác nhận 330 tệp đầu vào vẫn nguyên vẹn, gồm báo cáo gốc, ảnh DFD, ảnh giao diện, các tài liệu và .report_work. Dữ liệu gốc được đọc, chỉ các database kiểm thử riêng được ghi và dọn.

## Môi trường thực tế

| Thành phần | Kết quả |
|---|---|
| Python | 3.14.3 |
| pyodbc | 5.3.0 |
| Tcl/Tk | 8.6.15 |
| SQL Server | 16.0.1210.3, Express Edition (64-bit) |
| ODBC | ODBC Driver 17 for SQL Server có sẵn và được connect() chọn |
| IDE | VS Code 1.140.0, x64, người dùng xác nhận và code --version trả về |
| Hệ điều hành | Windows 11, build 26300 |
| Xác thực SQL | Windows Authentication, không dùng mật khẩu SQL trong nhật ký |

SQL trả thời điểm máy chủ theo UTC. Nhật ký kiểm định ghi rõ UTC+7, không gán múi giờ máy chủ thành giờ địa phương.

## Lệnh và kết quả chạy mới

```text
python --version
python -m pip show pyodbc
python -m tkinter
code --version
python -B -m unittest discover -s tests -v
```

Python mặc định qua WindowsApps không khởi động. Công cụ kiểm định dùng Python đã cài tại C:/Users/PC/AppData/Local/Python/pythoncore-3.14-64/python.exe và chỉ thêm thư mục này vào PATH của tiến trình con. Không đổi PATH hệ thống. Truy vấn ngày giờ ban đầu gặp kiểu datetimeoffset không được pyodbc đọc trực tiếp. Công cụ được sửa để CONVERT sang NVARCHAR trong truy vấn chỉ đọc.

Bắt đầu 2026-10-22T22:42:46+07:00, kết thúc 2026-10-22T22:43:06+07:00. unittest 19.656 giây, tiến trình 20.184908 giây. 19 đạt, 0 thất bại, 0 lỗi, 0 bỏ qua, mã thoát 0. stdout đầy đủ ở unittest_moi.stdout.txt (rỗng), stderr đầy đủ ở unittest_moi.stderr.txt. unittest mặc định ghi kết quả lên stderr, đây không phải dấu hiệu test lỗi.

Database được quan sát: CoffeeTest_00ad630653c647a78736a4e7375059ec. Trước và sau không có database thử. Bộ test cấp tên bằng uuid4, đăng ký addModuleCleanup trước setup. cleanup kiểm tra mẫu tên và so với database gốc rồi chỉ ALTER/DROP đúng tên do lần chạy cấp. Truy vấn đọc cuối xác nhận mọi database do các lần kiểm định này tạo đều không còn.

Kiểm tra cú pháp AST cho đủ 21 tệp, không tạo bytecode. Một số hộp thông báo Tkinter được thay trong bộ unittest. SQL Server, kết nối, ràng buộc và giao dịch đều thật.

### Kịch bản bổ sung

Ngày 22/10, tổng 80.000, nhận 100.000, thừa 20.000, khách cộng 8 điểm và bàn Trống được kiểm tra lại bằng PaymentDialog và SQL thật. Dữ liệu 13 món/12 đơn xác nhận TOP 10: tổng toàn kỳ 245.000, tổng 10 dòng 212.000 đồng. CSV mới có BOM UTF-8. Chỉ filedialog.asksaveasfilename được cung cấp đường dẫn tự động, không thay truy vấn hoặc hàm ghi CSV. Không coi đây là kiểm tra chọn tệp bằng chuột.

Hai lần mở UI trước đó đóng trước khi lấy được ảnh xác nhận. Nhật ký bo_sung_lan_dau_chua_hoan_tat.json và bo_sung_lan_hai_chua_hoan_tat.json được giữ riêng, không tính đạt. bo_sung_tien_do.json là lần hoàn tất sau đó, mã thoát lưu ở bo_sung_exit_code.txt. Thời gian bổ sung không cộng vào thời gian unittest.

### Chứng cứ lịch sử

CSV tại docs và thư mục SoLieuCSVProject giống SHA-256, kỳ 14–20/10/2026, 8 đơn, 1.200.000 đồng. Cà phê đen 30 ly/750.000, cà phê sữa 15 ly/450.000. evidence_new.json lưu sự kiện ngày 20/10. Database lịch sử không còn nên chỉ xác nhận tính nhất quán tập tin và nhật ký. evidence.json là lần khác ngày 04/10, không dùng ghép với kỳ 14–20/10. tests.txt cũ có 19 test OK trong 19,801 giây nhưng không tự chứng minh thời điểm hay commit. Không dùng các thời gian 18,003/16,156 giây thiếu log tương ứng trong FINAL.

## Ma trận báo cáo và mã nguồn

| Mục | Tuyên bố | Tệp và class/hàm | Test | Bằng chứng | Kết luận |
|---|---|---|---|---|---|
| 1, 2, 3 và 4.2 | Băm và xác thực mật khẩu | security.py:9,18 / hash_password, verify_password | test_password_hash_and_login | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Thiết lập lặp lại không nhân đôi dữ liệu | database_setup.py:78 / setup | test_setup_idempotent | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Kiểm tra giá, tên, điện thoại và điểm | models/service.py:39,53,162 / price, phone, save_entity | test_validation | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Thêm, đọc, sửa, xóa danh mục | models/service.py:141,162,209 / list_entities, save_entity, delete_entity | test_crud_all_entities | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Tài khoản, mật khẩu và phiên bị khóa | models/service.py:116,243,292,312 / save_account, delete_account, change_password, _authorize | test_account_crud_password_and_disabled_session | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Bảo vệ quản lý đang sử dụng | models/service.py:243,292 / save_account, delete_account | test_protect_current_manager | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Chặn thao tác quản trị của nhân viên | models/service.py:116 / _authorize | test_staff_permissions_enforced_in_service | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Tạo, sửa, chuyển bàn và xóa đơn hợp lệ | models/service.py:396,506 / save_order, delete_order | test_order_create_edit_move_and_delete | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Lỗi lưu đơn hoàn tác dữ liệu | models/service.py:396 / save_order | test_order_failure_rolls_back | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Giữ giá và tên lúc bán, hạn chế món ngừng bán | models/service.py:396 / save_order | test_snapshot_price_and_discontinued_product | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Thanh toán, tích điểm và giữ lịch sử | models/service.py:481,506 / finish_order, delete_order | test_payment_points_and_preserve_history | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Hủy và xóa đúng trạng thái | models/service.py:476,481,506 / finish_order, delete_order, _sync_table | test_cancel_and_delete | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Lỗi SQL khi cộng điểm hoàn tác cả đơn và bàn | models/service.py:481 / finish_order | test_payment_database_failure_rolls_back_all_changes | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Phiên bản cũ không ghi đè hoặc thanh toán | models/service.py:396,481 / save_order, finish_order | test_stale_order_cannot_overwrite_or_pay | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Hai thao tác giữ cùng bàn chỉ một thành công | models/service.py:86,396 / save_order, _lock | test_concurrent_table_reservation | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Hai thao tác thanh toán không cộng điểm hai lần | models/service.py:86,481 / finish_order, _lock | test_concurrent_payment_only_once | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Kỳ ngày, tháng và loại đơn hủy/chưa thanh toán | models/service.py:60,531,559 / statistics, revenue_series, report_period | test_statistics_dates_month_and_excluded_statuses | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Control bo góc, chuột, bàn phím, trạng thái khóa | ui/theme.py:14 / rounded_controls | test_rounded_controls_mouse_keyboard_and_disabled_state | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 1, 2, 3 và 4.2 | Tkinter đăng nhập, trang theo vai trò, biểu mẫu, gọi món | ui/main_window.py:16 / MainWindow | test_tkinter_login_pages_forms_and_order_flow | unittest_moi.stderr.txt và unittest_moi.json | ĐÚNG |
| 2.3 | Bảy bảng nghiệp vụ, không tính sysdiagrams của SSMS | database_setup.py / SCHEMA | Không có bài riêng | moi_truong.json, SCHEMA trong database_setup.py | ĐÚNG |
| 2.3 | ROWVERSION là phiên bản nhị phân, không phải thời điểm | database_setup.py / SCHEMA | test_stale_order_cannot_overwrite_or_pay | moi_truong.json: PhienBan kiểu timestamp, tài liệu Microsoft rowversion | ĐÚNG. timestamp là tên đồng nghĩa SQL, không phải datetime. |
| 2.3 | Chỉ mục duy nhất có điều kiện cho bàn đang có đơn | database_setup.py / SCHEMA | test_concurrent_table_reservation | moi_truong.json: UX_Ban_DonDangXuLy unique + filter | ĐÚNG |
| 3.3 | Khóa sp_getapplock và giao dịch | models/service.py:86,396,481 / _lock, save_order, finish_order | test_concurrent_payment_only_once | Mã nguồn, các test đồng thời và rollback | ĐÚNG. Khóa ứng dụng chờ tối đa 10 giây. Đây không phải thử tải nhiều máy. |
| 2.6, 4.3 | Chặn tiền sai hoặc thiếu tại giao diện | ui/payment_dialog.py:56,62,72 / change_amount, update_change, confirm | test_tkinter_login_pages_forms_and_order_flow | bo_sung_tien_do.json, phép thử tiền 80.000 nhận 100.000 | ĐÚNG. Dịch vụ không nhận tiền khách đưa. Kiểm tra UI riêng không phải ràng buộc SQL. |
| 2.6 | expected_version tùy chọn ở dịch vụ, được GUI thanh toán truyền | models/service.py:481 / finish_order | test_stale_order_cannot_overwrite_or_pay | Mã nguồn + ui/payment_dialog.py:confirm | ĐÚNG |
| 2.4, 4.3 | TOP 10 và tổng toàn kỳ có thể khác tổng dòng sản phẩm | models/service.py:531 / statistics | Không có bài riêng | bo_sung_tien_do.json, doanh_thu_kiem_dinh_moi.csv | ĐÚNG. 13 món, 12 đơn, tổng 245.000, 10 dòng 212.000 đồng. Ngoài 19 phương thức. |
| 2.4, 4.3 | CSV UTF-8 có BOM và ghi đúng dữ liệu SQL | ui/statistics_tab.py:112 / export | Không có bài riêng | csv_lich_su.json và doanh_thu_kiem_dinh_moi.csv | ĐÚNG. Kịch bản mới chỉ thay hàm chọn đường dẫn, không thay SQL, writer hoặc dữ liệu. Chưa chứng minh chọn tệp bằng chuột. |
| 2.4 | Tên thống kê từ danh mục hiện tại, tên hóa đơn từ lúc bán | models/service.py:396,531 / statistics, save_order | test_snapshot_price_and_discontinued_product | Mã truy vấn statistics và phép thử snapshot | ĐÚNG. Test lịch sử giá không kiểm tra mọi tình huống đổi tên trên báo cáo thống kê. |
| 3.1 | VS Code 1.140.0 x64, Python 3.14.3, pyodbc 5.3.0, SQL 16.0.1210.3 | verification/moi_truong.json / Lệnh phiên bản và truy vấn chỉ đọc | Không có bài riêng | moi_truong.json, vscode_version.stdout.txt, pyodbc_pip.stdout.txt | ĐÚNG |
| 4.2 | 19 đạt, không lỗi hoặc bỏ qua, mã thoát 0 | tests/test_coffee.py:46 / CoffeeTests | Không có bài riêng | unittest_moi.json, unittest_moi.stderr.txt | ĐÚNG |
| 4.3 | CSV lịch sử 14–20/10, 8 đơn, 1.200.000 đồng | docs/doanh_thu_kiem_tra.csv / Không áp dụng | Không có bài riêng | csv_lich_su.json và .report_work/evidence_new.json | ĐÚNG. Chỉ xác nhận nhất quán của tập tin và nhật ký lưu, không xác nhận SQL lịch sử còn tồn tại. |
| 4.3 | Tái truy vấn database trình diễn ngày 20/10/2026 | verification/moi_truong.json / Không áp dụng | Không có bài riêng | historical_demo_database_present=false | THIẾU CHỨNG CỨ. Database cũ không còn. Đã giới hạn khẳng định trong báo cáo. |
| 4.4 | Tắt máy, mất điện, tải lớn, nhiều máy hoặc kiểm định bảo mật độc lập | tests/test_coffee.py:46 / CoffeeTests | Không có bài riêng | Không có phép thử các tình huống này | THIẾU CHỨNG CỨ. Không kết luận đạt, ghi giới hạn tại mục 4.4 và hướng phát triển. |
| 4.4 | Ảnh giao diện mới và chọn đường dẫn CSV bằng chuột trong lần mới | verification/bo_sung_lan_dau_chua_hoan_tat.json / Không áp dụng | Không có bài riêng | Hai nhật ký chưa hoàn tất và thông báo Sky cửa sổ đã đóng | THIẾU CHỨNG CỨ. Giữ ảnh cũ, không tạo hoặc tráo ảnh. Kết quả UI tự động trong 19 test vẫn có. |
| Giới thiệu | DFD giữ nguyên hai tác nhân và 12 luồng | sodo/dfd_muc_0.puml / Không áp dụng | Không có bài riêng | docs/DFD_Muc0.png, sodo/dfd_muc_0.puml, bảng 2 và đối chiếu mã | ĐÚNG. Ảnh gốc độ phân giải thấp, giải thích nhãn bằng Bảng 2, không sửa hình. |
| Tài liệu cũ | CoffeeService.login, guarded, transaction/contextmanager còn được một số MD mô tả | docs/BAO_VE.md / Không còn các thành phần này | Không có bài riêng | Đối chiếu AST 21 tệp và docs/BAO_VE.md, docs/DanhMuc_SoDo.md | SAI. Tài liệu cũ được bảo toàn theo phạm vi kiểm định. FINAL dùng login tự do và try/except/finally thật. |
| Kết luận | Kho nguyên liệu, in hóa đơn, nhập CSV, thanh toán ngân hàng đã có | models/service.py / Không áp dụng | Không có bài riêng | Không có chức năng này trong mã | KHÔNG ÁP DỤNG. Chỉ nêu hướng phát triển, không ghi là chức năng hoàn thành. |

## Phát hiện và xử lý

15 điểm rà soát: 11 đã xử lý, 4 giới hạn còn mở. Không phát hiện lỗi ứng dụng có thể chứng minh trong phạm vi chạy. Không sửa mã ứng dụng, không đổi test để ép đạt. Đây không phải khẳng định ứng dụng không có lỗi.

| Loại | Phát hiện | Xử lý hoặc giới hạn | Trạng thái |
|---|---|---|---|
| Báo cáo | Thiếu IDE được xác nhận | Thêm VS Code và kết quả code --version | ĐÃ XỬ LÝ |
| Báo cáo | Thời gian cũ 18,003/16,156 giây thiếu log tương ứng | Thay bằng lần mới 19,656 giây, exit 0. Log lịch sử thật ghi 19,801 giây | ĐÃ XỬ LÝ |
| Báo cáo | Chưa nêu rõ người/công cụ thực thi | Ghi Codex thực thi tự động, mô tả phạm vi mock thông báo | ĐÃ XỬ LÝ |
| Báo cáo | Dễ gộp số liệu cũ, ảnh cũ với lần mới | Ghi riêng ngày 20/10 và 22/10, chú thích bảng lịch sử | ĐÃ XỬ LÝ |
| Báo cáo | CSV chưa giải thích giới hạn TOP 10 | Thêm giới hạn và kịch bản SQL/CSV thật 13 món | ĐÃ XỬ LÝ |
| Báo cáo | Kiểm tra tiền dễ bị hiểu là ràng buộc dịch vụ | Giải thích kiểm tra tại PaymentDialog, không lưu tiền nhận/thừa | ĐÃ XỬ LÝ |
| Báo cáo | Chưa nhấn mạnh expected_version là tùy chọn | Mô tả đúng chữ ký dịch vụ và lời gọi GUI | ĐÃ XỬ LÝ |
| Trình bày | Đoạn ngắn tràn sang trang riêng sau khi biên tập | Rút gọn nội dung lặp, mục lục đơn dòng, giữ ảnh/bảng/khổ lề | ĐÃ XỬ LÝ |
| Tham khảo | Nguồn cần được truy cập lại cho lần kiểm định mới | Kiểm tra nguồn chính, cập nhật ngày 22/10 và liên kết Python 3.14 | ĐÃ XỬ LÝ |
| Môi trường | Lệnh python mặc định trỏ WindowsApps không khởi động | Dùng bản Python đã cài, thêm PATH chỉ cho tiến trình con | ĐÃ XỬ LÝ |
| Công cụ kiểm định | pyodbc không đọc trực tiếp datetimeoffset kiểu -155 | Chuyển kiểu sang NVARCHAR trong truy vấn chỉ đọc, không sửa ứng dụng | ĐÃ XỬ LÝ |
| Tài liệu cũ | Một số MD mô tả API và số hình cũ | Giữ nguyên, đánh dấu SAI và dùng ma trận mới làm căn cứ | CÒN GIỚI HẠN |
| Bằng chứng lịch sử | Database ngày 20/10 không còn | CSV và nhật ký khớp, không thể tái xác nhận SQL lịch sử | CÒN GIỚI HẠN |
| Phạm vi thử nghiệm | Chưa tắt máy, mất điện, thử tải hoặc đánh giá bảo mật độc lập | Báo cáo nêu rõ chưa thực hiện, không kết luận đạt | CÒN GIỚI HẠN |
| Bằng chứng giao diện | Hai lần mở UI bổ sung đóng trước khi lấy được ảnh xác nhận | Lưu cả hai nhật ký, hoàn tất bổ sung bằng API/Tkinter và cấp đường dẫn tự động | CÒN GIỚI HẠN |

## Đối chiếu sơ đồ

DFD gốc giữ nguyên byte, không tráo hình. Hai tác nhân và 12 luồng khớp phạm vi chính. Chưa tách luồng đổi mật khẩu, các thao tác phục vụ mà quản lý kế thừa và bước ghi CSV thành luồng riêng. Đây là phần diễn giải chưa chi tiết của sơ đồ ngữ cảnh, không xác nhận có luồng nghiệp vụ khác với mã. Bảng 2 chép nhãn để khắc phục chữ nhỏ. SQL là nơi lưu chính, CSV là đầu ra của quản lý. Các chi tiết kho dữ liệu đặt ở thiết kế quan hệ, không tự thêm vào DFD gốc.

Bốn sơ đồ thiết kế được đối chiếu với hàm, điều kiện và bảy bảng thật. ERD thể hiện đúng tài khoản bắt buộc có nhân viên, nhân viên có tối đa một tài khoản, khách của đơn có thể trống. SQL khóa ngoại cho phép đơn chưa có dòng chi tiết, nhưng save_order() bắt buộc giỏ không rỗng. Lưu đồ thanh toán phân biệt kiểm tra tiền tại UI và giao dịch cập nhật dữ liệu.

Không render lại hoặc chỉnh ảnh sơ đồ trong vòng này. Mã tương đương nằm trong sodo/*.puml và README.md. docs/DanhMuc_SoDo.md, docs/SoDo_PlantUML.md còn số hình/API cũ, chỉ dùng như lịch sử. Nếu giảng viên yêu cầu thể hiện riêng bước ghi CSV hoặc thay DFD, cần sinh viên quyết định và cung cấp bản vẽ mới. Không tự sửa bản gốc.

## Checklist yêu cầu và trình bày

Mẫu Python ưu tiên cấu trúc, DNC áp dụng phần trình bày phù hợp. Các ngoại lệ của tài liệu luận văn đã được giải thích trong README có sẵn, được giữ nguyên. Danh sách dưới ghi lại kết quả đối chiếu mới.

| Số | Yêu cầu | Kết luận | Căn cứ hoặc lý do |
|---:|---|---|---|
| 1 | Mẫu Python trang 1: bìa đúng tên trường, đơn vị, học phần, tên đề tài tiếng Việt và tiếng Anh, sinh viên, mã số, lớp và thời điểm báo cáo. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 2 | Mẫu Python trang 2: khổ A4, lề trái 3,5 cm, phải 2 cm, trên 2 cm và dưới 2 cm. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 3 | Mẫu Python trang 2: bảng mã Unicode, Times New Roman, cỡ 13, giãn dòng 1,2. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 4 | Mẫu Python trang 2: không quá 60 trang, không tính phụ lục. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 5 | Mẫu Python trang 2: mục lục tự động, có liên kết và số trang đúng. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 6 | Mẫu Python trang 2: danh mục đồ thị, biểu bảng và hình ảnh đồng bộ nội dung. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 7 | Mẫu Python trang 2: phần Giới thiệu có Đặt vấn đề trước Những nghiên cứu liên quan. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 8 | Mẫu Python trang 2: khảo sát ít nhất năm ứng dụng hoặc thư viện thật và phân tích kỹ một ứng dụng chính. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 9 | Mẫu Python trang 2: tiếp theo là Mục tiêu rồi Đối tượng và phạm vi nghiên cứu. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 10 | Mẫu Python trang 2: Giới thiệu có DFD cấp 0 và giải thích đường đi từ người dùng, Python đến tệp CSV. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 11 | Mẫu Python trang 2: Chương 1 có tên Đặc tả yêu cầu, mô tả đúng các chức năng thật. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 12 | Mẫu Python trang 2: Chương 2 có tên Thiết kế giải pháp. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 13 | Mẫu Python trang 2: có sơ đồ phân cấp hàm dựa trên tên hàm thật. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 14 | Mẫu Python trang 2: có lưu đồ thuật toán cho các chức năng quan trọng. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 15 | Mẫu Python trang 2: mô tả danh sách, từ điển và định dạng các cột CSV thật. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 16 | Mẫu Python trang 3: Chương 3 có tên Cài đặt giải pháp. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 17 | Mẫu Python trang 3: ghi phiên bản Python và môi trường phát triển có bằng chứng, không tự gán IDE chưa dùng. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 18 | Mẫu Python trang 3: trích mã nguồn quan trọng và giải thích đủ tám nội dung học phần. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 19 | Mẫu Python trang 3: Chương 4 có tên Đánh giá kiểm thử. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 20 | Mẫu Python trang 3: có mục tiêu, phương pháp, kịch bản, kết quả thực tế và đánh giá mục tiêu. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 21 | Mẫu Python trang 3: thử nhập liệu hợp lệ và sai. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 22 | Mẫu Python trang 3: thử tính tiền, doanh thu và điểm theo mã thực. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 23 | Mẫu Python trang 3: thử lưu trữ sau khi đóng và mở lại, phân biệt với tình huống tắt máy chưa thực hiện. | ĐẠT TRONG PHẠM VI | Có chứng cứ kết nối mới và đọc dữ liệu đã commit. Tắt máy chưa thực hiện, không đánh dấu đạt tình huống đó. |
| 24 | Mẫu Python trang 3: kết luận có kết quả đạt được và hướng phát triển. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 25 | Mẫu Python trang 3: tài liệu tham khảo thật, có liên kết và được dùng trong nội dung. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 26 | Mẫu Python trang 3: phụ lục hướng dẫn cài Python, phụ thuộc, cơ sở dữ liệu và chạy chương trình. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 27 | DNC trang 3: giấy trắng, in một mặt, header và footer cách mép 1 cm, không đặt tên đề tài hoặc người trong đầu và chân trang. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 28 | DNC trang 3: thụt đầu đoạn 1 cm, cách trước 6 pt và sau 0 pt. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 29 | DNC trang 3: bảng, hình, tài liệu tham khảo và phụ lục giãn dòng đơn. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 30 | DNC trang 3: tiếng Việt nhất quán, thuật ngữ ngoại ngữ cần thiết được giải thích. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 31 | DNC trang 3: mỗi chương sang trang, tên chương hai dòng, chữ hoa, đậm, cỡ 14, căn giữa. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 32 | DNC trang 4: mục cấp một chữ hoa đậm sát trái, mục cấp hai chữ thường đậm cách trái 1 cm, không quá bốn cấp số. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 33 | DNC trang 4: tiêu đề chương và mục không có dấu chấm hoặc dấu hai chấm ở cuối. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 34 | DNC trang 4: số trang cỡ 13 căn giữa chân trang, phần đầu số La Mã và nội dung số Ả Rập. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 35 | DNC trang 4: bảng được nhắc trước khi xuất hiện, không cắt hàng, lặp tiêu đề cột nếu qua trang. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 36 | DNC trang 4 và 5: hình được nhắc trước, nằm cùng dòng văn bản, căn giữa, không có khung ngoài. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 37 | DNC trang 5: hình và bảng đánh số liên tục theo chương, chú thích cỡ 13, tên bảng ở trên căn trái và tên hình ở dưới căn giữa. | ĐẠT | Giữ ngoại lệ do người dùng chấp thuận: Giới thiệu dùng Hình 1, Bảng 1, Bảng 2. Chương dùng số x.y, kiểm tra liên tục. |
| 38 | DNC trang 5: công thức trình bày bằng công cụ toán, đánh số, giải thích ký hiệu và đơn vị khi xuất hiện lần đầu. | KHÔNG ÁP DỤNG | Không có công thức toán độc lập cần đánh số. Phép tính tiền là ví dụ số, thuật toán nằm trong mã. |
| 39 | DNC trang 5: nguồn hình hoặc bảng lấy từ bên ngoài đặt dưới, căn giữa, nghiêng cỡ 11 và có trong tài liệu tham khảo. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 40 | DNC trang 5 và 6: cột, hàng, đơn vị rõ nghĩa, số thập phân dấu phẩy, hàng nghìn dấu chấm, số liệu căn phải. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 41 | DNC trang 6: trích dẫn tác giả và năm, không ghi học hàm hoặc chức danh. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 42 | DNC trang 6 và 7: tài liệu trích dẫn và danh mục khớp nhau, chia theo ngôn ngữ, sắp xếp theo tác giả, giữ nguyên tên tài liệu nước ngoài. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 43 | DNC trang 7: tài liệu nhiều dòng thụt dòng tiếp theo 1 cm. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 44 | DNC trang 12: mục lục đến mục cấp hai, chỉ liệt kê tên chung của phụ lục. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 45 | DNC trang 12: danh sách hình và bảng có đúng tên và đúng trang. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 46 | DNC trang 13: từ viết tắt được giải thích ở lần đầu và trong danh mục khi cần. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 47 | DNC trang 15 đến 17: ghi thông tin nguồn theo loại tài liệu, website có tác giả, năm nếu xác định được, địa chỉ và ngày truy cập thật. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 48 | DNC trang 17: phụ lục đặt sau tài liệu tham khảo. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 49 | Không áp dụng lề trên và dưới 2,5 cm của DNC vì mẫu học phần ưu tiên lề 2 cm. | KHÔNG ÁP DỤNG | Không áp dụng lề trên và dưới 2,5 cm của DNC vì mẫu học phần ưu tiên lề 2 cm. |
| 50 | Không áp dụng mẫu bìa và màu bìa khóa luận ở DNC trang 8 vì giảng viên cung cấp bìa báo cáo học phần riêng. | KHÔNG ÁP DỤNG | Không áp dụng mẫu bìa và màu bìa khóa luận ở DNC trang 8 vì giảng viên cung cấp bìa báo cáo học phần riêng. |
| 51 | Không áp dụng phụ bìa ở DNC trang 9 vì mẫu học phần không yêu cầu và người dùng đã chọn giữ bố cục học phần. | KHÔNG ÁP DỤNG | Không áp dụng phụ bìa ở DNC trang 9 vì mẫu học phần không yêu cầu và người dùng đã chọn giữ bố cục học phần. |
| 52 | Không áp dụng trang chấp thuận hội đồng ở DNC trang 10 vì đây là báo cáo học phần, chưa có kết quả hội đồng. | KHÔNG ÁP DỤNG | Không áp dụng trang chấp thuận hội đồng ở DNC trang 10 vì đây là báo cáo học phần, chưa có kết quả hội đồng. |
| 53 | Không áp dụng lời cảm tạ ở DNC trang 11 vì mẫu học phần không yêu cầu. | KHÔNG ÁP DỤNG | Không áp dụng lời cảm tạ ở DNC trang 11 vì mẫu học phần không yêu cầu. |
| 54 | Không áp dụng cam kết khóa luận ở DNC trang 11 vì không phải khóa luận và không được tự xác nhận thành tích nghiên cứu. | KHÔNG ÁP DỤNG | Không áp dụng cam kết khóa luận ở DNC trang 11 vì không phải khóa luận và không được tự xác nhận thành tích nghiên cứu. |
| 55 | Không áp dụng nhận xét cơ quan thực tập vì dự án không có cơ quan thực tập được xác nhận. | KHÔNG ÁP DỤNG | Không áp dụng nhận xét cơ quan thực tập vì dự án không có cơ quan thực tập được xác nhận. |
| 56 | Không áp dụng cấu trúc năm chương nghiên cứu ở DNC trang 13 đến 15 vì mẫu Python yêu cầu bốn chương cụ thể. | KHÔNG ÁP DỤNG | Không áp dụng cấu trúc năm chương nghiên cứu ở DNC trang 13 đến 15 vì mẫu Python yêu cầu bốn chương cụ thể. |
| 57 | Không áp dụng minh họa khảo sát địa bàn, thí nghiệm và giấy phép dữ liệu đề tài cấp khoa vì dự án dùng dữ liệu thử tự tạo, không thực hiện các nội dung đó. | KHÔNG ÁP DỤNG | Không áp dụng minh họa khảo sát địa bàn, thí nghiệm và giấy phép dữ liệu đề tài cấp khoa vì dự án dùng dữ liệu thử tự tạo, không thực hiện các nội dung đó. |
| 58 | Không áp dụng ví dụ trích dẫn sách, hội thảo hoặc luận án không được sử dụng. Chỉ áp dụng quy tắc phù hợp nguồn thực tế. | KHÔNG ÁP DỤNG | Không áp dụng ví dụ trích dẫn sách, hội thảo hoặc luận án không được sử dụng. Chỉ áp dụng quy tắc phù hợp nguồn thực tế. |
| 59 | Yêu cầu người dùng: giữ nguyên tất cả ảnh và tệp gốc DFD PowerDesigner, chỉ nêu chênh lệch và tạo mã tương đương để đối chiếu. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 60 | Yêu cầu người dùng: Python đơn giản, không decorator, không kỹ thuật hoặc thư viện mới, giữ hành vi. | ĐẠT | Không sửa mã ứng dụng, không thêm thư viện. AST 21 tệp và bộ 19 test đã được kiểm tra. |
| 61 | Yêu cầu người dùng: một README.md duy nhất, gộp tài liệu và xóa tài liệu Markdown thừa. | KHÔNG ÁP DỤNG | Yêu cầu kiểm định mới ưu tiên bảo toàn tài liệu và chứng cứ cũ, đồng thời bắt buộc tạo verification/BAO_CAO_KIEM_DINH_CUOI.md. Không dọn hoặc xóa tài liệu cũ. |
| 62 | Yêu cầu người dùng: một thư mục hình sơ đồ, mã PlantUML có nghĩa, render bằng Java trên máy. | KHÔNG ÁP DỤNG | Yêu cầu kiểm định mới ưu tiên bảo toàn tài liệu và chứng cứ cũ, đồng thời bắt buộc tạo verification/BAO_CAO_KIEM_DINH_CUOI.md. Không dọn hoặc xóa tài liệu cũ. |
| 63 | Yêu cầu người dùng: mọi bảng có đầy đủ đường viền đơn và tiêu đề cụ thể. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 64 | Yêu cầu người dùng: không mã chức năng tự đặt, không G.1, không emoji, không placeholder trong báo cáo. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 65 | Yêu cầu người dùng: chạy thật các chức năng chính, ghi nhật ký và kết quả có bằng chứng. | ĐẠT | unittest_moi.json và bo_sung_tien_do.json. Không xem hai lần UI chưa hoàn tất là đạt. |
| 66 | Yêu cầu người dùng: kiểm tra tự động số hình, bảng, mục lục, viền, ký tự và mở lại Word. | ĐẠT | Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang. |
| 67 | Yêu cầu người dùng: không còn bytecode, tệp tạm, log thử nghiệm, bản sao hoặc script thử không dùng. | KHÔNG ÁP DỤNG | Yêu cầu kiểm định mới ưu tiên bảo toàn tài liệu và chứng cứ cũ, đồng thời bắt buộc tạo verification/BAO_CAO_KIEM_DINH_CUOI.md. Không dọn hoặc xóa tài liệu cũ. |

## Kiểm định Word và trực quan

Tạo bản sao từ đúng DOCX đầu vào, chỉ sửa phần cần thiết trong OOXML. Giữ 15 bảng, 13 ảnh, bố cục bìa, các section và mã trích. So sánh SHA ảnh và kích thước inline cho thấy không thay đổi. Không tạo báo cáo mới từ tài liệu trắng.

Microsoft Word 16.0 cập nhật trường nhiều lượt, lưu và xuất PDF. render_docx.py của bộ công cụ tài liệu dùng PDF Word để tạo ảnh trang. Đã mở và xem đủ 34 trang. Số trang trước nội dung i–iv, nội dung 1–29. Kiểm tra 127 hàng bảng xác nhận từng hàng không bị tách qua hai trang. 60 PAGEREF khớp trang thực của bookmark, không liên kết nội bộ bị đứt. Có 12 chú thích hình và 15 chú thích bảng, số liên tục trong từng chương và ngoại lệ Giới thiệu đã được chấp thuận.

Khổ A4, lề trái 3,5 cm, phải/trên/dưới 2 cm, đầu/chân trang 1 cm. Nội dung Times New Roman 13, giãn 1,2, thụt 1 cm, trước 6 pt, sau 0. Bảng đầy đủ viền đơn, tiêu đề lặp, không tách hàng. Hình inline đúng tỷ lệ, chú thích dưới hình. Mục lục cấp 1–2 tự động, danh mục tự động. Đã kiểm tra không chấm phẩy, placeholder TODO, mã G.1/CN1 hoặc ký tự vô hình bất thường.

Hai hàm trích phone và finish_order có AST tương đương nguồn sau khi bỏ khác biệt khoảng trắng trong chuỗi SQL. Đây chỉ là thụt lề trình bày SQL, không thay câu lệnh hoặc logic. Không kết luận toàn bộ mã trình bày trong Word là bài kiểm thử độc lập.

## Hồ sơ bàn giao và tệp có thể dọn sau

Báo cáo nộp: docs/BaoCao_QuanLyQuanCaPhe_FINAL.docx. Nhật ký, ma trận, kết quả cấu trúc và SHA-256 đặt trong verification. manifest.json không tự băm chính nó để tránh tự tham chiếu. Các script kiểm định không là thư viện mới của ứng dụng, không sửa requirements.txt.

Không xóa .report_work, tài liệu cũ, PNG QA cũ trong sodo hoặc báo cáo đối chiếu GitHub của người dùng. Chúng có thể được xem xét dọn sau khi người dùng giữ đủ chứng cứ. Các ảnh QA của vòng này nằm riêng tại verification/trang_bao_cao. Bằng chứng và tệp bàn giao đều đặt trong thư mục dự án ở ổ D, không đưa nhật ký lên GitHub.

## Điều kiện nghiệm thu

| Điều kiện | Kết luận | Căn cứ |
|---|---|---|
| A | ĐẠT | Các tuyên bố trọng yếu có mã, phương thức thử hoặc chứng cứ cụ thể trong ma trận. Các nội dung thiếu chứng cứ được nêu là giới hạn. |
| B | ĐẠT | 19 phương thức chạy mới đạt, failure=0, error=0, skipped=0, mã thoát 0. Không sửa ứng dụng hoặc dùng SQL giả. |
| C | ĐẠT | CSV lịch sử 8 đơn/1.200.000 và CSV mới 12 đơn/245.000 được tách biệt. Hai lần UI chưa hoàn tất không tính đạt. |
| D | ĐẠT | Word mở lại được, 15 bảng, 13 ảnh nguyên vẹn, 34 trang đã render và xem, 60 tham chiếu trang khớp bookmark. |
| E | ĐẠT | Bản báo cáo đã bỏ khẳng định vượt chứng cứ. Các tài liệu MD cũ mâu thuẫn được đánh dấu, không dùng bác bỏ mã mới. |

Không còn BLOCKER theo A–E. Bốn giới hạn đã công khai ở trên vẫn cần giữ trong báo cáo. Nếu cần mở rộng chứng cứ, thực hiện tắt/khởi động lại máy sau khi lưu công việc, kiểm tra giao diện và chọn đường dẫn bằng chuột trên database riêng, hoặc cung cấp bản sao database lịch sử. Không cần bổ sung thông tin sinh viên hoặc IDE.
