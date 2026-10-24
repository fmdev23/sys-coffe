import sys,os,importlib.util,json
from pathlib import Path
from pypdf import PdfReader
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[1]
out=root/'verification'
os.environ['PATH']='C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin'+os.pathsep+os.environ['PATH']
os.environ['TEMP']=os.environ['TMP']=str(out)
renderer='C:/Users/PC/.codex/plugins/cache/openai-primary-runtime/documents/26.1015.12040/skills/documents/render_docx.py'
spec=importlib.util.spec_from_file_location('renderer',renderer)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.convert_to_pdf=lambda *args,**kwargs:(str(out/'bao_cao_kiem_tra.pdf'),'Microsoft Word native PDF export, already updated fields')
candidate=root/'docs/BaoCao_QuanLyQuanCaPhe_DRAFT.docx'
if not candidate.exists():candidate=root/'docs/BaoCao_QuanLyQuanCaPhe_FINAL.docx'
pages=module.rasterize(str(candidate),str(out/'trang_bao_cao'),120,False,False)
pdf=PdfReader(out/'bao_cao_kiem_tra.pdf')
text=[]
for i,page in enumerate(pdf.pages,1):
    value=page.extract_text();text.append({'physical_page':i,'text':value})
    print(i,len(value),repr(value[:100]),repr(value[-90:]))
(out/'trang_bao_cao.json').write_text(json.dumps(text,ensure_ascii=False,indent=2),encoding='utf-8')
print('Đã render',len(pages),'trang qua render_docx.py')
