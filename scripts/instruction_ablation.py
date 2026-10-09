#!/usr/bin/env python3
"""Create section-ablated SKILL.md variants and compare optional ablation experiment records."""
from __future__ import annotations
import argparse, json, re, shutil, sys
from pathlib import Path

HEADING=re.compile(r'^(#{2,6})\s+(.+?)\s*$',re.M)

def remove_section(text:str,title:str)->str:
    matches=list(HEADING.finditer(text)); target=None
    norm=lambda value: re.sub(r'^\d+\.\s*', '', value.strip()).casefold()
    for i,m in enumerate(matches):
        if norm(m.group(2))==norm(title): target=(i,m); break
    if target is None: raise ValueError(f'section not found: {title}')
    i,m=target; level=len(m.group(1)); end=len(text)
    for nxt in matches[i+1:]:
        if len(nxt.group(1))<=level: end=nxt.start(); break
    return text[:m.start()]+text[end:]

def create_variant(skill_dir:Path,title:str,out:Path)->Path:
    if out.exists(): shutil.rmtree(out)
    shutil.copytree(skill_dir,out)
    p=out/'SKILL.md'; p.write_text(remove_section(p.read_text(encoding='utf-8'),title),encoding='utf-8'); return p

def compare(path:Path)->dict:
    rows=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
    vals={}
    for variant in ('control','full','ablated'):
        scores=[float(r.get('score_fraction',0)) for r in rows if r.get('variant')==variant and r.get('status','completed')=='completed']
        vals[variant]=sum(scores)/len(scores) if scores else None
    full=vals['full']; abl=vals['ablated'];
    decision='INSUFFICIENT_DATA' if full is None or abl is None else ('PRUNE_CANDIDATE' if abl>=full-0.01 else 'KEEP_SECTION')
    return {'averages':vals,'decision':decision}

def main(argv=None)->int:
    p=argparse.ArgumentParser(description='Create/compare instruction ablation experiments.'); sub=p.add_subparsers(dest='cmd',required=True)
    c=sub.add_parser('create'); c.add_argument('skill_dir',type=Path); c.add_argument('--section',required=True); c.add_argument('--output-dir',type=Path,required=True)
    x=sub.add_parser('compare'); x.add_argument('records',type=Path); x.add_argument('--fail-on-prune-candidate',action='store_true')
    a=p.parse_args(argv)
    try:
        if a.cmd=='create': print(create_variant(a.skill_dir.resolve(),a.section,a.output_dir.resolve())); return 0
        result=compare(a.records); print(json.dumps(result,indent=2)); return 1 if a.fail_on_prune_candidate and result['decision']=='PRUNE_CANDIDATE' else 0
    except (OSError,ValueError,json.JSONDecodeError) as exc: print(f"[ERROR] {exc}",file=sys.stderr); return 2
if __name__=='__main__': raise SystemExit(main())
