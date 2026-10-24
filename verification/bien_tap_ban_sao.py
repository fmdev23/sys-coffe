"""Biên tập bản sao OOXML, giữ nguyên ảnh và các phần không cần sửa."""
import sys, json, re, hashlib
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from copy import deepcopy
from lxml import etree as E
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification'
SOURCE=ROOT/'docs/BaoCao_QuanLyQuanCaPhe.docx'
TARGET=ROOT/'docs/BaoCao_QuanLyQuanCaPhe_DRAFT.docx'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W}
q=lambda name:'{'+W+'}'+name
with ZipFile(SOURCE) as z:
    infos=z.infolist()
    data={i.filename:z.read(i.filename) for i in infos}
root=E.fromstring(data['word/document.xml'])
body=root.find(q('body'))
paragraphs=body.findall(q('p'))
tables=body.findall(q('tbl'))
changes=[]
def text(node):return ''.join(node.xpath('.//w:t/text()',namespaces=NS))
def settext(p,value):
    assert not p.xpath('.//w:drawing|.//w:instrText',namespaces=NS)
    old=text(p)
    for child in list(p):
        if child.tag not in [q('pPr'),q('bookmarkStart'),q('bookmarkEnd')]:p.remove(child)
    run=E.SubElement(p,q('r'))
    for i,line in enumerate(value.split('\n')):
        if i:E.SubElement(run,q('br'))
        t=E.SubElement(run,q('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=line
    changes.append({'old':old,'new':value})
def replace(index,value):settext(paragraphs[index],value)
def caption(index,title):
    p=paragraphs[index]
    ended=False
    for child in list(p):
        if ended and child.tag==q('r'):p.remove(child)
        if child.xpath('./w:fldChar[@w:fldCharType="end"]',namespaces=NS):ended=True
    r=E.SubElement(p,q('r'));t=E.SubElement(r,q('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=' '+title
def insert_after(index,values):
    anchor=paragraphs[index]
    for value in values:
        p=E.Element(q('p'));settext(p,value);anchor.addnext(p);anchor=p

updates={
96:'Sáu nguồn được lựa chọn ở Bảng 1 bao quát ứng dụng tham khảo, giao diện, kết nối dữ liệu và xử lý tập tin.',
100:'Ứng dụng Restaurant Management System của abdelbend được chọn để phân tích logic. Phần giới thiệu cung cấp chế độ dòng lệnh và giao diện Tkinter. Tệp db.py dùng SQLite, tổ chức dữ liệu thực đơn và món được khách gọi theo mã đơn. Cách tách thao tác dữ liệu khỏi giao diện giúp nhận diện các bước nhận món, lưu đơn và lập hóa đơn. Dự án hiện tại vận dụng cách tổ chức này, đồng thời dùng SQL Server và bổ sung nghiệp vụ bàn, tài khoản và tích điểm theo yêu cầu riêng (abdelbend, không ghi năm a, b).',
114:'Các luồng vào và ra của Hình 1 được chép lại trong Bảng 2 để đọc rõ nhãn của bản gốc.',
117:'Đối chiếu mã nguồn cho thấy hai tác nhân Nhân viên và Quản lý phù hợp với hai vai trò đang sử dụng. Khách hàng không đăng nhập nên không được đặt thành tác nhân sử dụng phần mềm. Hình gốc chưa tách riêng luồng đổi mật khẩu và xuất CSV khỏi nhóm yêu cầu quản trị. CSV đã có trong luồng trả kết quả cho Quản lý, nhưng chưa thể hiện rõ bước ghi tập tin được mẫu học phần đề cập. Báo cáo giữ nguyên hình của sinh viên, giải thích phần này bằng nội dung và mã PlantUML trong README.md. Kho SQL Server được mô tả tại Chương 2, không đưa vào sơ đồ ngữ cảnh.',
120:'Các thao tác phục vụ, quản trị và thống kê được đối chiếu theo dữ liệu đầu vào và kết quả trong Bảng 1.1.',
124:'Bảng 1.2 xác định những dữ liệu phải kiểm tra trước khi ghi đơn và danh mục.',
128:'Hai vai trò có quyền thao tác như Bảng 1.3. Phần xử lý tiếp tục kiểm tra quyền sau khi giao diện được mở.',
137:'Các hàm được nhóm theo phiên làm việc, danh mục, đơn hàng và báo cáo trong Hình 2.1.',
141:'Bảng 2.1 xác định tệp chịu trách nhiệm cho từng phần xử lý để truy ngược từ giao diện đến dữ liệu.',
146:'Hình 2.2 thể hiện khóa chính, khóa ngoại và quan hệ giữa bảy bảng nghiệp vụ.',
150:'Tên trường và kiểu dữ liệu thực tế của các bảng được liệt kê trong Bảng 2.2.',
155:'Bảng 2.3 liên hệ danh sách, từ điển và kiểu số với nơi sử dụng trong chương trình.',
158:'Tập tin xuất có phần thông tin kỳ báo cáo và phần sản phẩm như Bảng 2.4.',
160:'CSV được ghi bằng utf-8-sig nên có dấu nhận biết UTF-8 ở đầu tập tin. Dòng tổng doanh thu và số đơn tính trên toàn bộ đơn đã thanh toán trong kỳ. Phần sản phẩm lấy tối đa 10 món từ statistics(), sắp theo số lượng giảm dần rồi doanh thu. Vì vậy, khi có hơn 10 món được bán, tổng các dòng chi tiết có thể nhỏ hơn tổng doanh thu. Đây là tập tin báo cáo món bán chạy, chưa phải bản xuất chi tiết mọi món. Tên món trong phần thống kê lấy từ danh mục hiện tại, còn chi tiết đơn giữ tên và giá lúc bán.',
163:'Trình tự kiểm tra giỏ, giữ giá bán và ghi dữ liệu của save_order() được thể hiện trong Hình 2.3.',
168:'PaymentDialog.change_amount() kiểm tra chuỗi tiền khách đưa và tính tiền thừa. update_change() khóa nút khi tiền không hợp lệ hoặc còn thiếu. confirm() kiểm tra lại trước khi gọi finish_order(). Hàm xử lý đơn không nhận số tiền khách đưa và không lưu tiền nhận, tiền thừa vào SQL. Kiểm tra đủ tiền thuộc lớp giao diện, chưa phải ràng buộc áp dụng cho mọi lời gọi trực tiếp đến dịch vụ.',
169:'Hình 2.4 nối bước xác nhận thu tiền tại giao diện với giao dịch cập nhật đơn, điểm và bàn.',
172:'Khi hủy, finish_order(pay=False) chỉ nhận đơn đang xử lý, ghi trạng thái Đã hủy và đồng bộ bàn. Đơn hủy không có thời điểm thanh toán và không cộng điểm. Tham số expected_version là tùy chọn tại hàm dịch vụ. Giao diện thanh toán truyền phiên bản đã đọc để phát hiện đơn bị sửa trước khi thu tiền.',
175:'Các phiên bản và cấu hình ở Bảng 3.1 được đọc lại trên máy kiểm định ngày 22/10/2026.',
177:'IDE sử dụng là Visual Studio Code (VS Code), do sinh viên xác nhận. Lệnh code --version trả về 1.140.0, kiến trúc x64. Python, pyodbc và Tcl/Tk được kiểm tra trực tiếp, phiên bản SQL Server được đọc bằng truy vấn chỉ đọc. Lệnh chạy và nhật ký nằm trong thư mục verification. Commit được đối chiếu là 7af74062bae32226ce0f14c11df0c60af213eab0 trên nhánh main.',
180:'Bảng 3.2 đối chiếu bốn nội dung đầu của học phần với các phần mã đang sử dụng.',
184:'Các nội dung về chuỗi, danh sách, tập tin và Tkinter được đối chiếu tiếp trong Bảng 3.3.',
195:'Hình 3.1 là ảnh giao diện đăng nhập đã lưu trong dự án, được giữ nguyên trong vòng kiểm định này.',
199:'Ảnh Hình 3.2 thuộc bộ chứng cứ trình diễn đã lưu trước vòng kiểm định ngày 22/10/2026. Màn hình quản lý có tám trang. Các chỉ số phụ thuộc dữ liệu và khoảng ngày tại thời điểm chụp, không được dùng làm số liệu vận hành của quán.',
200:'Hình 3.2 cho thấy cách bố trí chỉ số và các lối vào thao tác của quản lý.',
204:'Hình 3.3 cho thấy danh sách thực đơn, ô tìm kiếm và các thao tác quản lý món.',
208:'Trong kịch bản lịch sử ngày 20/10/2026, hai cà phê đen giá 25.000 đồng và một cà phê sữa giá 30.000 đồng tạo tổng 80.000 đồng. Ảnh gọi món Hình 3.4 được giữ nguyên từ bộ chứng cứ đã lưu. Phép tính này cũng được kiểm tra lại bằng dữ liệu cách ly ngày 22/10/2026, ghi riêng trong Chương 4.',
209:'Giỏ hàng trong Hình 3.4 hiển thị số lượng, đơn giá và tổng cần thu.',
213:'Hình 3.5 lưu lại trạng thái giao diện thu tiền của kịch bản lịch sử, không phải ảnh chụp mới.',
217:'Ảnh thống kê và CSV lịch sử dùng kỳ 14/10/2026 đến 20/10/2026, có 8 đơn đã thanh toán với doanh thu 1.200.000 đồng. Đây là dữ liệu chuẩn bị cho lần trình diễn ngày 20/10/2026. Lần kiểm định ngày 22/10/2026 đọc lại CSV và nhật ký đã lưu, không tái tạo hoặc thay thế ảnh Hình 3.6.',
218:'Hình 3.6 thể hiện bộ lọc kỳ, doanh thu, số đơn và danh sách món bán chạy của dữ liệu lịch sử.',
222:'Hình 3.7 lưu giao diện ba trang phục vụ của nhân viên. Quyền tương ứng được kiểm tra lại trong bộ kiểm thử mới.',
227:'Kiểm thử đối chiếu các yêu cầu nhập liệu, tính toán, phân quyền và lưu trữ với hành vi thực tế. Bộ tests/test_coffee.py dùng unittest, SQL Server thật và Tkinter. Tự động hóa bởi AI Agent Codex được dùng để thực thi và lưu kết quả, không được xem là bằng chứng sinh viên trực tiếp thao tác từng trường hợp. Phương pháp gồm kiểm thử tích hợp trên dữ liệu hợp lệ, dữ liệu sai, ràng buộc, lỗi giao dịch và hai thao tác đồng thời.',
228:'Bộ kiểm thử có 19 phương thức, trong đó một phương thức có thể kiểm tra nhiều bộ dữ liệu. Một số phép thử thay hộp thông báo bằng unittest.mock để không chờ xác nhận. Kết nối, truy vấn, giao dịch và ràng buộc đều chạy trên SQL Server thật, không dùng dữ liệu trả về giả. Mỗi lần chạy tạo CoffeeTest_<UUID> riêng. Bộ kiểm thử chỉ dọn cơ sở dữ liệu có tên đã tạo trong chính lần chạy đó.',
230:'Lần chạy mới bắt đầu lúc 22 giờ 42 phút 46 giây ngày 22/10/2026, múi giờ UTC+7. Kết quả có 19 kiểm thử đạt, 0 thất bại, 0 lỗi, 0 bỏ qua, mã thoát 0. unittest ghi 19,656 giây, còn thời gian tiến trình là 20,185 giây. Database thử được quan sát khi tạo và không còn sau khi kết thúc. Nhật ký đầy đủ là verification/unittest_moi.stderr.txt, thông tin thời điểm và mã thoát là verification/unittest_moi.json. Kết quả này độc lập với các lần chạy đã lưu trước đó.',
231:'python -B -m unittest discover -s tests -v\nRan 19 tests in 19.656s\nOK',
232:'Các kết quả mới về dữ liệu và nghiệp vụ được đối chiếu trong Bảng 4.1 với các phương thức của tests/test_coffee.py.',
234:'Bảng 4.2 ghi phần kiểm tra giao dịch, xử lý đồng thời, thống kê và điều khiển giao diện trong cùng lần chạy mới.',
237:'Kịch bản lịch sử ngày 20/10/2026 được lưu tại .report_work/evidence_new.json. Dữ liệu được tạo riêng gồm năm món khởi đầu, tám bàn, một khách và một nhân viên có tài khoản. Các đơn có ngày thanh toán trong kỳ được chuẩn bị cho trình diễn, không phải doanh thu thực tế của quán. Bảng 4.3 chỉ ghi lại kết quả lịch sử, không gộp vào kết quả 19 kiểm thử mới.',
238:'Các thao tác và kết quả lịch sử trong Bảng 4.3 được đối chiếu với nhật ký và CSV đã lưu.',
240:'Ngày 22/10/2026, CSV trong docs/doanh_thu_kiem_tra.csv được đọc lại cùng bản tại D:\\NCTU\\Python\\ThucHanh\\SoLieuCSVProject. Tập tin có BOM UTF-8, đúng kỳ 14/10/2026 đến 20/10/2026, 8 đơn và doanh thu 1.200.000 đồng. Cà phê đen có 30 ly, 750.000 đồng. Cà phê sữa có 15 ly, 450.000 đồng. Tổng hai dòng khớp dòng tổng. Database trình diễn cũ không còn nên chưa thể tái xác nhận dữ liệu SQL lịch sử. Chi tiết kiểm tra tập tin được lưu tại verification/csv_lich_su.json.',
242:'Trong phạm vi các trường hợp đã chạy, chương trình xử lý đúng dữ liệu hợp lệ, từ chối dữ liệu sai và hoàn tác các cập nhật liên quan khi phát sinh lỗi đã kiểm tra. Hai vai trò được kiểm tra ở giao diện và dịch vụ. Các kết luận chỉ áp dụng cho commit, môi trường và tập dữ liệu được ghi nhận, không phải chứng nhận an toàn hoặc hiệu năng cho mọi tình huống sử dụng.',
243:'Việc đóng cửa sổ và đọc lại bằng kết nối mới có chứng cứ lịch sử, đồng thời các kiểm thử mới đọc lại dữ liệu đã commit. Chưa thử tắt máy rồi khởi động lại, mất điện, tải lớn, nhiều máy vận hành dài ngày hoặc bảo mật độc lập. Hai lần mở giao diện bổ sung kết thúc trước khi chụp được ảnh có thể xác nhận. Vì vậy, báo cáo giữ bộ ảnh cũ và không khẳng định có ảnh mới. Kiểm tra xuất CSV bổ sung tự động cung cấp đường dẫn cho hộp chọn tệp, chưa xác nhận thao tác chọn đường dẫn bằng chuột trong lần mới.',
247:'Lần kiểm định mới ngày 22/10/2026 có 19 kiểm thử đạt và mã thoát 0. Kịch bản bổ sung trên database riêng xác nhận tổng 80.000 đồng, nhận 100.000 đồng, thừa 20.000 đồng và cộng 8 điểm. CSV 8 đơn, 1.200.000 đồng là chứng cứ lịch sử ngày 20/10/2026, được đọc lại để kiểm tra tính nhất quán. Tám nội dung học phần được liên hệ với các tệp và hàm thực tế của dự án.',
280:'Bộ kiểm thử cần SQL Server, quyền tạo và xóa database thử và môi trường có Tkinter. Cơ sở dữ liệu CoffeeTest_<UUID> được tạo riêng rồi dọn sau khi hoàn tất. Nếu lệnh python trỏ tới WindowsApps nhưng không chạy, chọn trình thông dịch Python đã cài trong VS Code hoặc gọi đường dẫn python.exe của bản cài đó. Lần kiểm định chỉ điều chỉnh PATH của tiến trình chạy thử, không đổi cấu hình hệ thống. Biên bản, nhật ký và ma trận đối chiếu nằm trong verification/BAO_CAO_KIEM_DINH_CUOI.md.'
}
updates.update({
143:'Giao diện gọi CoffeeService để kiểm tra quyền, trạng thái và xử lý dữ liệu. Các thao tác ghi dùng try/except/finally để commit(), rollback() và đóng kết nối. SQL không đặt trong các biểu mẫu.',
166:'Lỗi được rollback() và đóng kết nối. Sửa đơn phải khớp PhienBan. Chuyển bàn cập nhật trạng thái cả hai bàn.',
168:'PaymentDialog.change_amount() kiểm tra tiền và tính tiền thừa. update_change() khóa nút khi dữ liệu sai hoặc còn thiếu. confirm() kiểm tra lại rồi gọi finish_order(). Dịch vụ không nhận hoặc lưu tiền khách đưa. Kiểm tra đủ tiền thuộc giao diện, chưa áp dụng cho lời gọi trực tiếp đến dịch vụ.',
172:'Hủy đơn dùng finish_order(pay=False), ghi Đã huỷ, không cộng điểm hoặc ghi thời điểm thanh toán. Khi thu tiền, giao diện truyền expected_version để kiểm tra đơn đã thay đổi. Tham số này là tùy chọn tại dịch vụ.',
264:'Cài Python cho Windows từ python.org, giữ Tcl/Tk và pip, chọn thêm Python vào PATH. Nếu lệnh python trỏ tới WindowsApps nhưng không chạy, chọn trình thông dịch đã cài trong VS Code. Lần kiểm định dùng Python 3.14.3. Kiểm tra bằng các lệnh sau.',
280:'Bộ kiểm thử tạo và dọn database CoffeeTest_<UUID> riêng. Nhật ký và ma trận đối chiếu nằm trong verification.'
})
for index,value in updates.items():replace(index,value)
for anchor_index,value in [(83,'BOM: Byte Order Mark, dấu nhận biết mã hóa ở đầu tập tin'),(89,'UUID: Universally Unique Identifier, mã định danh dùng tạo tên database thử riêng')]:
    p=E.Element(q('p'))
    prop=E.SubElement(p,q('pPr'));indent=E.SubElement(prop,q('ind'));indent.set(q('firstLine'),'0')
    settext(p,value)
    paragraphs[anchor_index].addnext(p)
caption(176,'Môi trường được kiểm tra ngày 22/10/2026')
caption(239,'Kết quả trình diễn lịch sử ngày 20/10/2026')
insert_after(240,[
    'Kiểm tra bổ sung ngày 22/10/2026 dùng một database riêng khác với bộ unittest. PaymentDialog từ chối chuỗi rỗng, chữ, số âm, số có dấu phẩy, chữ số không thuộc ASCII và chuỗi quá 15 chữ số. Tiền nhận 50.000 đồng không cho hoàn tất đơn 80.000 đồng. Khi nhận 100.000 đồng, tiền thừa là 20.000 đồng. Sau xác nhận, SQL ghi đơn Đã thanh toán, khách có 8 điểm và bàn Trống. Đơn hủy được kiểm tra riêng và bị loại khỏi doanh thu.',
    'Để xác nhận giới hạn TOP 10, dữ liệu bổ sung có 13 món đã bán qua 12 đơn. Truy vấn trả đúng 10 món, tổng doanh thu toàn kỳ 245.000 đồng, tổng 10 dòng chi tiết 212.000 đồng. StatisticsTab.export() được gọi với đường dẫn lưu do công cụ kiểm thử cung cấp. Phần truy vấn và ghi tập tin chạy thật, không thay SQL bằng dữ liệu giả. verification/doanh_thu_kiem_dinh_moi.csv có BOM UTF-8 và khớp các giá trị trên. Đây là dữ liệu thử mới, không dùng thay cho CSV lịch sử.',
    'Kết quả từng bước và xác nhận dọn database được lưu tại verification/bo_sung_tien_do.json. Thời gian của kịch bản bổ sung không cộng vào 19,656 giây của unittest. Hai lần mở giao diện chưa hoàn tất được giữ riêng trong nhật ký, không tính thành trường hợp đạt.'
])
# Thêm đúng một dòng IDE vào bảng môi trường, dùng lại định dạng của bảng gốc.
env=tables[9]
newrow=deepcopy(env.findall(q('tr'))[2])
for node in newrow.iter():
    for key in list(node.attrib):
        if 'paraId' in key or 'textId' in key:del node.attrib[key]
for cell,value in zip(newrow.findall(q('tc')),['IDE sử dụng','Visual Studio Code 1.140.0, x64.']):
    settext(cell.find(q('p')),value)
env.insert(4,newrow)
# Không thay các ô đã có, chỉ bổ sung giới hạn thực của phần CSV.
for p in tables[8].xpath('.//w:p',namespaces=NS):
    old=text(p)
    if old=='Một dòng cho mỗi sản phẩm thuộc kết quả thống kê bán chạy.':settext(p,'Tối đa 10 dòng sản phẩm thuộc kết quả thống kê bán chạy.')
# Sửa ngày truy cập thực, dùng tài liệu Python đúng nhánh 3.14.
for index in range(252,262):
    p=paragraphs[index]
    for t in p.xpath('.//w:t',namespaces=NS):
        if t.text:t.text=t.text.replace('04/10/2026','22/10/2026').replace('https://docs.python.org/3/library/','https://docs.python.org/3.14/library/')
    for t in p.xpath('.//w:t',namespaces=NS):
        if t.text and 'Truy cập ngày' in t.text:break
rels=E.fromstring(data['word/_rels/document.xml.rels'])
for rel in rels:
    url=rel.get('Target','')
    if 'https://docs.python.org/3/library/' in url:rel.set('Target',url.replace('/3/library/','/3.14/library/'))
    if url=='https://learn.microsoft.com/en-us/sql/t-sql/data-types/rowversion-transact-sql':
        rel.set('Target',url+'?view=sql-server-ver16')
for t in paragraphs[254].xpath('.//w:t',namespaces=NS):
    if t.text and t.text.startswith('https://learn.microsoft.com/'):t.text+='?view=sql-server-ver16'
# Yêu cầu trường: danh mục chỉ đến cấp mục thứ hai.
for instr in root.xpath('//w:instrText',namespaces=NS):
    if instr.text and 'TOC \\o "1-3"' in instr.text:instr.text=instr.text.replace('"1-3"','"1-2"')
settings=E.fromstring(data['word/settings.xml'])
update=settings.find(q('updateFields'))
if update is None:update=E.SubElement(settings,q('updateFields'))
update.set(q('val'),'true')
data['word/document.xml']=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
data['word/_rels/document.xml.rels']=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
data['word/settings.xml']=E.tostring(settings,xml_declaration=True,encoding='UTF-8',standalone=True)
styles=E.fromstring(data['word/styles.xml'])
for style in styles.findall(q('style')):
    if style.get(q('styleId')) in ['TOC1','TOC2','TOC3']:
        prop=style.find(q('pPr'))
        if prop is None:prop=E.SubElement(style,q('pPr'))
        spacing=prop.find(q('spacing'))
        if spacing is None:spacing=E.SubElement(prop,q('spacing'))
        for key,value in {'before':'0','after':'0','line':'240','lineRule':'auto'}.items():spacing.set(q(key),value)
data['word/styles.xml']=E.tostring(styles,xml_declaration=True,encoding='UTF-8',standalone=True)
assert ';' not in text(root)
with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
    for info in infos:z.writestr(info,data[info.filename])
(OUT/'nhat_ky_bien_tap.json').write_text(json.dumps({'source':str(SOURCE),'candidate':str(TARGET),'changes':changes,'images_changed':0,'tables_deleted':0},ensure_ascii=False,indent=2),encoding='utf-8')
print('Đã biên tập bản sao:',TARGET)
print('Giữ nguyên',len(tables),'bảng và',len([x for x in data if x.startswith('word/media/')]),'ảnh')
