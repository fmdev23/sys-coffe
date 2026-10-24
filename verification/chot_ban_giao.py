"""Lưu xác nhận xem trang, chốt tên tệp sau nghiệm thu và tạo manifest."""
import sys,json,hashlib,subprocess,ast
from pathlib import Path
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification'
zone=timezone(timedelta(hours=7));now=lambda:datetime.now(zone).isoformat(timespec='seconds')
sys.stdout.reconfigure(encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mode=sys.argv[1]
if mode=='visual':
    images=OUT/'trang_bao_cao'
    baseline=json.loads((OUT/'anh_qa_da_xem.json').read_text(encoding='utf-8'))
    changed=[int(i) for i,h in baseline.items() if sha(images/f'page-{i}.png')!=h]
    assert changed==[5,15]
    record={'time':now(),'method':'Word xuất PDF, render_docx.py 120 DPI, mở từng trang bằng view_image',
        'all_final_pages_reviewed':True,
        'notes':'Đã xem trang 1–24 trước sửa thuật ngữ. SHA ảnh xác nhận chỉ trang 5 và 15 thay đổi, đã mở lại cả hai. Đã mở trang 25–34 sau lần sửa cuối. Không thấy mất ảnh, méo hình, tách hàng, cắt chữ hoặc đoạn tràn sang trang riêng. DFD gốc chữ nhỏ, giữ nguyên và chép nhãn ở Bảng 2.',
        'pages':[{'number':i,'path':str(images/f'page-{i}.png'),'sha256':sha(images/f'page-{i}.png'),'visually_reviewed':True} for i in range(1,35)]}
    (OUT/'xem_trang.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    # Chỉ bỏ năm ảnh QA thừa do chính vòng này render trước khi sửa phân trang.
    assert images.resolve().is_relative_to(OUT.resolve())
    for i in range(35,40):
        old=images/f'page-{i}.png'
        if old.exists():old.unlink()
    print('Đã lưu xác nhận xem đủ 34 trang. Chỉ dọn ảnh QA 35–39 do vòng này tạo, không đụng ảnh nguồn.')
elif mode=='promote':
    gate=json.loads((OUT/'nghiem_thu.json').read_text(encoding='utf-8'))
    assert gate['conclusion']=='SẴN SÀNG NỘP' and not gate['blockers']
    draft=ROOT/'docs/BaoCao_QuanLyQuanCaPhe_DRAFT.docx';final=ROOT/'docs/BaoCao_QuanLyQuanCaPhe_FINAL.docx'
    assert draft.exists() and not final.exists() and draft.parent==final.parent
    value=sha(draft);draft.rename(final);assert sha(final)==value
    print('Đã chốt tên:',final)
elif mode=='syntax':
    paths=[ROOT/f['path'] for f in json.loads((OUT/'ma_nguon.json').read_text(encoding='utf-8'))]
    paths+=sorted(OUT.glob('*.py'))
    for p in paths:ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
    result={'time':now(),'python':sys.version.split()[0],'executable':sys.executable,'exit_code':0,'app_and_tests':21,'verification_helpers':len(paths)-21,'files':[p.relative_to(ROOT).as_posix() for p in paths],'method':'ast.parse, no imports or bytecode'}
    (OUT/'cu_phap_python_thuc.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('AST OK:',len(paths),'files with Python',sys.version.split()[0])
elif mode=='manifest':
    final=ROOT/'docs/BaoCao_QuanLyQuanCaPhe_FINAL.docx';assert final.exists()
    paths=[final]+sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='manifest.json')
    result={'generated_at':now(),'timezone':'UTC+7','branch':'main','commit':'7af74062bae32226ce0f14c11df0c60af213eab0',
        'manifest_self_hash_excluded':True,'files':[{'path':p.relative_to(ROOT).as_posix(),'modified_at':datetime.fromtimestamp(p.stat().st_mtime,zone).isoformat(timespec='seconds'),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]}
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Manifest:',len(paths),'tệp. SHA-256 báo cáo:',sha(final))
else:raise ValueError(mode)
