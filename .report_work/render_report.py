import os, importlib.util
from pathlib import Path
from pypdf import PdfReader
from zipfile import ZipFile
from lxml import etree
work=Path(__file__).parent
os.environ['PATH']='C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin'+os.pathsep+os.environ['PATH']
os.environ['TEMP']=str(work)
os.environ['TMP']=str(work)
path='C:/Users/PC/.codex/plugins/cache/openai-primary-runtime/documents/26.905.11957/skills/documents/render_docx.py'
spec=importlib.util.spec_from_file_location('renderer',path)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.convert_to_pdf=lambda *args,**kwargs:(str(work/'report.pdf'),'Microsoft Word PDF export')
pages=m.rasterize(str(work.parent/'docs/BaoCao_QuanLyQuanCaPhe.docx'),str(work/'render'),120,False,False)
pdf=PdfReader(work/'report.pdf')
for i,page in enumerate(pdf.pages,1):
    txt=page.extract_text()
    (work/f'page-{i}.txt').write_text(txt,encoding='utf-8')
    print(i,len(txt),repr(txt[:140]),repr(txt[-110:]))
with ZipFile(work.parent/'docs/BaoCao_QuanLyQuanCaPhe.docx') as z:
    xml=etree.fromstring(z.read('word/document.xml'))
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    print('TOC links',len(xml.xpath('//w:hyperlink[@w:anchor]',namespaces=ns)))
    print('Fields',xml.xpath('//w:instrText/text()',namespaces=ns)[:5])
    text=''.join(xml.xpath('//w:t/text()',namespaces=ns))
    assert ';' not in text
    assert 'DH23TIN02' in text and '236717' in text
