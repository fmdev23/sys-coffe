from pathlib import Path
import re

W=Path(__file__).parent
s=(W/'build_report.py').read_text(encoding='utf-8')
# Giữ nội dung và bằng chứng đã thu thập, dùng hình mới từ cùng mã PlantUML.
s=s[:s.index('class Diagram:')]+s[s.index('doc=Document()'):]
s=s.replace('sec.footer_distance=Cm(1)','sec.footer_distance=Cm(1)\n    sec.header_distance=Cm(1)')
s=s.replace("s.paragraph_format.space_after=Pt(6)","s.paragraph_format.space_before=Pt(6)\n    s.paragraph_format.space_after=Pt(0)")
s=s.replace('s.paragraph_format.space_before=Pt(10)','s.paragraph_format.space_before=Pt(6)')
s=s.replace("return doc.add_paragraph(text)",r'''pp=doc.add_paragraph()
    foreign=('Data Flow Diagram','Byte Order Mark')
    for part in re.split(r'(Data Flow Diagram|Byte Order Mark)',text):
        pp.add_run(part).italic=part in foreign
    return pp''')
s=s.replace("styles['Heading 1'].font.size=Pt(15)","styles['Heading 1'].font.size=Pt(14)\nstyles['Heading 1'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER\nstyles['Heading 3'].paragraph_format.first_line_indent=Cm(1)")
s=s.replace("styles['Caption'].font.italic=True", "styles['Caption'].font.italic=False\nstyles['Caption'].font.bold=False\nstyles['Caption'].paragraph_format.line_spacing=1.0")
s=s.replace("styles[name].paragraph_format.space_after=Pt(3)","styles[name].paragraph_format.space_before=Pt(6)\n    styles[name].paragraph_format.space_after=Pt(0)")
s=s.replace("pp.paragraph_format.line_spacing=1.2","pp.paragraph_format.line_spacing=1.0\n                pp.paragraph_format.space_before=Pt(0)")
s=s.replace("pp.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT\n                pp.paragraph_format.space_after", "pp.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.RIGHT if i>0 and re.fullmatch(r'[0-9 /.,]+',str(txt)) else WD_ALIGN_PARAGRAPH.LEFT\n                pp.paragraph_format.space_after")
s=s.replace("def h(text,level=2):return doc.add_heading(text,level)",r'''chapter='G'
section_no=0
subsection_no=0
appendix=False
seq_seen=set()
def h(text,level=None):
    global chapter,section_no,subsection_no,appendix
    if level is None:
        level=2 if section_no==0 or chapter=='G' else 3
    if level==1:
        m=re.match(r'CHƯƠNG (\d+)\. (.*)',text)
        if m:
            chapter=m.group(1)
            section_no=subsection_no=0
            text='CHƯƠNG '+chapter+'\n'+m.group(2)
        elif text.startswith('PHỤ LỤC'):
            chapter='A'
            section_no=subsection_no=0
            appendix=True
            text='PHỤ LỤC A\nCÀI ĐẶT VÀ SỬ DỤNG'
        return doc.add_heading(text,1)
    if chapter in ('1','2','3','4','A'):
        if level==2:
            section_no+=1
            subsection_no=0
            text=f'{chapter}.{section_no} '+text.upper()
        else:
            subsection_no+=1
            text=f'{chapter}.{section_no}.{subsection_no} '+text
    # Đưa đúng hai cấp tiểu mục vào mục lục, không đưa mục nhỏ của phụ lục.
    pp=doc.add_heading(text,level)
    if appendix:
        style_name='Appendix '+str(level)
        if style_name not in styles:
            st=styles.add_style(style_name,1)
            st.base_style=styles['Normal']
            st.font.bold=True
            st.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
            st.paragraph_format.first_line_indent=Cm(0 if level==2 else 1)
            st.paragraph_format.keep_with_next=True
        pp.style=styles[style_name]
        outline=OxmlElement('w:outlineLvl')
        outline.set(qn('w:val'),'9')
        pp._p.get_or_add_pPr().append(outline)
    return pp''')
