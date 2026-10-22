from pathlib import Path
import ast
import textwrap

ROOT=Path(__file__).resolve().parent.parent

def replace_transactions(source):
    tree=ast.parse(source)
    lines=source.splitlines(keepends=True)
    targets=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.With) and len(node.items)==1:
            expr=node.items[0].context_expr
            if isinstance(expr,ast.Call) and isinstance(expr.func,ast.Name) and expr.func.id=='transaction':
                targets.append(node)
    for node in sorted(targets,key=lambda x:x.lineno,reverse=True):
        indent=' '*node.col_offset
        body=lines[node.lineno:node.end_lineno]
        returns=[]
        for statement in node.body:
            for child in ast.walk(statement):
                if isinstance(child,ast.Return):
                    returns.append(child)
        for ret in sorted(returns,key=lambda x:x.lineno,reverse=True):
            gap=' '*ret.col_offset
            if ret.value is None:
                replacement=gap+'connection.commit()\n'+gap+'return\n'
            else:
                expression=ast.get_source_segment(source,ret.value)
                replacement=gap+'result_to_return = ('+expression+')\n'+gap+'connection.commit()\n'+gap+'return result_to_return\n'
            start=ret.lineno-node.lineno-1
            end=ret.end_lineno-node.lineno
            body[start:end]=[replacement]
        replacement=indent+'connection = connect()\n'+indent+'try:\n'
        replacement+=indent+'    connection.execute("SET XACT_ABORT ON")\n'
        replacement+=indent+'    cursor = connection.cursor()\n'+''.join(body)
        if not isinstance(node.body[-1],ast.Return):
            replacement+=indent+'    connection.commit()\n'
        replacement+=indent+'except Exception:\n'+indent+'    connection.rollback()\n'+indent+'    raise\n'
        replacement+=indent+'finally:\n'+indent+'    connection.close()\n'
        lines[node.lineno-1:node.end_lineno]=[replacement]
    return ''.join(lines)

for path in [ROOT/'models/service.py',ROOT/'database_setup.py',ROOT/'tests/test_coffee.py']:
    source=replace_transactions(path.read_text(encoding='utf-8'))
    source=source.replace('from db_connection import rows, transaction','from db_connection import rows, connect')
    source=source.replace('from db_connection import connect, database_name, transaction','from db_connection import connect, database_name')
    source=source.replace('from db_connection import transaction','from db_connection import connect')
    path.write_text(source,encoding='utf-8')

path=ROOT/'models/service.py'
source=path.read_text(encoding='utf-8')
start=source.index('    @classmethod\n    def login')
end=source.index('    def _authorize',start)
login=textwrap.dedent(source[start:end]).replace('@classmethod\n','').replace('def login(cls, username, password):','def login(username, password):').replace('return cls(', 'return CoffeeService(').replace('result_to_return = (cls(', 'result_to_return = (CoffeeService(')
source=source[:start]+source[end:]
source=source.replace('class CoffeeService:',login+'\nclass CoffeeService:')
source=source.replace('    @staticmethod\n','')
for name in ['_pending_order','_sync_table','_ensure_other_manager']:
    source=source.replace('def '+name+'(cursor,','def '+name+'(self, cursor,')
path.write_text(source,encoding='utf-8')

path=ROOT/'tests/test_coffee.py'
source=path.read_text(encoding='utf-8')
tree=ast.parse(source)
test_class=next(n for n in tree.body if isinstance(n,ast.ClassDef))
lines=source.splitlines(keepends=True)
functions=[]
for name in ['setUpClass','cleanup_database']:
    node=next(n for n in test_class.body if isinstance(n,ast.FunctionDef) and n.name==name)
    first=node.decorator_list[0].lineno
    chunk=textwrap.dedent(''.join(lines[first-1:node.end_lineno]))
    chunk=chunk.replace('@classmethod\n','').replace('def setUpClass(cls):','def setUpModule():').replace('def cleanup_database(cls):','def cleanup_database():')
    chunk=chunk.replace('cls.addClassCleanup(cls.cleanup_database)','unittest.addModuleCleanup(cleanup_database)')
    chunk=chunk.replace('cls.','CoffeeTests.')
    functions.append(chunk)
for node in sorted([n for n in test_class.body if isinstance(n,ast.FunctionDef) and n.name in ['setUpClass','cleanup_database']],key=lambda x:x.lineno,reverse=True):
    first=node.decorator_list[0].lineno
    lines[first-1:node.end_lineno]=[]
source=''.join(lines)
source=source.replace('class CoffeeTests(unittest.TestCase):','\n\n'.join(functions)+'\n\n\nclass CoffeeTests(unittest.TestCase):')
path.write_text(source,encoding='utf-8')

for path in list((ROOT/'ui').glob('*.py'))+[ROOT/'tests/test_coffee.py']:
    source=path.read_text(encoding='utf-8')
    if 'CoffeeService.login(' in source:
        source=source.replace('CoffeeService.login(','login(')
        source=source.replace('from models.service import ', 'from models.service import login, ',1)
    if path.name=='common.py':
        source=source.replace('import functools\n','')
        start=source.index('def guarded(')
        end=source.index('def center_window(',start)
        source=source[:start]+source[end:]
    if '    @staticmethod\n' in source:
        source=source.replace('    @staticmethod\n','').replace('def format_status(key, value):','def format_status(self, key, value):')
    tree=ast.parse(source)
    lines=source.splitlines(keepends=True)
    methods=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.FunctionDef) and any(isinstance(d,ast.Name) and d.id=='guarded' for d in node.decorator_list):
            methods.append(node)
    for node in sorted(methods,key=lambda x:x.lineno,reverse=True):
        first=node.decorator_list[0].lineno
        body=lines[node.lineno:node.end_lineno]
        replacement=lines[node.lineno-1]+'        try:\n'
        for line in body:
            replacement+=('    '+line if line.strip() else line)
        replacement+='        except Exception as error:\n            report_error(self, error)\n'
        lines[first-1:node.end_lineno]=[replacement]
    source=''.join(lines).replace(', guarded,',', report_error,').replace(', guarded\n',', report_error\n')
    # Các nhãn thao tác chỉ dùng chữ, giữ nguyên lệnh được gọi.
    for old,new in [('＋ ',''),('↻ ',''),('✓  ',''),('✓ ',''),('✕ ',''),('← ',''),('→ ',''),(' →',''),(' • ',' - '),(' · ',' - '),(' — ',' - '),('…','...'),('−','-')]:
        source=source.replace(old,new)
    source=source.replace('show="●"','show="*"').replace('else "●"','else "*"')
    path.write_text(source,encoding='utf-8')

for path in [ROOT/'main.py',ROOT/'security.py']:
    source=path.read_text(encoding='utf-8')
    ast.parse(source)
for path in [ROOT/'models/service.py',ROOT/'database_setup.py',ROOT/'tests/test_coffee.py']+list((ROOT/'ui').glob('*.py')):
    tree=ast.parse(path.read_text(encoding='utf-8'))
    assert not any(isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.decorator_list for n in ast.walk(tree)),path
print('Đã chuyển giao dịch và xử lý sự kiện sang try/except/finally, không còn decorator.')
