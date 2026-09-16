"""Backup and structural checks for the current local Dice database dialect."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys
import campaign_archive as archive
import session


def check(path,expected_sha256=None):
    if expected_sha256 is not None:
        if not isinstance(expected_sha256,str) or len(expected_sha256)!=64 or any(c not in '0123456789abcdefABCDEF' for c in expected_sha256):
            raise ValueError('Expected SHA-256 must contain 64 hexadecimal characters')
        if archive.file_digest(path)!=expected_sha256.lower():raise ValueError('Archive file checksum mismatch')
    db=archive.connect_readonly(path)
    try:
        db.execute('BEGIN')
        if db.execute('PRAGMA integrity_check').fetchall()!=[('ok',)]:raise ValueError('SQLite integrity check failed')
        columns=[r[1] for r in db.execute('PRAGMA table_info(requests)')]
        if columns!=['scope','operation','request','response']:raise ValueError('Expected current local Dice dialect; legacy accounts and campaign ledgers are separate')
        scopes={};operations=0
        for scope,raw in db.execute('SELECT scope,state FROM tables'):
            if not isinstance(scope,str) or not scope.strip():raise ValueError('Invalid Dice scope')
            state=json.loads(raw)
            if not isinstance(state,dict):raise ValueError('Invalid Dice state')
            session.integer(state.get('revision'))
            for key in ('players','npcs','monsters','team','initiative','clues','logs','config','decks','custom','scenes','replies','clocks'):
                if not isinstance(state.get(key),dict):raise ValueError('Invalid Dice state container')
            if not isinstance(state.get('observers'),list):raise ValueError('Invalid observer list')
            for player in state['players'].values():
                if not isinstance(player,dict) or not isinstance(player.get('cards'),dict):raise ValueError('Invalid player card store')
                if player.get('active') is not None and player['active'] not in player['cards']:raise ValueError('Active card missing')
            if state.get('active_log') is not None and state['active_log'] not in state['logs']:raise ValueError('Active log missing')
            scopes[scope]={'revision':state['revision'],'seen':set()}
        for scope,operation,raw_request,raw_response in db.execute('SELECT scope,operation,request,response FROM requests'):
            if scope not in scopes or not isinstance(operation,str) or not operation.strip():raise ValueError('Invalid Dice operation owner')
            request,response=json.loads(raw_request),json.loads(raw_response)
            if not isinstance(request,list) or len(request)!=3 or any(not isinstance(x,str) or not x.strip() for x in request[:2]):raise ValueError('Invalid Dice request')
            session.integer(request[2])
            if not isinstance(response,dict) or set(response)!={'revision','operation','audience','result'}:raise ValueError('Invalid Dice response')
            revision=response['revision'];session.integer(revision,1)
            if response['operation']!=operation or revision!=request[2]+1 or revision>scopes[scope]['revision'] or revision in scopes[scope]['seen']:
                raise ValueError('Dice receipt identity/revision mismatch')
            audience=response['audience']
            if audience!='table' and (not isinstance(audience,list) or any(not isinstance(a,str) or not a for a in audience)):
                raise ValueError('Invalid Dice receipt audience')
            session.encode(response);scopes[scope]['seen'].add(revision);operations+=1
        for info in scopes.values():
            if len(info['seen'])!=info['revision']:raise ValueError('Missing Dice operation receipts')
        return {'ok':True,'dialect':'dice-local','tables':len(scopes),'operations':operations,
                'scope':'SQLite integrity, state containers, active references and receipt revision continuity; not full command replay or authenticity'}
    except (ValueError,KeyError,TypeError) as exc:
        raise ValueError('Local Dice archive validation failed; check dialect, state and receipt consistency') from exc
    finally:db.close()


def backup(source,output):return archive.backup(source,output,validator=check)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('database',type=Path)
    sub=parser.add_subparsers(dest='command',required=True)
    c=sub.add_parser('check');c.add_argument('--expected-sha256')
    b=sub.add_parser('backup');b.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(session.encode(check(args.database,args.expected_sha256) if args.command=='check' else backup(args.database,args.output)))


if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    try:main()
    except (ValueError,KeyError,TypeError,OSError,sqlite3.Error) as exc:
        print(session.encode({'error':str(exc)}),file=sys.stderr);raise SystemExit(2)
