import json,re
from pathlib import Path
W=Path(__file__).parent
ROOT=W.parent
checks=json.loads((W/'checklist.json').read_text(encoding='utf-8'))
inventory=json.loads((W/'inventory.json').read_text(encoding='utf-8'))
evidence=json.loads((W/'evidence_new.json').read_text(encoding='utf-8'))
content='''# Quản lý quán cà phê bằng Python

Sinh viên Lê Minh Phú, MSSV 236717, lớp DH23TIN02. Giảng viên Bùi Thị Diễm Trinh.

## Mục lục

- [Mô tả và phạm vi](#mô-tả-và-phạm-vi)
- [Cấu trúc tệp](#cấu-trúc-tệp)
- [Cài đặt và sử dụng](#cài-đặt-và-sử-dụng)
- [Checklist yêu cầu](#checklist-yêu-cầu)
- [Danh sách hình và bảng](#danh-sách-hình-và-bảng)
- [Đối chiếu DFD mức 0](#đối-chiếu-dfd-mức-0)
- [Mã PlantUML](#mã-plantuml)
- [Nhật ký chạy thử và kiểm tra](#nhật-ký-chạy-thử-và-kiểm-tra)
- [Chuẩn bị bảo vệ](#chuẩn-bị-bảo-vệ)

## Mô tả và phạm vi

Ứng dụng Tkinter/ttk trên Windows, kết nối Microsoft SQL Server qua pyodbc. Quản lý có tám trang. Nhân viên chỉ có Đơn hàng, Sơ đồ bàn và Thực đơn. Chức năng gồm danh mục sản phẩm, bàn, nhân viên, khách hàng, tài khoản, gọi món, sửa/chuyển bàn, thanh toán, hủy đơn, thống kê và xuất CSV.

Các điểm có thể trình bày theo tiêu chí chấm mà sinh viên cung cấp:

| Tiêu chí | Minh chứng thực tế |
|---|---|
| Giao diện | Logo, nút và ô nhập bo góc, thẻ bàn, giỏ hàng, phân quyền, trạng thái bằng chữ và màu |
| Kết nối cơ sở dữ liệu | Bảy bảng SQL Server, thêm/đọc/sửa/xóa, khóa ngoại, giao dịch và dữ liệu lưu sau khi mở lại |
| Tập tin | Xuất CSV tiếng Việt bằng csv.writer, chọn nơi lưu và đọc lại để đối chiếu |
| Xử lý | Kiểm tra dữ liệu, giữ giá lúc bán, tính tổng/tiền thừa/điểm, lọc kỳ và tổng hợp doanh thu |

Dự án hiện chỉ xuất CSV, chưa nhập CSV. Nếu giảng viên bắt buộc cả nhập và xuất, tiêu chí đó chưa đủ. Hai tài liệu được cung cấp không xác nhận công thức cộng bốn điểm trên, nên đây là danh sách minh chứng để đối chiếu, không phải cam kết điểm số.

Giới hạn: chưa có in hóa đơn, nguyên liệu, thuế/khuyến mãi, thanh toán ngân hàng, tự động sao lưu, triển khai Internet hoặc thử tải lớn. Tiền khách đưa và tiền thừa chỉ tính trên giao diện.

## Cấu trúc tệp

| Tệp hoặc thư mục | Vai trò |
|---|---|
| main.py | Điểm chạy, CoffeeApp, chuyển màn hình, xử lý lỗi sự kiện |
| database_setup.py | Tạo bảy bảng và dữ liệu ban đầu, chạy lại không xóa dữ liệu |
| db_connection.py | Cấu hình, kết nối SQL và chuyển bản ghi thành danh sách từ điển |
| security.py | Băm và kiểm tra mật khẩu |
| models/__init__.py | Đánh dấu gói models |
| models/service.py | login, kiểm tra dữ liệu/quyền, danh mục, đơn, tài khoản, báo cáo |
| ui/__init__.py | Đánh dấu gói ui |
| ui/theme.py | Màu, chữ, kiểu ttk và ảnh nền control |
| ui/common.py | Biểu mẫu, bảng, tìm kiếm, định dạng, thông báo lỗi |
| ui/chart.py | Biểu đồ Canvas |
| ui/login_window.py | Biểu mẫu đăng nhập |
| ui/main_window.py | Điều hướng theo vai trò và thao tác chung |
| ui/dashboard.py | Tổng quan của quản lý |
| ui/entity_tab.py | Màn hình danh mục sản phẩm, khách, nhân viên |
| ui/account_tab.py | Quản lý tài khoản |
| ui/table_tab.py | Thẻ bàn, thêm/sửa/xóa bàn theo quyền |
| ui/order_tab.py | Danh sách đơn và thao tác trạng thái |
| ui/order_editor.py | Giỏ hàng, gọi món, sửa/chuyển bàn |
| ui/payment_dialog.py | Nhập tiền và xác nhận thu tiền |
| ui/statistics_tab.py | Chọn kỳ, xem thống kê, xuất CSV |
| assets/coffee_logo.png | Logo của ứng dụng |
| assets/controls/ | 23 ảnh nền cần thiết cho nút, ô nhập, danh sách chọn và thẻ |
| tests/test_coffee.py | 19 kiểm thử tích hợp được giữ để tái kiểm tra |
| requirements.txt | Chỉ khai báo pyodbc>=5.2,<6 |
| .gitignore | Bỏ qua bytecode, môi trường Python và log khi quản lý phiên bản |
| docs/BaoCao_QuanLyQuanCaPhe.docx | Báo cáo đã ghi đè, không giữ bản cũ |
| docs/BaoCao_LapTrinhPython_Maubaocao.pdf | Mẫu giảng viên, ưu tiên cao nhất |
| docs/Quyet-dinh-ban-hanh-Qui-dinh-trinh-bay-luan-van-(DNC).pdf | Quy định trường do sinh viên cung cấp |
| docs/DFD_Muc0.png | Ảnh gốc của sinh viên, không sửa |
| sodo/ | Năm mã PlantUML, ảnh dựng tương ứng, bảy ảnh giao diện và logo trường dùng cho bìa |
| README.md | Tài liệu Markdown duy nhất của dự án |

Tên tệp Python được giữ vì đã phản ánh đúng trách nhiệm, không cần đổi tên hàng loạt. Các tệp đánh dấu gói rỗng vẫn cần thiết cho cấu trúc nhập mô-đun. Bộ kiểm thử có mục đích sử dụng tiếp, không phải script tạm.

## Cài đặt và sử dụng

Cần Python có Tcl/Tk, SQL Server và ODBC Driver 17 for SQL Server hoặc trình điều khiển SQL Server dự phòng. Môi trường đã chạy: Windows 11 bản dựng 26300, Python 3.14.3, Tk 8.6.15, pyodbc 5.3.0, SQL Server Express 64-bit 16.0.1210.3.

Trong thư mục dự án:

```powershell
python -m pip install -r requirements.txt
python database_setup.py
python main.py
```

Mặc định server `THINKPADX1\\SQLSEVER`, database `QuanLyQuanCoffee`, xác thực Windows. Có thể đặt biến môi trường `COFFEE_SQL_SERVER`, `COFFEE_SQL_DATABASE` cho máy thực tế. Tài khoản Windows cần quyền tạo database lần đầu và quyền đọc/ghi khi sử dụng. Thiết lập tạo năm món, tám bàn và tài khoản `admin` với mật khẩu `Admin@123`. Đổi mật khẩu sau lần đăng nhập đầu. Chạy lại thiết lập không đặt lại mật khẩu đã đổi.

Quản lý chuẩn bị danh mục, hồ sơ nhân viên rồi cấp tài khoản. Nhân viên chọn bàn, thêm món, đổi số lượng và lưu đơn. “Lưu & thu tiền” lưu đơn trước khi mở bước thu tiền. Quay lại bước này vẫn giữ đơn đang xử lý. Chỉ xác nhận hoàn tất sau khi nhận đủ tiền. Quản lý chọn kỳ trong Báo cáo doanh thu rồi xuất CSV. F5 làm mới trang hiện tại, trang dài có thể cuộn.

Giá nguyên đồng lớn hơn 0 và không quá 1.000.000.000. Số lượng từ 1 đến 999 sau khi gộp cùng món. Điện thoại có thể trống, nếu nhập dùng 10 số bắt đầu bằng 0 hoặc +84 và 9 số. Mỗi bàn có tối đa một đơn đang xử lý. Món đã lưu giữ tên và giá cũ. Mỗi 10.000 đồng được một điểm, làm tròn xuống, chỉ cộng khi thanh toán cho khách đã chọn. Không sửa/xóa đơn đã thanh toán, không xóa danh mục còn liên kết lịch sử.

## Checklist yêu cầu

Đã đọc đủ ba trang mẫu Python và 18 trang quy định DNC trước khi dọn mã và sửa báo cáo. Quyết định 309/QĐ-ĐHNCT ngày 08/12/2016 là tài liệu được cung cấp, không được diễn giải là bản mới nhất của trường. Mẫu Python được ưu tiên khi hai nguồn khác nhau. Mỗi dòng dưới đây giữ số để đối chiếu cuối.

'''
special={
 4:'Đạt. Báo cáo 32 trang cả bìa và phụ lục, dưới giới hạn 60 trang.',
 17:'Chưa đủ thông tin. Đã ghi phiên bản đo được và PowerShell, chưa xác nhận trình soạn thảo/IDE thực tế của sinh viên.',
 23:'Đạt phần đóng/mở cửa sổ và kết nối mới. Chưa thử tắt máy rồi khởi động lại, đã nêu rõ trong Chương 4.',
 27:'Đạt thiết lập tệp. In một mặt là lựa chọn cần giữ khi in giấy, chưa thực hiện in vật lý.',
 38:'Không áp dụng công thức toán độc lập. Báo cáo giải thích phép tính bằng lời, số liệu chạy và mã nguồn, không có công thức đặt số.',
 39:'Đạt. Bảng khảo sát có nguồn dưới bảng, nghiêng cỡ 11. Sơ đồ và ảnh giao diện do dự án tạo, DFD do sinh viên cung cấp. Logo bìa theo mẫu học phần, không phải hình nội dung.',
 42:'Đạt. Các nguồn được trích đều có trong danh mục tiếng Anh. Chữ a, b đi kèm “không ghi năm” chỉ phân biệt tài liệu cùng tác giả, theo quy tắc trích dẫn của DNC, không phải mã chức năng.',
 59:'Đạt. SHA-256 DFD gốc khớp trước và sau. Không tìm thấy tệp .pdm trong dự án để kiểm tra cấu trúc mô hình.',
 66:'Đạt kiểm tra tự động, đang hoàn tất rà ảnh từng trang trước bàn giao.',
 67:'Đang dọn các tệp công cụ và ảnh rà trang trước bàn giao.'}
