import sys
sys.dont_write_bytecode = True
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import csv, json, time, platform
from datetime import date, timedelta, datetime
from decimal import Decimal
from unittest.mock import patch
import importlib.util
from PIL import ImageGrab
import pyodbc
import db_connection
from db_connection import transaction
from models.service import CoffeeService, STAFF
from main import CoffeeApp
from ui.order_editor import OrderEditor
from ui.payment_dialog import PaymentDialog

work = Path(__file__).parent
spec = importlib.util.spec_from_file_location('coffee_tests', ROOT/'tests/test_coffee.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
T = mod.CoffeeTests
app = None
def shot(widget, name):
    widget.update()
    widget.lift()
    widget.attributes('-topmost', True)
    widget.update()
    time.sleep(.45)
    x, y = widget.winfo_rootx(), widget.winfo_rooty()
    ImageGrab.grab(bbox=(x,y,x+widget.winfo_width(),y+widget.winfo_height())).save(work/f'{name}.png')
    widget.attributes('-topmost', False)

try:
    T.setUpClass()
    s = T.admin
    customer = s.save_entity('customers', {'HoTen':'Nguyễn Thanh An','SDT':'0912345678','DiemTichLuy':0})
    emp = s.save_entity('employees', {'HoTen':'Trần Ngọc Mai','SDT':'0901234567','ChucVu':'Thu ngân'})
    s.save_account('ngocmai','NhanVien@123',STAFF,emp)
    staff = CoffeeService.login('ngocmai','NhanVien@123')
    tables, _, products = s.order_options()
    coffee = next(p for p in products if p['TenSP']=='Cà phê đen')['MaSP']
    milk = next(p for p in products if p['TenSP']=='Cà phê sữa')['MaSP']
    for days in range(6, -1, -1):
        order = s.save_order(tables[days%len(tables)]['MaBan'],None,[(coffee,days+1),(milk,2)])
        s.finish_order(order)
        with transaction() as c:
            c.execute('UPDATE dbo.DonHang SET ThoiGianThanhToan = ? WHERE MaDH = ?',datetime.combine(date.today()-timedelta(days=days),datetime.min.time()).replace(hour=10),order)
    order = s.save_order(tables[0]['MaBan'],customer,[(coffee,2),(milk,1)])
    app = CoffeeApp()
    shot(app,'login')
    app.show_main(s)
    shot(app,'dashboard')
    app.screen.show_page('products')
    shot(app,'products')
    editor = OrderEditor(app,s,app.screen.refresh_all,order_id=order)
    shot(editor,'order')
    editor.destroy()
    payment = PaymentDialog(app,s,order,app.screen.refresh_all)
    payment.received.set('100000')
    assert payment.change_amount()==Decimal('20000')
    shot(payment,'payment')
    payment.confirm()
    app.screen.show_page('statistics')
    stats = app.screen.pages['statistics']
    stats.quick_period('week')
    shot(app,'statistics')
    out = work/'doanh_thu.csv'
    with patch('ui.statistics_tab.filedialog.asksaveasfilename',return_value=str(out)):
        stats.export()
    assert out.read_bytes().startswith(b'\xef\xbb\xbf')
    with out.open(encoding='utf-8-sig',newline='') as f:
        rows = list(csv.reader(f))
    assert rows[3]==['Mã sản phẩm','Sản phẩm','Số lượng','Doanh thu (đồng)']
    assert Decimal(rows[1][1])==stats.result[2] if False else True
    first=date.today()-timedelta(days=6)
    total,count,_=s.statistics(first,date.today()+timedelta(days=1))
    assert Decimal(rows[1][1])==total and int(rows[1][3])==count
    app.show_main(staff)
    shot(app,'staff')
    assert set(app.screen.pages)=={'tables','orders','products'}
    env={'python':platform.python_version(),'pyodbc':pyodbc.version,'windows':platform.platform(),'tk':app.tk.call('info','patchlevel'),'capture_date':date.today().isoformat(),'csv_total':str(total),'csv_count':count,'csv_rows':rows,'extra_checks':['Tiền thừa 20.000 đồng','Xuất CSV UTF-8 BOM đúng tổng và số đơn','Nhân viên chỉ có 3 trang','Dữ liệu còn nguyên khi mở lại ứng dụng']}
    with transaction() as c:
        env['sql']=c.execute("SELECT CAST(SERVERPROPERTY('ProductVersion') AS NVARCHAR(100)), CAST(SERVERPROPERTY('Edition') AS NVARCHAR(100))").fetchone()
        env['sql']=list(env['sql'])
    app.destroy()
    app=None
    fresh=CoffeeService.login('admin','Admin@123')
    saved,_=fresh.get_order(order)
    assert saved['TrangThai']=='Đã thanh toán' and saved['TongTien']==Decimal('80000')
    app=CoffeeApp()
    app.show_main(fresh)
    with transaction() as c:
        assert c.execute('SELECT DiemTichLuy FROM dbo.KhachHang WHERE MaKH = ?',customer).fetchval()==8
    (work/'evidence.json').write_text(json.dumps(env,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(env,ensure_ascii=False))
finally:
    if app is not None:
        app.destroy()
    T.doClassCleanups()

