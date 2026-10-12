#!/usr/bin/env python3
"""Evaluate workflow retry/review/scope signals and recommend a reset when iteration is thrashing."""
from __future__ import annotations
import argparse, json

DEFAULTS={'L0':(1,1,150,3),'L1':(2,1,350,6),'L2':(3,2,800,12),'L3':(3,2,1500,20),'L4':(4,3,3000,35)}

def assess(level:str,attempts:int,same_failure:int,review_cycles:int,churn:int,files:int)->list[str]:
    max_attempts,max_reviews,max_churn,max_files=DEFAULTS[level]; out=[]
    if same_failure>=2: out.append('same failure repeated twice: stop patching and rebuild the hypothesis')
    if attempts>max_attempts: out.append(f'implementation attempts {attempts} exceed {level} reset threshold {max_attempts}')
    if review_cycles>max_reviews: out.append(f'review cycles {review_cycles} exceed {level} reset threshold {max_reviews}')
    if churn>max_churn or files>max_files: out.append(f'diff scope ({files} files/{churn} churn) exceeds the default {level} review signal ({max_files}/{max_churn})')
    return out

def main(argv=None)->int:
    p=argparse.ArgumentParser(description='Check workflow thrash/revision signals.'); p.add_argument('--level',choices=DEFAULTS,default='L1'); p.add_argument('--attempts',type=int,default=1); p.add_argument('--same-failure',type=int,default=0); p.add_argument('--review-cycles',type=int,default=0); p.add_argument('--churn',type=int,default=0); p.add_argument('--files',type=int,default=0); p.add_argument('--json',action='store_true'); p.add_argument('--fail-on-reset',action='store_true'); a=p.parse_args(argv)
    signals=assess(a.level,a.attempts,a.same_failure,a.review_cycles,a.churn,a.files)
    if a.json: print(json.dumps({'level':a.level,'signals':signals,'reset_required':bool(signals)},indent=2))
    else:
        print(f"Workflow budget: {a.level}")
        print('Reset signals: none' if not signals else 'Reset signals:\n'+'\n'.join('  - '+x for x in signals))
    return 1 if a.fail_on_reset and signals else 0
if __name__=='__main__': raise SystemExit(main())