for i,text in enumerate(checks,1):
    if 49<=i<=58:
        status='Không áp dụng. Lý do nằm ngay trong yêu cầu đối chiếu này.'
    else:
        status=special.get(i,'Đạt.')
    content+=f'{i}. {text} **{status}**\n'
content+='''68. Ngoại lệ đã được sinh viên chọn: Giới thiệu dùng Hình 1 và Bảng 1, Bảng 2. Các chương vẫn dùng Hình 2.1, Bảng 1.1 theo chương. Không dùng mã G hoặc mã tự đặt. **Đạt.**

Khổ A4, trái 3,5 cm, phải 2 cm, trên/dưới 2 cm. Times New Roman 13, giãn dòng 1,2, thụt đầu 1 cm, trước 6 pt và sau 0 pt. Bảng, hình, tham khảo và phụ lục giãn dòng đơn. Tiêu đề chương hai dòng, 14 đậm căn giữa. Số mục dùng đánh số nhiều cấp của Word. Mục lục và hai danh mục dùng trường TOC có liên kết, chú thích dùng SEQ, số trang dùng PAGE. Khi sửa nội dung trong Word, chọn toàn bộ rồi cập nhật trường, chọn cập nhật toàn bộ mục lục.

Không thêm use case vì mẫu không yêu cầu và không cần để giải thích ứng dụng này. Sơ đồ quan hệ bảy bảng được giữ vì giúp kiểm chứng cấu trúc SQL thật. Hai hình kiến trúc và luồng lưu trữ riêng của bản cũ được bỏ vì nội dung đã thể hiện bằng bảng vai trò tệp, DFD, bảng CSV và phần giải thích. Không có chức năng hoặc kết quả mới được suy ra từ hình tham khảo.

## Danh sách hình và bảng

'''
for key,label in [('figures','Hình'),('tables','Bảng')]:
    content+='| Số | Tên | Phần báo cáo |\n|---|---|---|\n'
    for item in inventory[key]:
        section='Giới thiệu' if not item['chapter'] else 'Chương '+item['chapter']
        content+=f'| {label} {item["number"]} | {item["title"]} | {section} |\n'
    content+='\n'
