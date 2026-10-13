# Release / Freeze Gate

Use this reference for substantial release, freeze, or project-readiness decisions.

Apply only gates relevant to the real consumer path:

- canonical source is correct;
- transformations/projections are synchronized;
- relevant static/unit/integration checks pass;
- build/export succeeds when applicable;
- runtime/e2e evidence exists when applicable;
- rendered/consumed output was inspected when the requirement is user-facing;
- important independent-review findings are resolved or dispositioned;
- required deferred tests are cleared or explicitly reported;
- final evidence is bound to the current candidate state.

Mark a gate non-applicable instead of inventing evidence.

## Verification depth

Use the cheapest evidence that can falsify the requirement, then broaden with risk.

Typical examples:

- library/API -> focused tests -> contract/integration -> consumer check;
- web UI -> component/integration -> build -> browser/e2e -> rendered inspection;
- docs -> source -> build -> published/rendered inspection;
- data pipeline -> unit -> transformation/schema -> persisted/output validation;
- generated artifact -> source -> generator -> generated file -> consumer validation.

Use `tiered-testing` only when test-cost/deferment decisions are material. Use `verify-change` at the final evidence gate rather than keeping either loaded through unrelated implementation work.

## Final report

Record:

- audited/changed scope;
- consumer paths checked;
- specialists used;
- checks actually completed;
- findings fixed/remaining;
- evidence unavailable;
- readiness decision and explicit conditions.

Never promote confidence, source inspection, simulation, or green unit tests into a stronger claim than the evidence supports.
