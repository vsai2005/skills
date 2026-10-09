#!/usr/bin/env python3
"""Measure discovery, core-skill, and progressive-disclosure resource budgets."""
from __future__ import annotations

import argparse, json, math, re, sys
from dataclasses import asdict, dataclass
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
RESOURCE_DIRS = ("references", "assets")

@dataclass(frozen=True)
class SkillBudget:
    name: str
    description_chars: int
    discovery_chars: int
    skill_lines: int
    skill_bytes: int
    rough_skill_tokens: int
    resource_files: int
    resource_bytes: int
    rough_resource_tokens: int


def _frontmatter(path: Path) -> dict[str,str]:
    text=path.read_text(encoding="utf-8"); m=FRONTMATTER_RE.match(text)
    if not m: raise ValueError(f"malformed frontmatter: {path}")
    data={}
    for raw in m.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#") or ":" not in raw: continue
        k,v=raw.split(":",1); v=v.strip()
        if v.startswith(("'",'"')) and len(v)>=2 and v.endswith(v[0]): v=v[1:-1]
        data[k.strip()]=v
    return data


def _resources(skill_dir: Path)->tuple[int,int,int]:
    files=[]
    for folder in RESOURCE_DIRS:
        p=skill_dir/folder
        if p.is_dir(): files.extend(x for x in p.rglob("*") if x.is_file())
    total=0; chars=0
    for p in files:
        data=p.read_bytes(); total += len(data)
        try: chars += len(data.decode("utf-8"))
        except UnicodeDecodeError: chars += len(data)
    return len(files), total, math.ceil(chars/4)


def measure(root: Path)->list[SkillBudget]:
    sr=root/"skills"
    if not sr.is_dir(): raise ValueError(f"skills directory missing: {sr}")
    out=[]
    for d in sorted(p for p in sr.iterdir() if p.is_dir()):
        md=d/"SKILL.md"
        if not md.is_file(): continue
        text=md.read_text(encoding="utf-8"); meta=_frontmatter(md); name=meta.get("name",d.name); desc=meta.get("description","")
        rf,rb,rt=_resources(d)
        out.append(SkillBudget(name,len(desc),len(name)+len(desc),len(text.splitlines()),len(text.encode()),math.ceil(len(text)/4),rf,rb,rt))
    return out


def summarize(b:list[SkillBudget])->dict[str,int]:
    return {
        "skills":len(b),
        "total_discovery_chars":sum(x.discovery_chars for x in b),
        "rough_total_skill_tokens":sum(x.rough_skill_tokens for x in b),
        "rough_total_resource_tokens":sum(x.rough_resource_tokens for x in b),
        "total_resource_bytes":sum(x.resource_bytes for x in b),
        "max_description_chars":max((x.description_chars for x in b),default=0),
        "max_skill_lines":max((x.skill_lines for x in b),default=0),
        "max_resource_bytes":max((x.resource_bytes for x in b),default=0),
    }


def violations(b:list[SkillBudget],*,max_total_discovery_chars:int,max_description_chars:int,max_skill_lines:int,max_resource_bytes:int,max_total_resource_bytes:int)->list[str]:
    probs=[]; s=summarize(b)
    if s["total_discovery_chars"]>max_total_discovery_chars: probs.append(f"total discovery metadata is {s['total_discovery_chars']} chars; budget is {max_total_discovery_chars}")
    if s["total_resource_bytes"]>max_total_resource_bytes: probs.append(f"total progressive-disclosure resources are {s['total_resource_bytes']} bytes; budget is {max_total_resource_bytes}")
    for x in b:
        if x.description_chars>max_description_chars: probs.append(f"{x.name} description is {x.description_chars} chars; budget is {max_description_chars}")
        if x.skill_lines>max_skill_lines: probs.append(f"{x.name}/SKILL.md is {x.skill_lines} lines; budget is {max_skill_lines}")
        if x.resource_bytes>max_resource_bytes: probs.append(f"{x.name} resources are {x.resource_bytes} bytes; budget is {max_resource_bytes}")
    return probs


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description="Measure skill discovery/core/resource context budgets.")
    p.add_argument("root",nargs="?",default=".",type=Path)
    p.add_argument("--max-total-discovery-chars",type=int,default=7000)
    p.add_argument("--max-description-chars",type=int,default=600)
    p.add_argument("--max-skill-lines",type=int,default=500)
    p.add_argument("--max-resource-bytes",type=int,default=50000)
    p.add_argument("--max-total-resource-bytes",type=int,default=300000)
    p.add_argument("--json",action="store_true"); p.add_argument("--fail-on-budget",action="store_true")
    a=p.parse_args(argv)
    try: b=measure(a.root.resolve())
    except (ValueError,OSError,UnicodeError) as exc: print(f"[ERROR] {exc}",file=sys.stderr); return 2
    probs=violations(b,max_total_discovery_chars=a.max_total_discovery_chars,max_description_chars=a.max_description_chars,max_skill_lines=a.max_skill_lines,max_resource_bytes=a.max_resource_bytes,max_total_resource_bytes=a.max_total_resource_bytes); s=summarize(b)
    if a.json: print(json.dumps({"summary":s,"skills":[asdict(x) for x in b],"violations":probs},indent=2))
    else:
        print(f"Skills: {s['skills']}"); print(f"Discovery metadata: {s['total_discovery_chars']} chars"); print(f"Approximate SKILL.md total: {s['rough_total_skill_tokens']} tokens (all skills; normally selective)"); print(f"Progressive-disclosure resources: {s['total_resource_bytes']} bytes (~{s['rough_total_resource_tokens']} tokens, conditionally loaded)")
        for x in b: print(f"- {x.name}: description {x.description_chars} chars, SKILL.md {x.skill_lines} lines (~{x.rough_skill_tokens} tokens), resources {x.resource_files} files/{x.resource_bytes} bytes")
        if probs:
            print("Budget violations:"); [print(f"  - {q}") for q in probs]
        else: print("Budget violations: none")
    return 1 if a.fail_on_budget and probs else 0
if __name__=="__main__": sys.exit(main())