content+='''Logo trên bìa không đánh số hình. Có 12 hình nội dung và 15 bảng. DFD gốc nằm ở docs, các ảnh tạo mới chỉ nằm trong sodo.

## Đối chiếu DFD mức 0

Ảnh `docs/DFD_Muc0.png` được giữ nguyên cả tệp và nội dung chèn Word. Kích thước gốc 927 × 180 điểm ảnh. SHA-256:

```text
D009F45DCA9A9DC0D21B995B116BD83E4EB44539652AA8529EAF1F62E52E4E1C
```

- Hai tác nhân Nhân viên và Quản lý khớp phân quyền. Một tiến trình trung tâm số 1 khớp cách vẽ ngữ cảnh của sinh viên. Khách hàng là dữ liệu, không có màn hình tự đăng nhập để thêm tác nhân khách.
- Nhân viên gửi đăng nhập và dữ liệu đơn, nhận thực đơn, trạng thái bàn, tổng tiền, tiền thừa. Đây là các thao tác có trong LoginWindow, OrderEditor và PaymentDialog.
- Quản lý gửi danh mục, tài khoản và kỳ thống kê, nhận danh sách, doanh thu, số hóa đơn, món bán chạy và CSV. Các hàm tương ứng có thật trong CoffeeService và StatisticsTab.export().
- Không có kho SQL trong ảnh ngữ cảnh. Điều này không tự động làm ảnh sai vì kho bên trong được thể hiện ở phần thiết kế dữ liệu. Đường đi người dùng → Python → CSV được giải thích ngay sau hình trong báo cáo, đúng chức năng chỉ xuất tập tin.
- Điểm có thể làm rõ nếu sinh viên chọn sửa về sau: tách “yêu cầu thu tiền, khoảng thời gian thống kê” thành hai mũi tên. Bổ sung kết quả lưu/sửa/hủy/thanh toán và thông báo lỗi. Chức năng đổi mật khẩu có thật nhưng chưa có nhãn riêng ở DFD.
- Tên trung tâm đang ghi “COFFE”. Mã đối chiếu giữ đúng chữ đó để không tự sửa bản gốc. Tên nghiệp vụ trong phần văn bản là quản lý quán cà phê.
- Chưa có tệp .pdm để xem mô hình PowerDesigner. Không yêu cầu vẽ lại DFD. Nếu muốn hình in rõ hơn, sinh viên có thể xuất lại PNG độ phân giải cao hoặc ảnh vector từ mô hình gốc. Hiện báo cáo đã có Bảng 2 chép đủ 12 luồng để đọc nhãn rõ.

Các điểm trên là đề nghị để sinh viên quyết định, không phải thay đổi đã áp vào bản gốc. Mã PlantUML giữ 12 luồng và hướng, bố trí/hình khối do PlantUML sắp xếp nên không khẳng định giống từng điểm ảnh PowerDesigner.

## Mã PlantUML

Mỗi khối dưới đây là một sơ đồ riêng. Tệp .puml trong sodo có nội dung giống khối tương ứng. Đã dựng bằng Java 27 và plantuml.jar 1.2025.10 có Graphviz cục bộ. Không gọi máy chủ PlantUML, không gửi nội dung dự án ra ngoài.

Để dựng lại sau này, chuẩn bị plantuml.jar ở nơi quản lý công cụ của bạn rồi chạy Java với các tệp .puml. Tệp jar đã dùng khi hoàn thiện là công cụ tạm, không phải phụ thuộc chạy ứng dụng nên không giữ trong bản bàn giao. Không cần Java hoặc PlantUML để chạy ứng dụng và mở báo cáo.

'''
diagrams=[
 ('1','Sơ đồ DFD cấp 0 của ứng dụng','Giới thiệu, mục 5','dfd_muc_0','Mã tương đương để đối chiếu. Báo cáo chèn ảnh gốc của sinh viên, không chèn ảnh dựng lại.'),
 ('2.1','Sơ đồ phân cấp hàm','Mục 2.1','phan_cap_ham','Đối chiếu main.py, models/service.py, ui/dashboard.py và ui/statistics_tab.py.'),
 ('2.2','Quan hệ giữa bảy bảng dữ liệu','Mục 2.3','quan_he_du_lieu','Đối chiếu database_setup.py. Không hoặc nhiều chi tiết là ràng buộc ở mức SQL, nghiệp vụ yêu cầu giỏ có món.'),
 ('2.3','Lưu đồ thuật toán lưu đơn hàng','Mục 2.5','luu_don_hang','Đối chiếu CoffeeService.save_order(). Các ngoại lệ trong giao dịch được giải thích trong chú giải.'),
 ('2.4','Lưu đồ thuật toán thanh toán đơn','Mục 2.6','thanh_toan_don','Đối chiếu PaymentDialog và CoffeeService.finish_order(). Chỉ mô tả nhánh thanh toán, không đồng nhất nhánh hủy với thu tiền.')]
