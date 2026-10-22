import sys
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import csv,json,time,platform,re,uuid
from datetime import date,datetime,timedelta
from decimal import Decimal
from PIL import ImageGrab
import pyodbc
import db_connection,database_setup
from models.service import login,STAFF,PAID,PENDING,CANCELLED,AppError
from main import CoffeeApp
from ui.order_editor import OrderEditor
from ui.payment_dialog import PaymentDialog

work=Path(__file__).parent
images=ROOT/'sodo'
original=db_connection.DATABASE
database='CoffeeTest_'+uuid.uuid4().hex
db_connection.DATABASE=database
app=None
events=[]
out=ROOT/'docs/doanh_thu_kiem_tra.csv'

def record(name,result):
    events.append({'thao_tac':name,'ket_qua':result,'thoi_gian':datetime.now().isoformat(timespec='seconds')})
    print(name,':',result,flush=True)

def shot(widget,name):
    widget.update()
    widget.lift()
    widget.attributes('-topmost',True)
    widget.update()
    time.sleep(.3)
    x,y=widget.winfo_rootx(),widget.winfo_rooty()
    ImageGrab.grab(bbox=(x,y,x+widget.winfo_width(),y+widget.winfo_height())).save(images/(name+'.png'))
    widget.attributes('-topmost',False)

def sql(statement,*params):
    connection=db_connection.connect()
    try:
        cursor=connection.cursor()
        cursor.execute(statement,*params)
        value=cursor.fetchall() if cursor.description else []
        connection.commit()
        return value
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

def complete():
    global app
    if not out.exists():
        if time.monotonic()>deadline:
            record('Xuất CSV','Chưa hoàn thành hộp thoại lưu trong thời gian thử')
            app.destroy()
            return
        app.after(300,complete)
        return
    with out.open(encoding='utf-8-sig',newline='') as file:
        exported=list(csv.reader(file))
    total,count,products=manager.statistics(date.today()-timedelta(days=6),date.today()+timedelta(days=1))
    assert out.read_bytes().startswith(b'\xef\xbb\xbf')
    assert Decimal(exported[1][1])==total and int(exported[1][3])==count
    assert total==Decimal(1200000) and count==8
    record('Xuất CSV bằng hộp thoại lưu thật',f'{total} đồng, {count} đơn, UTF-8 có BOM')
    app.show_main(staff)
    assert set(app.screen.pages)=={'orders','tables','products'}
    shot(app,'giao_dien_nhan_vien')
    record('Đăng nhập nhân viên','Đúng ba trang đơn hàng, bàn, thực đơn')
    app.destroy()
    app=None
    fresh=login('admin','Admin@123')
    saved,_=fresh.get_order(order)
    points=sql('SELECT DiemTichLuy FROM dbo.KhachHang WHERE MaKH = ?',customer)[0][0]
    assert saved['TrangThai']==PAID and saved['TongTien']==Decimal(80000) and points==8
    app=CoffeeApp()
    app.show_main(fresh)
    app.update()
    record('Đóng cửa sổ và mở lại bằng kết nối mới','Đơn đã thanh toán, 80.000 đồng, khách có 8 điểm')
    sql_info=sql("SELECT CAST(SERVERPROPERTY('ProductVersion') AS NVARCHAR(100)), CAST(SERVERPROPERTY('Edition') AS NVARCHAR(100))")[0]
    env={'python':platform.python_version(),'pyodbc':pyodbc.version,'windows':platform.platform(),
        'tk':app.tk.call('info','patchlevel'),'capture_date':date.today().isoformat(),
        'sql':list(sql_info),'csv_total':str(total),'csv_count':count,'csv_rows':exported,'events':events,
        'database_test':database,'server':db_connection.SERVER}
    (work/'evidence_new.json').write_text(json.dumps(env,ensure_ascii=False,indent=2),encoding='utf-8')
    app.destroy()

