#!/usr/bin/env python3
"""Check cross-host Agent Skills portability without invoking a model."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

FRONT=re.compile(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)',re.S)
HOST_TERMS=re.compile(r'\b(?:Codex|Claude Code|Anthropic|OpenAI)\b',re.I)

def check(root:Path)->dict:
    errors=[]; warnings=[]; skills=[]
    manifests=['plugin.json','.codex-plugin/plugin.json','.claude-plugin/plugin.json']
    for rel in manifests:
        p=root/rel
        if not p.is_file(): errors.append(f'missing {rel}'); continue
        try: data=json.loads(p.read_text(encoding='utf-8'))
        except Exception as exc: errors.append(f'invalid {rel}: {exc}'); continue
        if data.get('name')!='engineering-quality': errors.append(f'{rel}: unexpected plugin name')
        if rel!='.claude-plugin/plugin.json' and data.get('skills')!='./skills/': errors.append(f'{rel}: skills path must be ./skills/')
    for d in sorted((root/'skills').iterdir() if (root/'skills').is_dir() else []):
        md=d/'SKILL.md'
        if not md.is_file(): continue
        text=md.read_text(encoding='utf-8'); m=FRONT.match(text)
        if not m: errors.append(f'{d.name}: malformed SKILL.md frontmatter'); continue
        keys=[]
        for line in m.group(1).splitlines():
            if ':' in line: keys.append(line.split(':',1)[0].strip())
        if set(keys)!={'name','description'}: errors.append(f'{d.name}: core frontmatter must contain only name/description')
        if HOST_TERMS.search(text): warnings.append(f'{d.name}: provider-specific product term in core SKILL.md')
        oa=d/'agents/openai.yaml'
        if not oa.is_file(): errors.append(f'{d.name}: missing agents/openai.yaml')
        skills.append(d.name)
    # Portable paths must not contain Windows-only separators or absolute links.
    for p in root.rglob('*.md'):
        try: text=p.read_text(encoding='utf-8')
        except UnicodeError: continue
        if re.search(r'\]\([A-Za-z]:\\',text): errors.append(f'{p.relative_to(root)}: Windows absolute Markdown link')
    return {'skills':skills,'errors':errors,'warnings':warnings}

def main(argv=None)->int:
    p=argparse.ArgumentParser(description='Check portable skill/manifests across common Agent Skills hosts.'); p.add_argument('root',nargs='?',type=Path,default=Path('.')); p.add_argument('--json',action='store_true'); p.add_argument('--warnings-as-errors',action='store_true'); a=p.parse_args(argv)
    r=check(a.root.resolve())
    if a.json: print(json.dumps(r,indent=2))
    else:
        for e in r['errors']: print('[ERROR]',e)
        for w in r['warnings']: print('[WARN]',w)
        if not r['errors'] and not r['warnings']: print(f"[OK] portability checks passed for {len(r['skills'])} skill(s)")
    return 1 if r['errors'] or (a.warnings_as_errors and r['warnings']) else 0
if __name__=='__main__': raise SystemExit(main())