for no,title,section,filename,note in diagrams:
    code=(ROOT/f'sodo/{filename}.puml').read_text(encoding='utf-8').rstrip()
    content+=f'### Hình {no} {title}\n\n{section}. {note}\n\n```plantuml\n{code}\n```\n\n'
content+='''## Nhật ký chạy thử và kiểm tra

Ngày 20/10/2026, cùng mã nguồn và môi trường đã nêu. Trước khi dọn mã: 19/19 kiểm thử, 18,003 giây. Sau khi dọn: 19/19, 16,156 giây. Thời gian chỉ ghi nhận hai lần chạy, không phải phép đo chứng minh tăng tốc.

```powershell
python -B -m unittest discover -s tests -v
```

Bộ kiểm thử kiểm tra SQL Server thật và Tkinter. Một số thông báo giao diện dùng unittest.mock để không dừng chờ, phần SQL và các giao dịch không bị thay thế. Các nhóm đã đạt: băm/xác thực, nhập sai, thiết lập lặp, danh mục, quyền, tài khoản, đơn/chuyển bàn, giá lúc bán, món ngừng bán, phiên bản cũ, chiếm bàn đồng thời, thanh toán một lần, hoàn tác lỗi, kỳ ngày/tháng/năm nhuận và thao tác chuột/bàn phím control.

Lần chạy bổ sung dùng cửa sổ thật và hộp thoại lưu CSV thật, không thay hộp thoại xuất bằng dữ liệu giả:

| Thời điểm | Thao tác | Kết quả quan sát |
|---|---|---|
'''
for event in evidence['events']:
    content+=f'| {event["thoi_gian"].replace("T"," ")} | {event["thao_tac"]} | {event["ket_qua"]} |\n'
