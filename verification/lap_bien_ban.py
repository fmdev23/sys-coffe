"""Lập biên bản từ các kết quả thực tế đã lưu, không thực thi lại ứng dụng."""
import ast,json,hashlib,re,subprocess,sys
from pathlib import Path
from datetime import datetime,timedelta,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification'
sys.stdout.reconfigure(encoding='utf-8')
load=lambda path:json.loads((OUT/path).read_text(encoding='utf-8-sig'))
now=datetime.now(timezone(timedelta(hours=7))).isoformat(timespec='seconds')
run=load('unittest_moi.json');env=load('moi_truong.json');doc=load('kiem_tra_docx.json')
assert run['confirmed_success'] and run['exit_code']==0 and run['tests_run']==19
matrix=[]
def add(section,claim,path,function,test,evidence,conclusion='ĐÚNG',note=''):
    if path.endswith('.py') and (ROOT/path).exists():
        tree=ast.parse((ROOT/path).read_text(encoding='utf-8-sig'))
        names=function.replace('CoffeeService.','').replace('CoffeeApp.','').replace('PaymentDialog.','').replace('StatisticsTab.','').replace('MainWindow.','').split(', ')
        positions=[str(n.lineno) for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
        if positions:path+=':'+','.join(positions)
    if test and test!='Không có bài riêng':assert any(t['method']==test for t in run['test_statuses']),test
    matrix.append({'muc':section,'tuyen_bo':claim,'tep':path,'lop_ham':function,'test':test or 'Không có bài riêng','bang_chung':evidence,'ket_luan':conclusion,'ghi_chu':note})
case_rows=[
('Băm và xác thực mật khẩu','security.py','hash_password, verify_password','password_hash_and_login'),
('Thiết lập lặp lại không nhân đôi dữ liệu','database_setup.py','setup','setup_idempotent'),
('Kiểm tra giá, tên, điện thoại và điểm','models/service.py','price, phone, save_entity','validation'),
('Thêm, đọc, sửa, xóa danh mục','models/service.py','list_entities, save_entity, delete_entity','crud_all_entities'),
('Tài khoản, mật khẩu và phiên bị khóa','models/service.py','save_account, delete_account, change_password, _authorize','account_crud_password_and_disabled_session'),
('Bảo vệ quản lý đang sử dụng','models/service.py','save_account, delete_account','protect_current_manager'),
('Chặn thao tác quản trị của nhân viên','models/service.py','_authorize','staff_permissions_enforced_in_service'),
('Tạo, sửa, chuyển bàn và xóa đơn hợp lệ','models/service.py','save_order, delete_order','order_create_edit_move_and_delete'),
('Lỗi lưu đơn hoàn tác dữ liệu','models/service.py','save_order','order_failure_rolls_back'),
('Giữ giá và tên lúc bán, hạn chế món ngừng bán','models/service.py','save_order','snapshot_price_and_discontinued_product'),
('Thanh toán, tích điểm và giữ lịch sử','models/service.py','finish_order, delete_order','payment_points_and_preserve_history'),
('Hủy và xóa đúng trạng thái','models/service.py','finish_order, delete_order, _sync_table','cancel_and_delete'),
('Lỗi SQL khi cộng điểm hoàn tác cả đơn và bàn','models/service.py','finish_order','payment_database_failure_rolls_back_all_changes'),
('Phiên bản cũ không ghi đè hoặc thanh toán','models/service.py','save_order, finish_order','stale_order_cannot_overwrite_or_pay'),
('Hai thao tác giữ cùng bàn chỉ một thành công','models/service.py','save_order, _lock','concurrent_table_reservation'),
('Hai thao tác thanh toán không cộng điểm hai lần','models/service.py','finish_order, _lock','concurrent_payment_only_once'),
('Kỳ ngày, tháng và loại đơn hủy/chưa thanh toán','models/service.py','statistics, revenue_series, report_period','statistics_dates_month_and_excluded_statuses'),
('Control bo góc, chuột, bàn phím, trạng thái khóa','ui/theme.py','rounded_controls','rounded_controls_mouse_keyboard_and_disabled_state'),
('Tkinter đăng nhập, trang theo vai trò, biểu mẫu, gọi món','ui/main_window.py','MainWindow','tkinter_login_pages_forms_and_order_flow')]
for claim,path,fn,test in case_rows:add('1, 2, 3 và 4.2',claim,path,fn,'test_'+test,'unittest_moi.stderr.txt và unittest_moi.json')
add('2.3','Bảy bảng nghiệp vụ, không tính sysdiagrams của SSMS','database_setup.py','SCHEMA','','moi_truong.json, SCHEMA trong database_setup.py')
add('2.3','ROWVERSION là phiên bản nhị phân, không phải thời điểm','database_setup.py','SCHEMA','test_stale_order_cannot_overwrite_or_pay','moi_truong.json: PhienBan kiểu timestamp, tài liệu Microsoft rowversion','ĐÚNG','timestamp là tên đồng nghĩa SQL, không phải datetime.')
add('2.3','Chỉ mục duy nhất có điều kiện cho bàn đang có đơn','database_setup.py','SCHEMA','test_concurrent_table_reservation','moi_truong.json: UX_Ban_DonDangXuLy unique + filter')
add('3.3','Khóa sp_getapplock và giao dịch','models/service.py','_lock, save_order, finish_order','test_concurrent_payment_only_once','Mã nguồn, các test đồng thời và rollback','ĐÚNG','Khóa ứng dụng chờ tối đa 10 giây. Đây không phải thử tải nhiều máy.')
add('2.6, 4.3','Chặn tiền sai hoặc thiếu tại giao diện','ui/payment_dialog.py','change_amount, update_change, confirm','test_tkinter_login_pages_forms_and_order_flow','bo_sung_tien_do.json, phép thử tiền 80.000 nhận 100.000','ĐÚNG','Dịch vụ không nhận tiền khách đưa. Kiểm tra UI riêng không phải ràng buộc SQL.')
add('2.6','expected_version tùy chọn ở dịch vụ, được GUI thanh toán truyền','models/service.py','finish_order','test_stale_order_cannot_overwrite_or_pay','Mã nguồn + ui/payment_dialog.py:confirm')
add('2.4, 4.3','TOP 10 và tổng toàn kỳ có thể khác tổng dòng sản phẩm','models/service.py','statistics','','bo_sung_tien_do.json, doanh_thu_kiem_dinh_moi.csv','ĐÚNG','13 món, 12 đơn, tổng 245.000, 10 dòng 212.000 đồng. Ngoài 19 phương thức.')
add('2.4, 4.3','CSV UTF-8 có BOM và ghi đúng dữ liệu SQL','ui/statistics_tab.py','export','','csv_lich_su.json và doanh_thu_kiem_dinh_moi.csv','ĐÚNG','Kịch bản mới chỉ thay hàm chọn đường dẫn, không thay SQL, writer hoặc dữ liệu. Chưa chứng minh chọn tệp bằng chuột.')
add('2.4','Tên thống kê từ danh mục hiện tại, tên hóa đơn từ lúc bán','models/service.py','statistics, save_order','test_snapshot_price_and_discontinued_product','Mã truy vấn statistics và phép thử snapshot','ĐÚNG','Test lịch sử giá không kiểm tra mọi tình huống đổi tên trên báo cáo thống kê.')
add('3.1','VS Code 1.140.0 x64, Python 3.14.3, pyodbc 5.3.0, SQL 16.0.1210.3','verification/moi_truong.json','Lệnh phiên bản và truy vấn chỉ đọc','','moi_truong.json, vscode_version.stdout.txt, pyodbc_pip.stdout.txt')
add('4.2','19 đạt, không lỗi hoặc bỏ qua, mã thoát 0','tests/test_coffee.py','CoffeeTests','','unittest_moi.json, unittest_moi.stderr.txt')
add('4.3','CSV lịch sử 14–20/10, 8 đơn, 1.200.000 đồng','docs/doanh_thu_kiem_tra.csv','Không áp dụng','','csv_lich_su.json và .report_work/evidence_new.json','ĐÚNG','Chỉ xác nhận nhất quán của tập tin và nhật ký lưu, không xác nhận SQL lịch sử còn tồn tại.')
add('4.3','Tái truy vấn database trình diễn ngày 20/10/2026','verification/moi_truong.json','Không áp dụng','','historical_demo_database_present=false','THIẾU CHỨNG CỨ','Database cũ không còn. Đã giới hạn khẳng định trong báo cáo.')
add('4.4','Tắt máy, mất điện, tải lớn, nhiều máy hoặc kiểm định bảo mật độc lập','tests/test_coffee.py','CoffeeTests','','Không có phép thử các tình huống này','THIẾU CHỨNG CỨ','Không kết luận đạt, ghi giới hạn tại mục 4.4 và hướng phát triển.')
add('4.4','Ảnh giao diện mới và chọn đường dẫn CSV bằng chuột trong lần mới','verification/bo_sung_lan_dau_chua_hoan_tat.json','Không áp dụng','','Hai nhật ký chưa hoàn tất và thông báo Sky cửa sổ đã đóng','THIẾU CHỨNG CỨ','Giữ ảnh cũ, không tạo hoặc tráo ảnh. Kết quả UI tự động trong 19 test vẫn có.')
add('Giới thiệu','DFD giữ nguyên hai tác nhân và 12 luồng','sodo/dfd_muc_0.puml','Không áp dụng','','docs/DFD_Muc0.png, sodo/dfd_muc_0.puml, bảng 2 và đối chiếu mã','ĐÚNG','Ảnh gốc độ phân giải thấp, giải thích nhãn bằng Bảng 2, không sửa hình.')
add('Tài liệu cũ','CoffeeService.login, guarded, transaction/contextmanager còn được một số MD mô tả','docs/BAO_VE.md','Không còn các thành phần này','','Đối chiếu AST 21 tệp và docs/BAO_VE.md, docs/DanhMuc_SoDo.md','SAI','Tài liệu cũ được bảo toàn theo phạm vi kiểm định. FINAL dùng login tự do và try/except/finally thật.')
add('Kết luận','Kho nguyên liệu, in hóa đơn, nhập CSV, thanh toán ngân hàng đã có','models/service.py','Không áp dụng','','Không có chức năng này trong mã','KHÔNG ÁP DỤNG','Chỉ nêu hướng phát triển, không ghi là chức năng hoàn thành.')
(OUT/'ma_tran_doi_chieu.json').write_text(json.dumps({'checked_at':now,'rows':matrix},ensure_ascii=False,indent=2),encoding='utf-8')

findings=[
('Báo cáo','Thiếu IDE được xác nhận','Thêm VS Code và kết quả code --version','ĐÃ XỬ LÝ'),
('Báo cáo','Thời gian cũ 18,003/16,156 giây thiếu log tương ứng','Thay bằng lần mới 19,656 giây, exit 0. Log lịch sử thật ghi 19,801 giây','ĐÃ XỬ LÝ'),
('Báo cáo','Chưa nêu rõ người/công cụ thực thi','Ghi Codex thực thi tự động, mô tả phạm vi mock thông báo','ĐÃ XỬ LÝ'),
('Báo cáo','Dễ gộp số liệu cũ, ảnh cũ với lần mới','Ghi riêng ngày 20/10 và 22/10, chú thích bảng lịch sử','ĐÃ XỬ LÝ'),
('Báo cáo','CSV chưa giải thích giới hạn TOP 10','Thêm giới hạn và kịch bản SQL/CSV thật 13 món','ĐÃ XỬ LÝ'),
('Báo cáo','Kiểm tra tiền dễ bị hiểu là ràng buộc dịch vụ','Giải thích kiểm tra tại PaymentDialog, không lưu tiền nhận/thừa','ĐÃ XỬ LÝ'),
('Báo cáo','Chưa nhấn mạnh expected_version là tùy chọn','Mô tả đúng chữ ký dịch vụ và lời gọi GUI','ĐÃ XỬ LÝ'),
('Trình bày','Đoạn ngắn tràn sang trang riêng sau khi biên tập','Rút gọn nội dung lặp, mục lục đơn dòng, giữ ảnh/bảng/khổ lề','ĐÃ XỬ LÝ'),
('Tham khảo','Nguồn cần được truy cập lại cho lần kiểm định mới','Kiểm tra nguồn chính, cập nhật ngày 22/10 và liên kết Python 3.14','ĐÃ XỬ LÝ'),
('Môi trường','Lệnh python mặc định trỏ WindowsApps không khởi động','Dùng bản Python đã cài, thêm PATH chỉ cho tiến trình con','ĐÃ XỬ LÝ'),
('Công cụ kiểm định','pyodbc không đọc trực tiếp datetimeoffset kiểu -155','Chuyển kiểu sang NVARCHAR trong truy vấn chỉ đọc, không sửa ứng dụng','ĐÃ XỬ LÝ'),
('Tài liệu cũ','Một số MD mô tả API và số hình cũ','Giữ nguyên, đánh dấu SAI và dùng ma trận mới làm căn cứ','CÒN GIỚI HẠN'),
('Bằng chứng lịch sử','Database ngày 20/10 không còn','CSV và nhật ký khớp, không thể tái xác nhận SQL lịch sử','CÒN GIỚI HẠN'),
('Phạm vi thử nghiệm','Chưa tắt máy, mất điện, thử tải hoặc đánh giá bảo mật độc lập','Báo cáo nêu rõ chưa thực hiện, không kết luận đạt','CÒN GIỚI HẠN'),
('Bằng chứng giao diện','Hai lần mở UI bổ sung đóng trước khi lấy được ảnh xác nhận','Lưu cả hai nhật ký, hoàn tất bổ sung bằng API/Tkinter và cấp đường dẫn tự động','CÒN GIỚI HẠN')]
(OUT/'phat_hien.json').write_text(json.dumps({'total':15,'resolved':11,'limitations':4,'application_bugs_demonstrated':0,'items':[{'category':a,'finding':b,'action':c,'status':d} for a,b,c,d in findings]},ensure_ascii=False,indent=2),encoding='utf-8')

checklist=json.loads((ROOT/'.report_work/checklist.json').read_text(encoding='utf-8'))
checks=[]
for i,line in enumerate(checklist,1):
    status='ĐẠT';note='Đối chiếu nội dung Word, kiểm tra cấu trúc và xem ảnh trang.'
    if line.startswith('Không áp dụng'):
        status='KHÔNG ÁP DỤNG';note=line
    if 'sau khi đóng và mở lại' in line:
        status='ĐẠT TRONG PHẠM VI';note='Có chứng cứ kết nối mới và đọc dữ liệu đã commit. Tắt máy chưa thực hiện, không đánh dấu đạt tình huống đó.'
    if 'công thức trình bày' in line:
        status='KHÔNG ÁP DỤNG';note='Không có công thức toán độc lập cần đánh số. Phép tính tiền là ví dụ số, thuật toán nằm trong mã.'
    if 'một README.md duy nhất' in line or 'không còn bytecode' in line or 'một thư mục hình sơ đồ' in line:
        status='KHÔNG ÁP DỤNG';note='Yêu cầu kiểm định mới ưu tiên bảo toàn tài liệu và chứng cứ cũ, đồng thời bắt buộc tạo verification/BAO_CAO_KIEM_DINH_CUOI.md. Không dọn hoặc xóa tài liệu cũ.'
    if 'chạy thật' in line.lower():note='unittest_moi.json và bo_sung_tien_do.json. Không xem hai lần UI chưa hoàn tất là đạt.'
    if 'theo chương' in line:
        note='Giữ ngoại lệ do người dùng chấp thuận: Giới thiệu dùng Hình 1, Bảng 1, Bảng 2. Chương dùng số x.y, kiểm tra liên tục.'
    if 'Python đơn giản' in line:note='Không sửa mã ứng dụng, không thêm thư viện. AST 21 tệp và bộ 19 test đã được kiểm tra.'
    checks.append({'number':i,'requirement':line,'status':status,'evidence_or_reason':note})
(OUT/'checklist_cuoi.json').write_text(json.dumps({'checked_at':now,'basis':'Đọc lại đủ 3 trang mẫu Python và 18 trang DNC. Danh sách cũ được dùng làm mục lục, từng mục được đối chiếu lại.','items':checks},ensure_ascii=False,indent=2),encoding='utf-8')

sources=[
('abdelbend','db.py','https://github.com/abdelbend/Restaurant-Management-System/blob/main/db.py'),
('abdelbend','Restaurant Management System','https://github.com/abdelbend/Restaurant-Management-System'),
('Microsoft','rowversion (Transact-SQL)','https://learn.microsoft.com/en-us/sql/t-sql/data-types/rowversion-transact-sql?view=sql-server-ver16'),
('mkleehammer và cộng sự','Database Transaction Management','https://github.com/mkleehammer/pyodbc/wiki/Database-Transaction-Management'),
('mkleehammer và cộng sự','pyodbc','https://github.com/mkleehammer/pyodbc'),
*[("Python Software Foundation",name,'https://docs.python.org/3.14/library/'+module+'.html') for module,name in [('csv','CSV File Reading and Writing'),('decimal','Decimal fixed-point and floating-point arithmetic'),('hashlib','Secure hashes and message digests'),('tkinter','Python interface to Tcl/Tk'),('unittest','Unit testing framework')]]]
(OUT/'nguon_tham_khao.json').write_text(json.dumps({'access_date':'2026-10-22','method':'Mở nguồn chính bằng web.run trong phiên kiểm định, không gửi mã nguồn dự án. Không tự gán năm xuất bản.','sources':[{'author':a,'title':b,'url':c,'accessible':True} for a,b,c in sources]},ensure_ascii=False,indent=2),encoding='utf-8')

visual=load('xem_trang.json')
assert visual['all_final_pages_reviewed'] and len(visual['pages'])==doc['pages']
cleanup=load('cleanup_cuoi.json')
assert cleanup['all_owned_test_databases_absent']
acceptance={
'A':('ĐẠT','Các tuyên bố trọng yếu có mã, phương thức thử hoặc chứng cứ cụ thể trong ma trận. Các nội dung thiếu chứng cứ được nêu là giới hạn.'),
'B':('ĐẠT','19 phương thức chạy mới đạt, failure=0, error=0, skipped=0, mã thoát 0. Không sửa ứng dụng hoặc dùng SQL giả.'),
'C':('ĐẠT','CSV lịch sử 8 đơn/1.200.000 và CSV mới 12 đơn/245.000 được tách biệt. Hai lần UI chưa hoàn tất không tính đạt.'),
'D':('ĐẠT','Word mở lại được, 15 bảng, 13 ảnh nguyên vẹn, 34 trang đã render và xem, 60 tham chiếu trang khớp bookmark.'),
'E':('ĐẠT','Bản báo cáo đã bỏ khẳng định vượt chứng cứ. Các tài liệu MD cũ mâu thuẫn được đánh dấu, không dùng bác bỏ mã mới.')}
git=subprocess.run(['git','status','--short','--branch'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
(OUT/'git_cuoi.txt').write_text(git.stdout+git.stderr,encoding='utf-8')
lines=['# Biên bản kiểm định cuối dự án sys-coffe','',f'Thời điểm chốt: {now}. Múi giờ UTC+7.',
'','Kết luận: SẴN SÀNG NỘP trong phạm vi các điều kiện A–E bên dưới. Không cam kết điểm số, không coi các giới hạn chưa thử là kết quả đạt.',
'','## Phạm vi và bảo toàn',
'','Nhánh main, commit 7af74062bae32226ce0f14c11df0c60af213eab0. Repository https://github.com/fmdev23/sys-coffe. Không push, reset, commit hoặc sửa mã ứng dụng. Đã đọc 21 tệp Python, cấu trúc SQL, 19 phương thức test, README, bốn tài liệu MD được chỉ định, cả hai PDF và toàn bộ Word đầu vào.',
'','Lệnh Git được thực hiện đầu tiên trước khi tạo thư mục kiểm định. Ban đầu chỉ có tệp chưa theo dõi docs/BaoCao_QuanLyQuanCaPhe_DoiChieu_GitHub.docx. git_ban_dau.json được ghi sau khi tạo verification nên có thêm thư mục này. Không sửa tệp chưa theo dõi của người dùng.',
'',f'Đối chiếu SHA-256 xác nhận {doc["input_files_checked"]} tệp đầu vào vẫn nguyên vẹn, gồm báo cáo gốc, ảnh DFD, ảnh giao diện, các tài liệu và .report_work. Dữ liệu gốc được đọc, chỉ các database kiểm thử riêng được ghi và dọn.',
'','## Môi trường thực tế',
'','| Thành phần | Kết quả |','|---|---|',
f'| Python | {env["python"]} |',f'| pyodbc | {env["pyodbc"]} |',f'| Tcl/Tk | {env["tk"]} |',
f'| SQL Server | {env["sql"]["version"]}, {env["sql"]["edition"]} |',
'| ODBC | ODBC Driver 17 for SQL Server có sẵn và được connect() chọn |',
'| IDE | VS Code 1.140.0, x64, người dùng xác nhận và code --version trả về |',
'| Hệ điều hành | Windows 11, build 26300 |',
'| Xác thực SQL | Windows Authentication, không dùng mật khẩu SQL trong nhật ký |',
'','SQL trả thời điểm máy chủ theo UTC. Nhật ký kiểm định ghi rõ UTC+7, không gán múi giờ máy chủ thành giờ địa phương.',
'','## Lệnh và kết quả chạy mới','',
'```text','python --version','python -m pip show pyodbc','python -m tkinter','code --version','python -B -m unittest discover -s tests -v','```',
'','Python mặc định qua WindowsApps không khởi động. Công cụ kiểm định dùng Python đã cài tại C:/Users/PC/AppData/Local/Python/pythoncore-3.14-64/python.exe và chỉ thêm thư mục này vào PATH của tiến trình con. Không đổi PATH hệ thống. Truy vấn ngày giờ ban đầu gặp kiểu datetimeoffset không được pyodbc đọc trực tiếp. Công cụ được sửa để CONVERT sang NVARCHAR trong truy vấn chỉ đọc.',
'',f'Bắt đầu {run["started_at"]}, kết thúc {run["finished_at"]}. unittest {run["duration_unittest_seconds"]} giây, tiến trình {run["duration_wall_seconds"]} giây. 19 đạt, 0 thất bại, 0 lỗi, 0 bỏ qua, mã thoát {run["exit_code"]}. stdout đầy đủ ở unittest_moi.stdout.txt (rỗng), stderr đầy đủ ở unittest_moi.stderr.txt. unittest mặc định ghi kết quả lên stderr, đây không phải dấu hiệu test lỗi.',
'',f'Database được quan sát: {run["database_created_observed"][0]}. Trước và sau không có database thử. Bộ test cấp tên bằng uuid4, đăng ký addModuleCleanup trước setup. cleanup kiểm tra mẫu tên và so với database gốc rồi chỉ ALTER/DROP đúng tên do lần chạy cấp. Truy vấn đọc cuối xác nhận mọi database do các lần kiểm định này tạo đều không còn.',
'','Kiểm tra cú pháp AST cho đủ 21 tệp, không tạo bytecode. Một số hộp thông báo Tkinter được thay trong bộ unittest. SQL Server, kết nối, ràng buộc và giao dịch đều thật.',
'','### Kịch bản bổ sung','',
'Ngày 22/10, tổng 80.000, nhận 100.000, thừa 20.000, khách cộng 8 điểm và bàn Trống được kiểm tra lại bằng PaymentDialog và SQL thật. Dữ liệu 13 món/12 đơn xác nhận TOP 10: tổng toàn kỳ 245.000, tổng 10 dòng 212.000 đồng. CSV mới có BOM UTF-8. Chỉ filedialog.asksaveasfilename được cung cấp đường dẫn tự động, không thay truy vấn hoặc hàm ghi CSV. Không coi đây là kiểm tra chọn tệp bằng chuột.',
'','Hai lần mở UI trước đó đóng trước khi lấy được ảnh xác nhận. Nhật ký bo_sung_lan_dau_chua_hoan_tat.json và bo_sung_lan_hai_chua_hoan_tat.json được giữ riêng, không tính đạt. bo_sung_tien_do.json là lần hoàn tất sau đó, mã thoát lưu ở bo_sung_exit_code.txt. Thời gian bổ sung không cộng vào thời gian unittest.',
'','### Chứng cứ lịch sử','',
'CSV tại docs và thư mục SoLieuCSVProject giống SHA-256, kỳ 14–20/10/2026, 8 đơn, 1.200.000 đồng. Cà phê đen 30 ly/750.000, cà phê sữa 15 ly/450.000. evidence_new.json lưu sự kiện ngày 20/10. Database lịch sử không còn nên chỉ xác nhận tính nhất quán tập tin và nhật ký. evidence.json là lần khác ngày 04/10, không dùng ghép với kỳ 14–20/10. tests.txt cũ có 19 test OK trong 19,801 giây nhưng không tự chứng minh thời điểm hay commit. Không dùng các thời gian 18,003/16,156 giây thiếu log tương ứng trong FINAL.',
'','## Ma trận báo cáo và mã nguồn','',
'| Mục | Tuyên bố | Tệp và class/hàm | Test | Bằng chứng | Kết luận |',
'|---|---|---|---|---|---|']
for r in matrix:lines.append('| '+' | '.join(str(x).replace('|','/').replace('\n',' ') for x in [r['muc'],r['tuyen_bo'],r['tep']+' / '+r['lop_ham'],r['test'],r['bang_chung'],r['ket_luan']+('. '+r['ghi_chu'] if r['ghi_chu'] else '')])+' |')
lines+=['','## Phát hiện và xử lý','','15 điểm rà soát: 11 đã xử lý, 4 giới hạn còn mở. Không phát hiện lỗi ứng dụng có thể chứng minh trong phạm vi chạy. Không sửa mã ứng dụng, không đổi test để ép đạt. Đây không phải khẳng định ứng dụng không có lỗi.','','| Loại | Phát hiện | Xử lý hoặc giới hạn | Trạng thái |','|---|---|---|---|']
for item in findings:lines.append('| '+' | '.join(item)+' |')
lines+=['','## Đối chiếu sơ đồ','','DFD gốc giữ nguyên byte, không tráo hình. Hai tác nhân và 12 luồng khớp phạm vi chính. Chưa tách luồng đổi mật khẩu, các thao tác phục vụ mà quản lý kế thừa và bước ghi CSV thành luồng riêng. Đây là phần diễn giải chưa chi tiết của sơ đồ ngữ cảnh, không xác nhận có luồng nghiệp vụ khác với mã. Bảng 2 chép nhãn để khắc phục chữ nhỏ. SQL là nơi lưu chính, CSV là đầu ra của quản lý. Các chi tiết kho dữ liệu đặt ở thiết kế quan hệ, không tự thêm vào DFD gốc.',
'','Bốn sơ đồ thiết kế được đối chiếu với hàm, điều kiện và bảy bảng thật. ERD thể hiện đúng tài khoản bắt buộc có nhân viên, nhân viên có tối đa một tài khoản, khách của đơn có thể trống. SQL khóa ngoại cho phép đơn chưa có dòng chi tiết, nhưng save_order() bắt buộc giỏ không rỗng. Lưu đồ thanh toán phân biệt kiểm tra tiền tại UI và giao dịch cập nhật dữ liệu.',
'','Không render lại hoặc chỉnh ảnh sơ đồ trong vòng này. Mã tương đương nằm trong sodo/*.puml và README.md. docs/DanhMuc_SoDo.md, docs/SoDo_PlantUML.md còn số hình/API cũ, chỉ dùng như lịch sử. Nếu giảng viên yêu cầu thể hiện riêng bước ghi CSV hoặc thay DFD, cần sinh viên quyết định và cung cấp bản vẽ mới. Không tự sửa bản gốc.',
'','## Checklist yêu cầu và trình bày','','Mẫu Python ưu tiên cấu trúc, DNC áp dụng phần trình bày phù hợp. Các ngoại lệ của tài liệu luận văn đã được giải thích trong README có sẵn, được giữ nguyên. Danh sách dưới ghi lại kết quả đối chiếu mới.','','| Số | Yêu cầu | Kết luận | Căn cứ hoặc lý do |','|---:|---|---|---|']
for r in checks:lines.append(f'| {r["number"]} | {r["requirement"]} | {r["status"]} | {r["evidence_or_reason"]} |')
lines+=['','## Kiểm định Word và trực quan','','Tạo bản sao từ đúng DOCX đầu vào, chỉ sửa phần cần thiết trong OOXML. Giữ 15 bảng, 13 ảnh, bố cục bìa, các section và mã trích. So sánh SHA ảnh và kích thước inline cho thấy không thay đổi. Không tạo báo cáo mới từ tài liệu trắng.',
'','Microsoft Word 16.0 cập nhật trường nhiều lượt, lưu và xuất PDF. render_docx.py của bộ công cụ tài liệu dùng PDF Word để tạo ảnh trang. Đã mở và xem đủ 34 trang. Số trang trước nội dung i–iv, nội dung 1–29. Kiểm tra 127 hàng bảng xác nhận từng hàng không bị tách qua hai trang. 60 PAGEREF khớp trang thực của bookmark, không liên kết nội bộ bị đứt. Có 12 chú thích hình và 15 chú thích bảng, số liên tục trong từng chương và ngoại lệ Giới thiệu đã được chấp thuận.',
'','Khổ A4, lề trái 3,5 cm, phải/trên/dưới 2 cm, đầu/chân trang 1 cm. Nội dung Times New Roman 13, giãn 1,2, thụt 1 cm, trước 6 pt, sau 0. Bảng đầy đủ viền đơn, tiêu đề lặp, không tách hàng. Hình inline đúng tỷ lệ, chú thích dưới hình. Mục lục cấp 1–2 tự động, danh mục tự động. Đã kiểm tra không chấm phẩy, placeholder TODO, mã G.1/CN1 hoặc ký tự vô hình bất thường.',
'','Hai hàm trích phone và finish_order có AST tương đương nguồn sau khi bỏ khác biệt khoảng trắng trong chuỗi SQL. Đây chỉ là thụt lề trình bày SQL, không thay câu lệnh hoặc logic. Không kết luận toàn bộ mã trình bày trong Word là bài kiểm thử độc lập.',
'','## Hồ sơ bàn giao và tệp có thể dọn sau','','Báo cáo nộp: docs/BaoCao_QuanLyQuanCaPhe_FINAL.docx. Nhật ký, ma trận, kết quả cấu trúc và SHA-256 đặt trong verification. manifest.json không tự băm chính nó để tránh tự tham chiếu. Các script kiểm định không là thư viện mới của ứng dụng, không sửa requirements.txt.',
'','Không xóa .report_work, tài liệu cũ, PNG QA cũ trong sodo hoặc báo cáo đối chiếu GitHub của người dùng. Chúng có thể được xem xét dọn sau khi người dùng giữ đủ chứng cứ. Các ảnh QA của vòng này nằm riêng tại verification/trang_bao_cao. Bằng chứng và tệp bàn giao đều đặt trong thư mục dự án ở ổ D, không đưa nhật ký lên GitHub.',
'','## Điều kiện nghiệm thu','','| Điều kiện | Kết luận | Căn cứ |','|---|---|---|']
for key,(status,note) in acceptance.items():lines.append(f'| {key} | {status} | {note} |')
lines+=['','Không còn BLOCKER theo A–E. Bốn giới hạn đã công khai ở trên vẫn cần giữ trong báo cáo. Nếu cần mở rộng chứng cứ, thực hiện tắt/khởi động lại máy sau khi lưu công việc, kiểm tra giao diện và chọn đường dẫn bằng chuột trên database riêng, hoặc cung cấp bản sao database lịch sử. Không cần bổ sung thông tin sinh viên hoặc IDE.']
(OUT/'BAO_CAO_KIEM_DINH_CUOI.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(OUT/'nghiem_thu.json').write_text(json.dumps({'time':now,'acceptance':acceptance,'conclusion':'SẴN SÀNG NỘP','application_bugs_demonstrated':0,'review_findings':15,'resolved':11,'open_limitations':4,'blockers':[]},ensure_ascii=False,indent=2),encoding='utf-8')
print('Đã lập',len(matrix),'dòng ma trận,',len(checks),'mục checklist và biên bản.')
