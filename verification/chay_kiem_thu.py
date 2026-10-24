"""Chạy lệnh kiểm định và lưu chứng cứ, không thay mã hoặc mock SQL."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import ast
import json
import os
import platform
import re
import shutil
import subprocess
import threading
import time
from datetime import datetime, timezone, timedelta

import pyodbc
import tkinter as tk
import db_connection

sys.stdout.reconfigure(encoding='utf-8')
OUT = ROOT / 'verification'
ENV = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1',
           PATH=str(Path(sys.executable).parent)+os.pathsep+os.environ.get('PATH',''))
ZONE = timezone(timedelta(hours=7))

def now():
    return datetime.now(ZONE).isoformat(timespec='seconds')

def save(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

def command(name, args, timeout=120):
    start = now()
    timer = time.perf_counter()
    result = subprocess.run(args, cwd=ROOT, env=ENV, capture_output=True, encoding='utf-8', errors='replace', timeout=timeout)
    # Các phép thử không in mật khẩu. Nếu một lỗi ngoài dự kiến làm lộ hằng mẫu, chỉ ẩn phần đó.
    secrets = set()
    tree = ast.parse((ROOT/'tests/test_coffee.py').read_text(encoding='utf-8'))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and re.search(r'@[0-9]', node.value):
            secrets.add(node.value)
    stdout, stderr = result.stdout, result.stderr
    redacted = 0
    for secret in secrets:
        for value in [stdout, stderr]:
            redacted += value.count(secret)
        stdout, stderr = stdout.replace(secret, '(mật khẩu đã ẩn)'), stderr.replace(secret, '(mật khẩu đã ẩn)')
    (OUT/(name+'.stdout.txt')).write_text(stdout, encoding='utf-8')
    (OUT/(name+'.stderr.txt')).write_text(stderr, encoding='utf-8')
    data = {'command': args, 'started_at': start, 'finished_at': now(), 'duration_wall_seconds': round(time.perf_counter()-timer, 6),
            'exit_code': result.returncode, 'stdout': name+'.stdout.txt', 'stderr': name+'.stderr.txt', 'secret_redactions': redacted}
    save(name+'.json', data)
    print(name, 'exit', result.returncode, 'seconds', data['duration_wall_seconds'], flush=True)
    return data, stdout, stderr

def database_names(connection):
    return [r[0] for r in connection.execute("SELECT name FROM sys.databases WHERE name LIKE 'CoffeeTest[_]%' ORDER BY name")]

if sys.argv[1]=='environment':
    results = []
    for name, args in [('python_version',['python','--version']), ('pyodbc_pip',['python','-m','pip','show','pyodbc'])]:
        results.append(command(name,args)[0])
    code = shutil.which('code')
    if code:
        results.append(command('vscode_version',['cmd.exe','/d','/c',code,'--version'])[0])
    else:
        save('vscode_version.json', {'user_confirmed':'Visual Studio Code', 'version':None, 'reason':'Lệnh code không khả dụng'})
    runtime={'time':now(),'python':platform.python_version(),'executable':sys.executable,'python_path':shutil.which('python'),
             'pyodbc':pyodbc.version,'windows':platform.platform(),'tk':tk.Tcl().call('info','patchlevel'),
             'odbc_drivers':pyodbc.drivers(),'ide_user_confirmed':'Visual Studio Code','commands':results}
    c=db_connection.connect('master',autocommit=True)
    try:
        row=c.execute("SELECT CAST(SERVERPROPERTY('ProductVersion') AS NVARCHAR(100)), CAST(SERVERPROPERTY('Edition') AS NVARCHAR(100)), CONVERT(NVARCHAR(50),SYSDATETIMEOFFSET(),127)").fetchone()
        runtime['sql']={'version':row[0],'edition':row[1],'server_time':str(row[2]),'server':db_connection.SERVER,'authentication':'Windows'}
        runtime['test_databases_before']=database_names(c)
        historical=json.loads((ROOT/'.report_work/evidence_new.json').read_text(encoding='utf-8'))
        runtime['historical_demo_database_present']=bool(c.execute('SELECT 1 FROM sys.databases WHERE name=?',historical['database_test']).fetchone())
    finally:
        c.close()
    c=db_connection.connect(autocommit=True)
    try:
        runtime['configured_database']=db_connection.DATABASE
        runtime['schema_tables']=[r[0] for r in c.execute("SELECT name FROM sys.tables WHERE schema_id=SCHEMA_ID('dbo') ORDER BY name")]
        runtime['filtered_index']=[list(r) for r in c.execute("SELECT name,is_unique,filter_definition FROM sys.indexes WHERE object_id=OBJECT_ID('dbo.DonHang') AND name='UX_Ban_DonDangXuLy'")]
        runtime['order_version_type']=[list(r) for r in c.execute("SELECT c.name,t.name FROM sys.columns c JOIN sys.types t ON c.user_type_id=t.user_type_id WHERE c.object_id=OBJECT_ID('dbo.DonHang') AND c.name='PhienBan'")]
    finally:
        c.close()
    save('moi_truong.json',runtime)
    print(json.dumps(runtime,ensure_ascii=False,indent=2),flush=True)
    command('tkinter_module',['python','-m','tkinter'],timeout=300)
elif sys.argv[1]=='tests':
    c=db_connection.connect('master',autocommit=True)
    before=database_names(c)
    c.close()
    observed=set()
    timeline=[]
    errors=[]
    stop=threading.Event()
    def watch():
        connection=db_connection.connect('master',autocommit=True)
        try:
            last=None
            while not stop.is_set():
                names=database_names(connection)
                observed.update(set(names)-set(before))
                if names!=last:
                    timeline.append({'time':now(),'databases':names})
                    last=names
                stop.wait(.1)
        except Exception as error:
            errors.append(str(error))
        finally:
            connection.close()
    thread=threading.Thread(target=watch)
    thread.start()
    try:
        data,stdout,stderr=command('unittest_moi',['python','-B','-m','unittest','discover','-s','tests','-v'])
    finally:
        stop.set()
        thread.join()
    c=db_connection.connect('master',autocommit=True)
    try:
        after=database_names(c)
    finally:
        c.close()
    combined=stdout+'\n'+stderr
    matched=re.search(r'Ran (\d+) tests? in ([0-9.]+)s',combined)
    statuses=re.findall(r'^(test_\w+) \(([^\n]+)\) \.\.\. (ok|FAIL|ERROR|skipped[^\n]*)$',combined,re.M)
    counts={'passed':sum(s[2]=='ok' for s in statuses),'failures':sum(s[2]=='FAIL' for s in statuses),
            'errors':sum(s[2]=='ERROR' for s in statuses),'skipped':sum(s[2].startswith('skipped') for s in statuses)}
    data.update({'tests_run':int(matched[1]) if matched else None,'duration_unittest_seconds':float(matched[2]) if matched else None,
                 **counts,'test_statuses':[{'method':s[0],'id':s[1],'status':s[2]} for s in statuses],
                 'success_marker':bool(re.search(r'^OK\s*$',combined,re.M)),
                 'database_before':before,'database_created_observed':sorted(observed),'database_after':after,
                 'database_monitor_timeline':timeline,'database_monitor_errors':errors,
                 'own_test_database_cleanup_confirmed':len(observed)==1 and all(re.fullmatch(r'CoffeeTest_[0-9a-f]{32}',n) and n not in after for n in observed)})
    data['confirmed_success']=data['exit_code']==0 and data['tests_run']==19 and counts=={'passed':19,'failures':0,'errors':0,'skipped':0} and data['success_marker'] and data['own_test_database_cleanup_confirmed'] and not errors
    save('unittest_moi.json',data)
    print(json.dumps(data,ensure_ascii=False,indent=2),flush=True)
else:
    raise SystemExit('Chọn environment hoặc tests')