s=s.replace('import json, math, textwrap','import json, math, textwrap, re')
a=s.index('def caption(label,text):')
b=s.index('\ndef picture(',a)
s=s[:a]+r'''def caption(label,text):
    pp=doc.add_paragraph(style='Caption')
    pp.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT if label=='Bảng' else WD_ALIGN_PARAGRAPH.CENTER
    pp.paragraph_format.keep_with_next=label=='Bảng'
    pp.add_run(label+' '+chapter+'.')
    key=(label,chapter)
    reset=r' \r 1' if key not in seq_seen else ''
    seq_seen.add(key)
    field(pp,'SEQ '+('Figure' if label=='Hình' else 'Table')+reset+r' \* ARABIC')
    pp.add_run(' '+text)
'''+s[b:]
# Không để lưu đồ cao vượt trang. Tỉ lệ ảnh giữ nguyên.
s=s.replace("shape=run.add_picture(str(W/f'{name}.png'),width=Cm(width))", "img=Image.open(W/f'{name}.png')\n    max_height=17.2 if name.startswith('flow_') else 19\n    width=min(width,max_height*img.width/img.height)\n    shape=run.add_picture(str(W/f'{name}.png'),width=Cm(width))")
s=s.replace("pp.paragraph_format.page_break_before=True", "pp.paragraph_format.page_break_before=title not in ('Luồng dữ liệu tổng quát','Các trường dữ liệu quan trọng')",1)
s=s.replace("cover('MỤC LỤC',15", "cover('MỤC LỤC',14")
s=s.replace('TOC \\\\o "1-2"','TOC \\\\o "1-3"')
a=s.index("doc.add_page_break()\ncover('DANH MỤC HÌNH")
b=s.index('\nbody=doc.add_section',a)
s=s[:a]+r'''doc.add_page_break()
cover('DANH MỤC BẢNG',14,True,after=12)
field(doc.add_paragraph(),'TOC \\h \\z \\c "Table"')
doc.add_page_break()
cover('DANH MỤC HÌNH VÀ SƠ ĐỒ',14,True,after=12)
field(doc.add_paragraph(),'TOC \\h \\z \\c "Figure"')
doc.add_page_break()
cover('DANH MỤC TỪ VIẾT TẮT',14,True,after=12)
for short,meaning in [
    ('BOM','Byte Order Mark, dấu nhận biết mã hoá ở đầu tệp'),
    ('CRUD','Create, Read, Update, Delete, thêm, đọc, sửa và xoá'),
    ('CSV','Comma-Separated Values, tệp dữ liệu phân cách bằng dấu phẩy'),
    ('DFD','Data Flow Diagram, sơ đồ luồng dữ liệu'),
    ('FK','Foreign Key, khoá ngoại'),
    ('IDE','Integrated Development Environment, môi trường phát triển tích hợp'),
    ('ODBC','Open Database Connectivity, giao tiếp kết nối cơ sở dữ liệu'),
    ('PBKDF2','Password-Based Key Derivation Function 2, hàm dẫn xuất khoá từ mật khẩu'),
    ('PK','Primary Key, khoá chính'),
    ('SQL','Structured Query Language, ngôn ngữ truy vấn có cấu trúc'),
    ('UTF-8','Unicode Transformation Format 8-bit, mã hoá văn bản Unicode')]:
    pp=doc.add_paragraph()
    pp.paragraph_format.first_line_indent=Cm(0)
    pp.add_run(short+': ').bold=True
    pp.add_run(meaning)
'''+s[b:]
# Lần đầu xuất hiện có tên đầy đủ, các định danh mã nguồn giữ nguyên.
s=s.replace('ứng dụng desktop Coffee','ứng dụng trên máy tính Coffee')
s=s.replace('Đây là ứng dụng desktop trên Windows','Đây là ứng dụng trên máy tính Windows')
s=s.replace('không phải ba dịch vụ độc lập','các phần không triển khai thành dịch vụ độc lập')
s=s.replace('không cần thêm thư viện xử lý dữ liệu','không cần thêm thư viện xử lý dữ liệu')
s=s.replace("p('DFD cấp 0 mô tả tổng quát dữ liệu đi vào và đi ra khỏi ứng dụng. Toàn bộ ứng dụng là tiến trình 0. Nhân viên và quản lý cung cấp dữ liệu đầu vào, nhận kết quả xử lý. SQL Server là kho lưu trữ chính. Báo cáo CSV là dữ liệu đầu ra được giao cho người nhận báo cáo.')", "p('Sơ đồ luồng dữ liệu (Data Flow Diagram, DFD) cấp 0 được trình bày theo dạng sơ đồ ngữ cảnh. Toàn bộ ứng dụng là tiến trình 0, trao đổi dữ liệu với hai tác nhân nhân viên và quản lý. Các mũi tên có tên dữ liệu và chiều truyền cụ thể. Kho lưu trữ bên trong được giải thích ở sơ đồ riêng, phù hợp cách phân biệt sơ đồ ngữ cảnh và các mức phân rã (Visual Paradigm, không ghi năm).')")
s=s.replace("p('Luồng cập nhật bao gồm danh mục, thông tin đơn, trạng thái thanh toán và điểm khách hàng. Luồng tra cứu trả về thông tin để hiển thị trên giao diện. Chỉ quản lý được yêu cầu báo cáo doanh thu. CSV không thay thế cơ sở dữ liệu và không phải đầu vào tự động của chương trình.')", "p('Nhân viên gửi thông tin đăng nhập, dữ liệu đơn và xác nhận thu tiền hoặc huỷ. Quản lý còn gửi thông tin quản trị và kỳ thống kê. Hệ thống trả kết quả xử lý, danh mục và thông tin đơn theo quyền. Báo cáo CSV được trả cho quản lý, không gán thêm một tác nhân nhận báo cáo chưa có trong ứng dụng.')")
insert="""page('Lưu trữ và xuất dữ liệu')
p('SQL Server lưu dữ liệu chính của chương trình. Các thao tác nhập được kiểm tra rồi ghi trong giao dịch. Kết quả tra cứu được đưa lên giao diện. Tệp CSV được tạo khi quản lý chọn kỳ báo cáo và đường dẫn lưu, không thay thế cơ sở dữ liệu và không được nhập ngược tự động.')
picture('storage','Luồng lưu trữ SQL Server và xuất báo cáo CSV')
p('Ví dụ, dữ liệu thanh toán được lưu trong DonHang và các bảng có liên quan. Chức năng xuất tệp đọc các đơn đã thanh toán trong kỳ và ghi thông tin tổng hợp cùng các món bán chạy. Cách lưu trữ này cho phép mở lại ứng dụng mà vẫn tra cứu được dữ liệu đã ghi.')

"""
s=s.replace("page('CHƯƠNG 1. ĐẶC TẢ YÊU CẦU',1)",insert+"page('CHƯƠNG 1. ĐẶC TẢ YÊU CẦU',1)")
s=s.replace("p('Hệ thống được chia thành bốn nhóm: phiên làm việc, danh mục, phục vụ và báo cáo. Nhóm phục vụ là luồng chính của nhân viên. Nhóm danh mục và báo cáo giúp quản lý chuẩn bị dữ liệu và kiểm tra kết quả hoạt động.')", "p('Hệ thống được chia thành bốn nhóm: phiên làm việc, danh mục, đơn hàng và báo cáo. Mỗi nhánh được liên hệ với các hàm chính để có thể tra cứu trong mã nguồn. Đường nối thể hiện quan hệ phân rã, không biểu diễn thứ tự chạy của chương trình.')")
s=s.replace("p('Các chức năng cùng dùng dịch vụ CoffeeService.","p('login, change_password và các hàm danh mục, đơn, thống kê thuộc CoffeeService. show_login thuộc CoffeeApp, refresh thuộc Dashboard, export thuộc StatisticsTab. Các hàm tài khoản là save_account, delete_account và list_accounts. Sơ đồ chỉ chọn hàm chính, các chức năng cùng dùng dịch vụ CoffeeService.")
s=s.replace('Các mũi tên trong sơ đồ đi từ bản ghi được tham chiếu đến bảng chứa khoá ngoại.', 'Sơ đồ dùng ký hiệu chân quạ để thể hiện số lượng bản ghi tham gia quan hệ. PK là khoá chính, FK là khoá ngoại, UNIQUE là ràng buộc duy nhất và NULL là trường có thể không có giá trị.')
s=s.replace("p('Một nhân viên có tối đa một tài khoản.","p('Ký hiệu hai vạch biểu thị đúng một, vòng tròn và vạch biểu thị không hoặc một, vòng tròn và chân quạ biểu thị không hoặc nhiều. Một nhân viên có tối đa một tài khoản.")
s=s.replace('Một đơn có nhiều chi tiết, mỗi chi tiết tham chiếu một sản phẩm.', 'Theo nghiệp vụ, một đơn được lưu phải có ít nhất một món. Riêng khoá ngoại SQL không bắt buộc mỗi đơn có chi tiết, nên sơ đồ dữ liệu dùng quan hệ không hoặc nhiều ở phía chi tiết. Mỗi chi tiết bắt buộc tham chiếu một đơn và một sản phẩm.')
s=s.replace('Tổng đơn bằng tổng của số lượng nhân đơn giá từng món.', 'Giao diện kiểm tra tiền nhận trước khi gọi finish_order. Số tiền nhận và tiền thừa không được lưu vào cơ sở dữ liệu. Giao diện luôn truyền phiên bản đơn để dịch vụ đối chiếu. Tổng đơn bằng tổng của số lượng nhân đơn giá từng món.')
s=s.replace('Toàn bộ ghi đơn, chi tiết và trạng thái bàn nằm trong một giao dịch, có lỗi thì hoàn tác.', 'Việc kiểm tra từng sản phẩm, lấy giá và cộng tổng diễn ra trong vòng lặp của giao dịch. Khi chuyển bàn, cả bàn cũ và bàn mới được đồng bộ. Mọi ngoại lệ trong khối giao dịch, kể cả lỗi truy vấn hoặc kiểm tra, đều dẫn đến hoàn tác. Các nhánh lỗi trong lưu đồ thể hiện gọn cơ chế này.')
s=s.replace('CSV dùng UTF-8 có BOM', 'CSV dùng mã hoá UTF-8 với dấu nhận biết ở đầu tệp (Byte Order Mark, BOM)')
# Chuyển các trích dẫn số sang tác giả–năm và giữ mọi nguồn được trích.
citations={
 '[1, 7]':'(abdelbend, không ghi năm a, b)',
 '[1]':'(abdelbend, không ghi năm b)',
 '[2]':'(Python Software Foundation, không ghi năm d)',
 '[3]':'(mkleehammer và cộng sự, không ghi năm b)',
 '[4]':'(Python Software Foundation, không ghi năm a)',
 '[5]':'(Python Software Foundation, không ghi năm b)',
 '[6]':'(Python Software Foundation, không ghi năm e)',
 '[8]':'(Microsoft, không ghi năm)',
 '[9]':'(mkleehammer và cộng sự, không ghi năm a)',
 '[10]':'(Python Software Foundation, không ghi năm c)'}
