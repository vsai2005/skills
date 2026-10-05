# Case Study: Fix the Classifier, Not the Examples

## Situation

A lesson-topic classifier uses a set of ignored short tokens. Programming language names such as `Go`, `C`, and `R` are also short tokens. A request combining an allowed lesson topic with one of these technologies is incorrectly treated as in-scope.

## Tempting patch

```ts
if (token === "Go" || token === "C" || token === "R") {
  return OUT_OF_SCOPE;
}
```

This fixes reported fixtures but teaches the system nothing about the actual semantic distinction. The next short technology name creates another patch.

## Root-cause workflow

1. Reproduce several failing names and ordinary short words.
2. Inspect token normalization, ignored-word handling, and technology taxonomy.
3. Find the precedence error: ignored/common-token filtering runs before recognized-technology classification.
4. Correct the classification rule so known technology/language tokens retain semantic identity before generic ignore logic.
5. Add regression coverage for reported names, a different technology name, ordinary short words, and important distinctions such as Java vs JavaScript.

## Better result

The code expresses the general rule once. Callers do not need technology-specific branches, and future taxonomy additions work through the same classifier boundary.

## Quality checks

- original failing requests now classify correctly;
- ordinary ignored words remain ignored;
- no list of bug-report values was added to a caller;
- tests still assert out-of-scope behavior rather than being relaxed;
- final diff contains no investigation logging.
