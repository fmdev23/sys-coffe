"""Kiểm tra bổ sung trên database riêng, không sửa dữ liệu vận hành."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import csv,json,re,uuid,hashlib,time,traceback
from datetime import date,datetime,timedelta,timezone
from decimal import Decimal
from unittest.mock import patch
import db_connection,database_setup
from models.service import login,AppError,STAFF,PAID,CANCELLED
from main import CoffeeApp
from ui.payment_dialog import PaymentDialog

OUT=ROOT/'verification'
sys.stdout.reconfigure(encoding='utf-8')
zone=timezone(timedelta(hours=7))
original=db_connection.DATABASE
own='CoffeeTest_'+uuid.uuid4().hex
events=[]
app=None
master=db_connection.connect('master',autocommit=True)
assert not master.execute('SELECT 1 FROM sys.databases WHERE name=?',own).fetchone()
master.close()

def record(action,result):
    events.append({'time':datetime.now(zone).isoformat(timespec='seconds'),'action':action,'result':result})
    print(action+': '+str(result),flush=True)
    (OUT/'bo_sung_tien_do.json').write_text(json.dumps({'database':own,'events':events},ensure_ascii=False,indent=2),encoding='utf-8')

def sql(statement,*parameters):
    c=db_connection.connect()
    try:
        rows=c.execute(statement,*parameters).fetchall()
        return [list(r) for r in rows]
    finally:c.close()

def historical():
    paths=[ROOT/'docs/doanh_thu_kiem_tra.csv',ROOT.parent/'SoLieuCSVProject/doanh_thu_2026-10-14.csv']
    checked=[]
    for path in paths:
        if not path.exists():continue
        raw=path.read_bytes()
        rows=list(csv.reader(raw.decode('utf-8-sig').splitlines()))
        assert raw.startswith(b'\xef\xbb\xbf')
        assert rows[0]==['Từ ngày','2026-10-14','Đến ngày','2026-10-20']
        assert Decimal(rows[1][1])==1200000 and int(rows[1][3])==8
        assert rows[4][1:3]==['Cà phê đen','30'] and Decimal(rows[4][3])==750000
        assert rows[5][1:3]==['Cà phê sữa','15'] and Decimal(rows[5][3])==450000
        assert sum(Decimal(r[3]) for r in rows[4:])==Decimal(rows[1][1])
        checked.append({'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'rows':rows,'bom':True})
    assert checked
    (OUT/'csv_lich_su.json').write_text(json.dumps({'checked_at':datetime.now(zone).isoformat(),'files':checked,
        'scope':'Đọc lại chứng cứ lịch sử, không tái xác nhận database trình diễn ngày 20/10/2026.'},ensure_ascii=False,indent=2),encoding='utf-8')
    record('Đọc CSV lịch sử','Đúng kỳ 14–20/10/2026, 8 đơn, 1.200.000 đồng, 30 ly đen và 15 ly sữa')

try:
    historical()
    db_connection.DATABASE=own
    database_setup.setup()
    record('Cách ly dữ liệu','Đã tạo '+own+', không dùng '+original)
    admin=login('admin','Admin@123')
    products=admin.list_entities('products')
    coffee=next(p['MaSP'] for p in products if p['TenSP']=='Cà phê đen')
    milk=next(p['MaSP'] for p in products if p['TenSP']=='Cà phê sữa')
    table=admin.list_entities('tables')[0]['MaBan']
    customer=admin.save_entity('customers',{'HoTen':'Khách kiểm định','SDT':'','DiemTichLuy':0})
    order=admin.save_order(table,customer,[(coffee,2),(milk,1)])
    saved,lines=admin.get_order(order)
    assert saved['TongTien']==Decimal(80000)
    record('Lưu đơn mới','2 × 25.000 + 1 × 30.000 = 80.000 đồng')
    app=CoffeeApp()
    app.show_main(admin)
    app.update()
    assert len(app.screen.pages)==8
    payment=PaymentDialog(app.screen,admin,order,app.screen.refresh_all)
    for invalid in ['', 'abc','-1','1,5','１０００００','9'*16]:
        payment.received.set(invalid)
        assert payment.confirm_button.instate(['disabled'])
    payment.received.set('50000')
    assert payment.confirm_button.instate(['disabled'])
    payment.received.set('100000')
    assert payment.change_amount()==Decimal(20000)
    assert payment.confirm_button.instate(['!disabled'])
    record('PaymentDialog','Từ chối dữ liệu sai/thiếu, tiền nhận 100.000 thì thừa 20.000 đồng')
    payment.withdraw()
    app.withdraw()
    def finish():
        saved,_=admin.get_order(order)
        points=sql('SELECT DiemTichLuy FROM dbo.KhachHang WHERE MaKH=?',customer)[0][0]
        assert saved['TrangThai']==PAID and points==8
        assert sql('SELECT TrangThai FROM dbo.Ban WHERE MaBan=?',table)[0][0]=='Trống'
        record('Thanh toán','Đơn đã thanh toán 80.000 đồng, 8 điểm và bàn Trống')
        cancelled=admin.save_order(table,None,[(milk,1)])
        admin.finish_order(cancelled,pay=False)
        assert admin.get_order(cancelled)[0]['TrangThai']==CANCELLED
        admin.delete_order(cancelled)
        record('Hủy và xóa','Đơn hủy bị loại khỏi doanh thu và xóa được theo quyền quản lý')
        for i in range(11):
            product=admin.save_entity('products',{'TenSP':f'Món kiểm định {i+1}','DanhMuc':'Kiểm định','Gia':10000+i*1000,'MoTa':'','TrangThai':1})
            oid=admin.save_order(table,None,[(product,1)])
            admin.finish_order(oid)
        # Dùng ngày thanh toán đo được trên SQL, không giả định múi giờ máy chủ.
        first=sql('SELECT CAST(MIN(ThoiGianThanhToan) AS DATE) FROM dbo.DonHang WHERE TrangThai=?',PAID)[0][0]
        until=sql('SELECT CAST(MAX(ThoiGianThanhToan) AS DATE) FROM dbo.DonHang WHERE TrangThai=?',PAID)[0][0]+timedelta(days=1)
        total,count,top=admin.statistics(first,until)
        distinct=sql('SELECT COUNT(DISTINCT ct.MaSP) FROM dbo.ChiTietDonHang ct JOIN dbo.DonHang d ON d.MaDH=ct.MaDH WHERE d.TrangThai=?',PAID)[0][0]
        assert distinct==13 and len(top)==10 and count==12
        top_total=sum(r['DoanhThu'] for r in top)
        assert top_total<total
        record('Giới hạn TOP 10',{'so_mon_da_ban':distinct,'so_mon_tra_ve':len(top),'so_don':count,'tong_toan_ky':str(total),'tong_10_mon':str(top_total)})
        stats=app.screen.pages['statistics']
        app.screen.show_page('statistics')
        stats.start.set(first.isoformat())
        stats.end.set((until-timedelta(days=1)).isoformat())
        stats.refresh()
        app.update()
        record('Cách chọn đường dẫn CSV','Tự động cung cấp đường dẫn cho filedialog, không kiểm tra thao tác chọn tệp bằng chuột. Truy vấn SQL và ghi CSV chạy thật, không thay thế.')
        exported=OUT/'doanh_thu_kiem_dinh_moi.csv'
        assert not exported.exists(), 'Không ghi đè bằng chứng CSV đã có'
        with patch('ui.statistics_tab.filedialog.asksaveasfilename',return_value=str(exported)):
            stats.export()
        rows=list(csv.reader(exported.read_text(encoding='utf-8-sig').splitlines()))
        assert exported.read_bytes().startswith(b'\xef\xbb\xbf')
        assert Decimal(rows[1][1])==total and int(rows[1][3])==count and len(rows[4:])==10
        record('Xuất CSV mới',{'so_don':count,'tong_toan_ky':str(total),'so_dong_mon':len(rows[4:]),'tong_dong_mon':str(sum(Decimal(r[3]) for r in rows[4:])),'file':exported.name})
        record('Kết quả bổ sung','Hoàn tất các kiểm tra bổ sung. Không có ảnh giao diện mới được xác nhận.')
    payment.confirm()
    finish()
except Exception:
    (OUT/'bo_sung_loi.txt').write_text(traceback.format_exc(),encoding='utf-8')
    raise
finally:
    if app:
        try:app.destroy()
        except Exception:pass
    assert re.fullmatch(r'CoffeeTest_[0-9a-f]{32}',own) and own!=original
    c=db_connection.connect('master',autocommit=True)
    try:
        if c.execute('SELECT 1 FROM sys.databases WHERE name=?',own).fetchone():
            c.execute(f'ALTER DATABASE [{own}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE')
            c.execute(f'DROP DATABASE [{own}]')
        assert not c.execute('SELECT 1 FROM sys.databases WHERE name=?',own).fetchone()
        record('Cleanup kiểm tra bổ sung','Đã xóa đúng database của lần kiểm tra '+own)
    finally:
        c.close()
        db_connection.DATABASE=original