for old,new in citations.items():s=s.replace(old,new)
# Bảng khảo sát giữ tên nguồn gọn, đưa trích dẫn ngay sau bảng.
for label,cite in [('Restaurant Management System',citations['[1]']),('Tkinter/ttk',citations['[2]']),('pyodbc',citations['[3]']),('csv',citations['[4]']),('decimal',citations['[5]']),('unittest',citations['[6]'])]:
 s=s.replace(label+' '+cite,label)
s=s.replace("h('Phân tích ứng dụng tham khảo chính')", "p('Các thư viện được sử dụng theo tài liệu chính thức: Tkinter/ttk cho giao diện (Python Software Foundation, không ghi năm d), pyodbc cho kết nối (mkleehammer và cộng sự, không ghi năm b), csv cho ghi tệp (Python Software Foundation, không ghi năm a), decimal cho tính tiền (Python Software Foundation, không ghi năm b) và unittest cho kiểm thử (Python Software Foundation, không ghi năm e).')\nh('Phân tích ứng dụng tham khảo chính')")
a=s.index('refs=[')
b=s.index("\npage('PHỤ LỤC",a)
s=s[:a]+r'''refs=[
 ('abdelbend','không ghi năm a','db.py trong Restaurant Management System','https://github.com/abdelbend/Restaurant-Management-System/blob/main/db.py'),
 ('abdelbend','không ghi năm b','Restaurant Management System','https://github.com/abdelbend/Restaurant-Management-System'),
 ('Gonzalez, Willie','không ghi năm','Food Ordering System Context DFD','https://circle.visual-paradigm.com/food-ordering-system-context-dfd/'),
 ('Microsoft','không ghi năm','rowversion (Transact-SQL)','https://learn.microsoft.com/en-us/sql/t-sql/data-types/rowversion-transact-sql'),
 ('mkleehammer và cộng sự','không ghi năm a','Database Transaction Management','https://github.com/mkleehammer/pyodbc/wiki/Database-Transaction-Management'),
 ('mkleehammer và cộng sự','không ghi năm b','pyodbc — Python ODBC bridge','https://github.com/mkleehammer/pyodbc'),
 ('Python Software Foundation','không ghi năm a','csv — CSV File Reading and Writing','https://docs.python.org/3/library/csv.html'),
 ('Python Software Foundation','không ghi năm b','decimal — Decimal fixed-point and floating-point arithmetic','https://docs.python.org/3/library/decimal.html'),
 ('Python Software Foundation','không ghi năm c','hashlib — Secure hashes and message digests','https://docs.python.org/3/library/hashlib.html'),
 ('Python Software Foundation','không ghi năm d','tkinter — Python interface to Tcl/Tk','https://docs.python.org/3/library/tkinter.html'),
 ('Python Software Foundation','không ghi năm e','unittest — Unit testing framework','https://docs.python.org/3/library/unittest.html')]
p('Tài liệu tiếng Anh')
for author,year,title,url in refs:
    pp=doc.add_paragraph()
    pp.paragraph_format.left_indent=Cm(1)
    pp.paragraph_format.first_line_indent=Cm(-1)
    pp.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
    pp.paragraph_format.line_spacing=1.0
    pp.add_run(author+' ('+year+'). ')
    pp.add_run(title).italic=True
    pp.add_run('. Truy cập ngày 04/10/2026. ')
    hyp=OxmlElement('w:hyperlink')
    hyp.set(qn('r:id'),pp.part.relate_to(url,RT.HYPERLINK,is_external=True))
    rr=OxmlElement('w:r')
    rp=OxmlElement('w:rPr')
    f=OxmlElement('w:rFonts')
    f.set(qn('w:ascii'),'Times New Roman')
    f.set(qn('w:hAnsi'),'Times New Roman')
    rp.append(f)
    size=OxmlElement('w:sz')
    size.set(qn('w:val'),'26')
    rp.append(size)
    rr.append(rp)
    tt=OxmlElement('w:t')
    tt.set(qn('xml:space'),'preserve')
    tt.text=url.replace('/', '/\u200b').replace('-', '-\u200b')
    rr.append(tt)
    hyp.append(rr)
    pp._p.append(hyp)
'''+s[b:]
# Một số tiêu đề có dấu hai chấm từ bản cũ, bỏ dấu đó theo DNC.
s=re.sub(r"(page\(')([^']+)(?='\))",lambda m:m.group(1)+m.group(2).replace(':',''),s)
s=s.replace("# Bìa theo mẫu của học phần.","# Bìa theo mẫu của học phần.")
s=s.replace("update=OxmlElement('w:updateFields')", "for pp in doc.paragraphs:\n    if pp.style.name=='Heading 1':\n        pp.paragraph_format.page_break_before=True\n# Giãn dòng đơn trong toàn bộ phụ lục.\nappendix_started=False\nfor pp in doc.paragraphs:\n    if pp.text.startswith('PHỤ LỤC A'):\n        appendix_started=True\n    if appendix_started:\n        pp.paragraph_format.line_spacing=1.0\nupdate=OxmlElement('w:updateFields')")
# Giới thiệu dùng tiêu đề không đánh số, hình/bảng G.x phân biệt các chương.
s=s.replace('(Visual Paradigm, không ghi năm)','(Gonzalez, không ghi năm)')
s=s.replace("img=Image.open(W/f'{name}.png')", "image_path=ROOT/'docs/DFD_Muc0.png' if name=='dfd' else W/f'{name}.png'\n    img=Image.open(image_path)")
s=s.replace("run.add_picture(str(W/f'{name}.png'),width=Cm(width))", "run.add_picture(str(image_path),width=Cm(width))")
s=s.replace('Toàn bộ ứng dụng là tiến trình 0, trao đổi dữ liệu với hai tác nhân nhân viên và quản lý.', 'Toàn bộ ứng dụng được biểu diễn bằng một tiến trình trung tâm, đánh số 1 trong bản vẽ, trao đổi dữ liệu với hai tác nhân nhân viên và quản lý.')
exec(compile(s,str(W/'build_report.py'),'exec'),{'__file__':str(W/'build_report.py')})
