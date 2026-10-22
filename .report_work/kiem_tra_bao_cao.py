import os,sys,importlib.util,re,json
from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from pypdf import PdfReader
sys.stdout.reconfigure(encoding='utf-8')
W=Path(__file__).parent
ROOT=W.parent
os.environ['PATH']='C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin'+os.pathsep+os.environ['PATH']
os.environ['TEMP']=str(W)
os.environ['TMP']=str(W)
spec=importlib.util.spec_from_file_location('render_docx','C:/Users/PC/.codex/plugins/cache/openai-primary-runtime/documents/26.1015.12040/skills/documents/render_docx.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.convert_to_pdf=lambda *args,**kwargs:(str(W/'report.pdf'),'Microsoft Word PDF export')
pages=module.rasterize(str(ROOT/'docs/BaoCao_QuanLyQuanCaPhe.docx'),str(ROOT/'sodo'),120,False,False)
reader=PdfReader(W/'report.pdf')
for i,page in enumerate(reader.pages,1):
    text=page.extract_text()
    (W/f'page-{i}.txt').write_text(text,encoding='utf-8')
    print(i,len(text),repr(text[:80]),repr(text[-90:]))
with ZipFile(ROOT/'docs/BaoCao_QuanLyQuanCaPhe.docx') as z:
    xml=etree.fromstring(z.read('word/document.xml'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
text=''.join(xml.xpath('//w:t/text()',namespaces=ns))
assert ';' not in text
assert not re.search(r'\b(?:CN\d+|BS\d+|G\.\d+|TODO|TBD|PLACEHOLDER)\b',text)
assert not any(c in text for c in ['\u200b','\ufffd','\u200d','\u200e','\u200f'])
table_nodes=xml.xpath('//w:tbl',namespaces=ns)
for t in table_nodes:
    for side in ['top','left','bottom','right','insideH','insideV']:
        assert t.xpath(f'./w:tblPr/w:tblBorders/w:{side}[@w:val="single"]',namespaces=ns)
    for row in t.xpath('./w:tr',namespaces=ns):
        assert row.xpath('./w:trPr/w:cantSplit',namespaces=ns)
    assert t.xpath('./w:tr[1]/w:trPr/w:tblHeader',namespaces=ns)
caps=[]
for pp in xml.xpath('//w:body/w:p',namespaces=ns):
    if pp.xpath('./w:pPr/w:pStyle[@w:val="Caption"]',namespaces=ns):
        caps.append(''.join(pp.xpath('.//w:t/text()',namespaces=ns)))
inventory=json.loads((W/'inventory.json').read_text(encoding='utf-8'))
for label,kind in [('Hình','figures'),('Bảng','tables')]:
    found=[c for c in caps if c.startswith(label)]
    expected=[f'{label} {c["number"]} {c["title"]}' for c in inventory[kind]]
    assert found==expected,(found,expected)
links=xml.xpath('//w:hyperlink[@w:anchor]',namespaces=ns)
fields=xml.xpath('//w:instrText/text()',namespaces=ns)
assert len(links)>=40,len(links)
assert len(table_nodes)==15
assert len(caps)==27
assert sum('TOC ' in f for f in fields)==3
assert sum('SEQ Figure' in f for f in fields)==12
assert sum('SEQ Table' in f for f in fields)==15
assert len(reader.pages)<=60
print('AUDIT OK',len(reader.pages),'pages',len(table_nodes),'tables',len(caps),'captions',len(links),'internal links')
(W/'audit.json').write_text(json.dumps({'pages':len(reader.pages),'tables':len(table_nodes),'figures':12,'captions':len(caps),'internal_links':len(links)},ensure_ascii=False),encoding='utf-8')