try:
    database_setup.setup()
    manager=login('admin','Admin@123')
    customer=manager.save_entity('customers',{'HoTen':'Nguyễn Thanh An','SDT':'0912345678','DiemTichLuy':0})
    employee=manager.save_entity('employees',{'HoTen':'Trần Ngọc Mai','SDT':'0901234567','ChucVu':'Thu ngân'})
    manager.save_account('ngocmai','NhanVien@123',STAFF,employee)
    staff=login('ngocmai','NhanVien@123')
    tables,_,products=manager.order_options()
    coffee=next(p['MaSP'] for p in products if p['TenSP']=='Cà phê đen')
    milk=next(p['MaSP'] for p in products if p['TenSP']=='Cà phê sữa')
    for days in range(6,-1,-1):
        order_id=manager.save_order(tables[days%len(tables)]['MaBan'],None,[(coffee,days+1),(milk,2)])
        manager.finish_order(order_id)
        sql('UPDATE dbo.DonHang SET ThoiGianThanhToan = ? WHERE MaDH = ?',datetime.combine(date.today()-timedelta(days=days),datetime.min.time()).replace(hour=10),order_id)
    app=CoffeeApp()
    shot(app,'dang_nhap')
    app.screen.username.set('admin')
    app.screen.password.set('sai_mat_khau')
    app.screen.login()
    assert 'không đúng' in app.screen.error_label.cget('text')
    record('Đăng nhập sai','Hiển thị lỗi và giữ màn hình đăng nhập')
    app.screen.password.set('Admin@123')
    app.screen.login()
    assert len(app.screen.pages)==8
    record('Đăng nhập quản lý','Đúng tám trang')
    app.screen.show_page('products')
    tab=app.screen.pages['products']
    form=tab.add()
    form.variables['TenSP'].set('Món kiểm tra nhập liệu')
    form.variables['DanhMuc'].set('Kiểm tra')
    form.variables['Gia'].set('abc')
    form.save()
    assert form.error_label.cget('text')
    record('Nhập chữ vào giá sản phẩm','Biểu mẫu giữ lại và báo lỗi')
    form.variables['Gia'].set('27000')
    form.save()
    created=next(p for p in manager.list_entities('products') if p['TenSP']=='Món kiểm tra nhập liệu')
    manager.delete_entity('products',created['MaSP'])
    record('Thêm và xoá món kiểm tra','Dữ liệu SQL được thêm rồi xoá đúng')
    order=manager.save_order(tables[0]['MaBan'],customer,[(coffee,2),(milk,1)])
    app.screen.show_page('dashboard')
    shot(app,'tong_quan')
    app.screen.show_page('products')
    shot(app,'thuc_don')
    editor=OrderEditor(app,manager,app.screen.refresh_all,order_id=order)
    editor.cart_table.tree.selection_set(str(coffee))
    editor.quantity_var.set('abc')
    editor.update_item()
    assert editor.error_label.cget('text')
    editor.quantity_var.set('2')
    editor.update_item()
    assert editor.cart[coffee]['SoLuong']==2
    shot(editor,'goi_mon')
    editor.destroy()
    record('Giỏ hàng và số lượng sai','Từ chối chữ, giỏ hợp lệ có tổng 80.000 đồng')
    payment=PaymentDialog(app,manager,order,app.screen.refresh_all)
    payment.received.set('50000')
    assert payment.confirm_button.instate(['disabled'])
    payment.received.set('100000')
    assert payment.change_amount()==Decimal(20000)
    shot(payment,'thanh_toan')
    payment.confirm()
    saved,_=manager.get_order(order)
    assert saved['TrangThai']==PAID and saved['DiemDaCong']==8
    record('Thanh toán thật','Tổng 80.000, nhận 100.000, thừa 20.000, cộng 8 điểm')
    cancelled=manager.save_order(tables[1]['MaBan'],None,[(milk,1)])
    manager.finish_order(cancelled,pay=False)
    assert manager.get_order(cancelled)[0]['TrangThai']==CANCELLED
    manager.delete_order(cancelled)
    record('Huỷ và xoá đơn chưa thanh toán','Đúng trạng thái, bàn trống, không tạo doanh thu')
    app.screen.show_page('statistics')
    stats=app.screen.pages['statistics']
    stats.quick_period('week')
    shot(app,'bao_cao_doanh_thu')
    deadline=time.monotonic()+360
    app.after(1200,stats.export)
    app.after(1500,complete)
    print('DIALOG_READY',flush=True)
    app.mainloop()
finally:
    if app is not None:
        try:app.destroy()
        except Exception:pass
    if not re.fullmatch(r'CoffeeTest_[0-9a-f]{32}',database) or database==original:
        raise RuntimeError('Tên database kiểm tra không hợp lệ')
    connection=db_connection.connect('master',autocommit=True)
    try:
        if connection.execute('SELECT 1 FROM sys.databases WHERE name = ?',database).fetchone():
            connection.execute(f'ALTER DATABASE [{database}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE')
            connection.execute(f'DROP DATABASE [{database}]')
    finally:
        connection.close()
        db_connection.DATABASE=original
    print('Đã xoá cơ sở dữ liệu trình diễn.',flush=True)