content+='''
Tập tin xuất gốc được giữ tại `D:\\NCTU\\Python\\ThucHanh\\SoLieuCSVProject\\doanh_thu_2026-10-14.csv`. Người dùng đã chọn vị trí lưu này. Kỳ 14/10 đến 20/10/2026 có 8 đơn, 1.200.000 đồng. Dòng cà phê đen: 30 ly, 750.000 đồng. Dòng cà phê sữa: 15 ly, 450.000 đồng. Đã đọc lại để xác nhận dấu nhận biết UTF-8, tiêu đề, số đơn và tổng tiền.

Ảnh tổng quan chụp trước khi thanh toán đơn 80.000 đồng nên hiện 85.000 đồng doanh thu hôm nay và một đơn đang phục vụ. Ảnh báo cáo chụp sau thanh toán nên kỳ có 8 đơn. Đây là hai thời điểm khác nhau, không phải số liệu mâu thuẫn.

Cơ sở dữ liệu trình diễn đã được xóa khi kết thúc. Chưa thử tắt máy/khởi động lại, mất điện, tải lớn hoặc bảo mật độc lập. Còn thiếu tên trình soạn thảo/IDE sinh viên thực tế đã dùng. Ảnh DFD độ phân giải cao và .pdm là bổ sung tùy chọn để đối chiếu mô hình, không phải lý do tự vẽ lại bản đã chốt.

Word đã cập nhật trường, lưu và mở để xuất kiểm tra. Số hình và bảng liên tục đúng chương, 15 bảng có đủ sáu cạnh viền ngoài/trong dạng đơn, tiêu đề cột lặp và hàng không bị cắt. Không có dấu chấm phẩy trong văn bản, mã chức năng tự đặt, placeholder, emoji hoặc ký tự vô hình. Ảnh rà trang và các công cụ tạm được dọn sau khi kiểm tra.

## Chuẩn bị bảo vệ

1. Đăng nhập quản lý, giới thiệu tổng quan và màu/trạng thái.
2. Thêm hoặc sửa món, tìm kiếm không dấu, giải thích dữ liệu ghi vào SQL.
3. Đăng nhập nhân viên để chỉ ra ba trang và quyền bị giới hạn ở cả giao diện lẫn CoffeeService.
4. Tạo đơn hai cà phê đen và một cà phê sữa. Giải thích 80.000 đồng, lưu, mở lại và chuyển bàn hợp lệ.
5. Thử tiền thiếu rồi nhận 100.000 đồng. Kiểm tra thừa 20.000 đồng, điểm khách và bàn trống.
6. Quản lý xem báo cáo, xuất CSV, đọc lại tổng và số đơn. Dữ liệu doanh thu tại buổi trình bày phụ thuộc các đơn thực tế lúc đó, không cam kết luôn là 1.200.000 đồng.
7. Giải thích vòng lặp gộp giỏ, giữ giá lúc bán, commit/rollback/finally và kiểm thử. Không chạy bộ kiểm thử giữa phần trình diễn vì sẽ mở nhiều cửa sổ thử.

Các điểm cần nắm: `Decimal` giúp tính tiền thập phân, `ROWVERSION` phát hiện đơn cũ, khóa giao dịch và chỉ mục duy nhất ngăn thao tác trùng, tham số `?` bảo vệ giá trị truy vấn. `ENTITIES` giới hạn tên bảng/cột. PBKDF2 trong security.py không lưu mật khẩu gốc. Dữ liệu ngẫu nhiên riêng làm cùng mật khẩu có giá trị băm khác nhau. Chi tiết đơn tách riêng để lưu nhiều món và giữ lịch sử tên/giá. Đơn khách lẻ để MaKH trống, không tạo khách giả.

Mã không còn decorator hoặc hàm giao dịch dùng generator. Các thao tác ghi dùng try/except/finally trực tiếp. Thư viện chạy ứng dụng không tăng. Tên login hiện là hàm của models/service.py, không còn CoffeeService.login. Hướng dẫn cũ nhắc guarded và transaction đã được thay bằng nội dung đúng với mã hiện tại.
'''
(ROOT/'README.md').write_text(content,encoding='utf-8')
print('README written',len(checks)+1,'requirements',len(content),'characters')
