#!/usr/bin/env python3
"""Bind independent-review results to the exact Git diff they reviewed."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LEDGER=Path('.verification/reviews.jsonl')

def git(repo:Path,*args:str)->str:
    p=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,encoding='utf-8',check=False)
    if p.returncode: raise ValueError((p.stderr or p.stdout).strip() or 'git failed')
    return p.stdout

def snapshot(repo:Path,base:str)->dict:
    head=git(repo,'rev-parse','HEAD').strip()
    base_sha=git(repo,'rev-parse',base).strip()
    diff=git(repo,'diff','--binary',base_sha)
    staged=git(repo,'diff','--cached','--binary',base_sha)
    untracked=git(repo,'ls-files','--others','--exclude-standard','-z')
    extra=[]
    for rel in [x for x in untracked.split('\0') if x]:
        p=repo/rel
        if p.is_file(): extra.append((rel,hashlib.sha256(p.read_bytes()).hexdigest()))
    payload=(diff+'\n--STAGED--\n'+staged+'\n--UNTRACKED--\n'+json.dumps(extra,sort_keys=True)).encode()
    changed=sorted(set(git(repo,'diff','--name-only',base_sha).splitlines()+git(repo,'diff','--cached','--name-only',base_sha).splitlines()+[x[0] for x in extra]))
    return {'git_head':head,'base':base_sha,'diff_sha256':hashlib.sha256(payload).hexdigest(),'changed_files':changed}

def read_ledger(path:Path)->list[dict]:
    if not path.exists(): return []
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]

def main(argv=None)->int:
    p=argparse.ArgumentParser(description='Record/check state-bound independent reviews.')
    sub=p.add_subparsers(dest='cmd',required=True)
    r=sub.add_parser('record'); r.add_argument('--id',required=True); r.add_argument('--base',default='HEAD^'); r.add_argument('--outcome',choices=['approved','changes-requested','advisory'],required=True); r.add_argument('--reviewer',default='independent'); r.add_argument('--ledger',type=Path,default=DEFAULT_LEDGER); r.add_argument('repo',nargs='?',type=Path,default=Path('.'))
    c=sub.add_parser('check'); c.add_argument('--id',required=True); c.add_argument('--ledger',type=Path,default=DEFAULT_LEDGER); c.add_argument('repo',nargs='?',type=Path,default=Path('.'))
    a=p.parse_args(argv); repo=a.repo.resolve()
    try:
        rows=read_ledger(a.ledger)
        if a.cmd=='record':
            if any(x.get('id')==a.id for x in rows): raise ValueError(f'review id already exists: {a.id}')
            snap=snapshot(repo,a.base); rec={'schema_version':1,'id':a.id,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'reviewer':a.reviewer,'outcome':a.outcome,**snap}
            a.ledger.parent.mkdir(parents=True,exist_ok=True)
            with a.ledger.open('a',encoding='utf-8') as f: f.write(json.dumps(rec,sort_keys=True)+'\n')
            print(f"[OK] recorded {a.id} {a.outcome} {rec['diff_sha256'][:12]}"); return 0
        matches=[x for x in rows if x.get('id')==a.id]
        if not matches: raise ValueError(f'unknown review id: {a.id}')
        rec=matches[-1]; now=snapshot(repo,str(rec['base']))
        valid=now['diff_sha256']==rec['diff_sha256']
        print(f"{'VALID' if valid else 'STALE'} {a.id}")
        if not valid:
            before=set(rec.get('changed_files',[])); after=set(now.get('changed_files',[]));
            print('changed review surface: '+', '.join(sorted(before^after) or now.get('changed_files',[])))
        return 0 if valid else 1
    except (OSError,ValueError,json.JSONDecodeError) as exc: print(f"[ERROR] {exc}",file=sys.stderr); return 2
if __name__=='__main__': raise SystemExit(main())
