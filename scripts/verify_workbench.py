"""Run the complete local test, replay and archive acceptance sequence.

Artifacts contain GM fixtures and stay in a new directory outside the repository.
"""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sqlite3
import sys
import time
import campaign_archive
import dice_archive
import dice_local
import session

ROOT=Path(__file__).resolve().parents[1]
REPLAYS=('action','combat','exploration','investigation','campaign','keeper')


def run(output,timeout=180):
    output=Path(output).resolve()
    if output.is_relative_to(ROOT):raise ValueError('Verification output must be outside the repository')
    output.mkdir(parents=True,exist_ok=False)
    report={'started_utc':datetime.now(timezone.utc).isoformat(),'passed':False,'checks':[],
            'scope':'Executed tests, scripted replays and archive roundtrips; not full rules or live-player certification'}
    def save():
        (output/'report.json').write_text(session.encode(report)+'\n',encoding='utf-8')
    def command(name,args):
        start=time.monotonic();item={'name':name,'passed':False}
        try:
            result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
            (output/(name+'.stdout.txt')).write_text(result.stdout,encoding='utf-8')
            (output/(name+'.stderr.txt')).write_text(result.stderr,encoding='utf-8')
            item.update(passed=result.returncode==0,exit_code=result.returncode)
        except (OSError,subprocess.TimeoutExpired) as exc:
            item['error']=type(exc).__name__
        item['seconds']=round(time.monotonic()-start,3);report['checks'].append(item);save()
        print(session.encode(item),flush=True)
    save()
    python=[sys.executable,'-X','utf8']
    command('tests',python+['-m','unittest','discover','-s','scripts','-q'])
    command('capabilities',python+['scripts/capabilities.py','--check'])
    for name in REPLAYS:
        filename='replay_acceptance.py' if name=='campaign' else f'replay_{name}_acceptance.py'
        command('replay-'+name,python+['scripts/'+filename,'--output',str(output/name)])
    archives=[]
    # Snapshot the file list first: backups must not recursively back up themselves.
    paths=sorted(output.rglob('*.sqlite'))
    for index,path in enumerate(paths):
        item={'database':str(path.relative_to(output)),'passed':False}
        try:
            db=campaign_archive.connect_readonly(path)
            try:
                tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                columns=[r[1] for r in db.execute('PRAGMA table_info(requests)')]
            finally:db.close()
            if 'events' in tables:validator=campaign_archive;dialect='campaign'
            elif 'tables' in tables and columns==['scope','operation','request','response']:validator=dice_archive;dialect='dice-local'
            else:raise ValueError('Unsupported acceptance database dialect')
            target=output/'backups'/f'{index}.sqlite'
            result=validator.backup(path,target)
            validator.check(target,result['file_sha256'])
            if dialect=='campaign':
                if session.view(path,gm=True)!=session.view(target,gm=True):raise ValueError('Campaign state differs after backup')
            else:
                db=campaign_archive.connect_readonly(path)
                try:scopes=[row[0] for row in db.execute('SELECT scope FROM tables')]
                finally:db.close()
                if any(dice_local.read(path,scope)!=dice_local.read(target,scope) for scope in scopes):raise ValueError('Dice state differs after backup')
            item.update(passed=True,dialect=dialect,file_sha256=result['file_sha256'])
        except (ValueError,KeyError,TypeError,OSError,sqlite3.Error) as exc:
            item['error']=type(exc).__name__
        archives.append(item)
    report['archives']=archives
    report['passed']=all(c['passed'] for c in report['checks']) and bool(archives) and all(a['passed'] for a in archives)
    report['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(session.encode({'passed':report['passed'],'checks':len(report['checks']),'archive_roundtrips':len(archives)}),flush=True)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:raise SystemExit(0 if run(args.output)['passed'] else 1)
    except (ValueError,OSError) as exc:
        print(session.encode({'error':str(exc)}),file=sys.stderr);raise SystemExit(2)
