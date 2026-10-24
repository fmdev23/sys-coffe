"""Chỉ truy vấn trạng thái, không xóa database trong bước xác nhận cuối."""
import sys,json,re
from pathlib import Path
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification'
sys.path.insert(0,str(ROOT));sys.dont_write_bytecode=True
import db_connection
names=[]
run=json.loads((OUT/'unittest_moi.json').read_text(encoding='utf-8'))
names.extend(run['database_created_observed'])
for filename in ['bo_sung_lan_dau_chua_hoan_tat.json','bo_sung_lan_hai_chua_hoan_tat.json','bo_sung_tien_do.json']:
    names.append(json.loads((OUT/filename).read_text(encoding='utf-8'))['database'])
assert len(set(names))==4 and all(re.fullmatch(r'CoffeeTest_[0-9a-f]{32}',n) for n in names)
c=db_connection.connect('master',autocommit=True)
try:
    present=[r[0] for r in c.execute("SELECT name FROM sys.databases WHERE name LIKE N'CoffeeTest[_]%'").fetchall()]
    original_present=bool(c.execute('SELECT 1 FROM sys.databases WHERE name=?',db_connection.DATABASE).fetchone())
finally:c.close()
result={'time':datetime.now(timezone(timedelta(hours=7))).isoformat(timespec='seconds'),
    'read_only_query':True,'owned_test_databases':names,'all_test_databases_still_present':present,
    'owned_test_databases_still_present':[n for n in names if n in present],
    'all_owned_test_databases_absent':not any(n in present for n in names),
    'original_database_still_present':original_present,'database_deleted_by_this_script':False}
assert result['all_owned_test_databases_absent'] and original_present
(OUT/'cleanup_cuoi.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Verified: four owned test databases absent, original database still present. Read-only query.')
