## What changed

## Why

## Skill behavior affected

- [ ] Activation/description
- [ ] Build workflow
- [ ] Debug workflow
- [ ] Refactor workflow
- [ ] Architecture workflow
- [ ] Verification workflow
- [ ] Scripts/tooling
- [ ] Documentation only

## Evidence

- [ ] `python3 scripts/validate_repo.py .`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] Self-audit or equivalent relevant check
- [ ] Activation/eval case added or updated when behavior changed

## Integrity checks

- [ ] I did not weaken a test/check merely to get green.
- [ ] I kept the smallest useful skill scope rather than adding generic prompt text.
- [ ] Provider-specific behavior is isolated from provider-neutral skill logic where practical.
- [ ] Any deliberate workaround has a reason and removal condition.
