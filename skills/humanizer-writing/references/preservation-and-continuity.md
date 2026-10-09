# Preservation and Continuity

## Protected content

Treat the following as protected unless the user explicitly permits a change:

- numbers, percentages, currency, dates, times, limits, and units;
- names, product versions, regions, URLs, citations, and quoted text;
- code, commands, paths, API names, identifiers, UI labels, and error codes;
- warnings and safety constraints;
- negation such as `no`, `not`, `never`, `without`, and `cannot`;
- modality and certainty such as `may`, `might`, `can`, `should`, `must`, and `will`.

Example semantic failure:

```text
Source: The migration may fail.
Bad rewrite: The migration will fail.
```

The rewrite sounds fluent but changes the claim.

## Deterministic checks

When repository helpers are available, `humanizer_audit.py compare` checks a useful subset of protected literals plus negation and modal language. It is intentionally conservative and does not replace semantic review.

A clean deterministic check does **not** prove that meaning is identical. It only removes several common failure modes.

## Long-form continuity

For longer work, maintain a compact ledger instead of relying on conversational memory.

Record:

- audience and purpose;
- voice anchors;
- terminology that must stay stable;
- protected facts and claim strength;
- current argument or narrative position;
- unresolved references or open threads;
- section purpose;
- deliberate stylistic choices.

Update the ledger only when the source or user changes one of these facts.

## Candidate selection

If Deep mode creates more than one candidate, compare every candidate directly with the original source for preservation. Do not use candidate A as the semantic source for candidate B.
