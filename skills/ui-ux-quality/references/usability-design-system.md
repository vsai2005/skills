# Usability and Design-System Review

Use this reference when the problem is broader than spacing or visual polish.

## Heuristic lens

Use established usability heuristics as prompts for inspection, not as proof that users will behave a certain way.

Check whether the interface:

1. keeps users informed about system status;
2. uses language and concepts that match the user's world;
3. provides control, cancel, back, undo, or another sensible escape;
4. follows internal and platform conventions;
5. prevents likely errors before relying on error messages;
6. favors recognition over recall;
7. supports efficient repeated use when the product needs it;
8. removes information and decoration that compete with the task;
9. helps users identify, understand, and recover from errors;
10. provides concise contextual help when the task cannot explain itself.

Reference: [Nielsen Norman Group usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/).

Do not mechanically produce ten findings. Apply only the heuristics that expose a real issue in the current task.

## Heuristic review is not user research

A reviewer can identify likely usability risks. A reviewer cannot prove:

- what users notice first;
- whether terminology matches a user's mental model;
- whether a navigation label is discoverable;
- whether a flow is faster or easier for the target audience;
- whether a redesign improves conversion, completion, satisfaction, or trust.

When those questions matter, label the conclusion as a hypothesis and recommend appropriate evidence such as task-based usability testing, analytics, support data, or controlled experiments.

Do not fabricate personas, user quotes, test results, success rates, or research findings.

## Semantic design-system use

Prefer design-system meaning over visual coincidence.

Examples:

- destructive action -> destructive/danger semantic role;
- primary action -> primary semantic role;
- warning/status -> the system's warning/status role;
- muted supporting text -> supporting/muted text role;
- selected/pressed/current -> established state styling and semantics.

A token or component is not correct merely because its color or shape looks similar.

Use this sequence:

```text
user intent -> semantic role -> established component/token -> rendered state
```

Repeated mismatch may indicate a shared component or token problem rather than several page-level defects.

## Accessible primitives first

For common interactive patterns, prefer in this order when practical:

1. native HTML semantics and controls;
2. an established project/design-system component;
3. an accessibility-focused primitive already used by the project;
4. a custom widget only when the previous options cannot satisfy the requirement.

A custom widget owns a behavior contract, not only markup. Depending on the pattern, that can include:

- accessible name, role, value, and state;
- keyboard interaction;
- visible and predictable focus;
- focus entry/exit behavior;
- pointer/touch behavior;
- disabled/read-only behavior;
- async and error states;
- screen-reader announcements where needed.

Use the [WAI-ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/) for complex widgets, while remembering that APG examples are guidance rather than a formal conformance guarantee.

## Interaction truth

Do not accept a control because it looks interactive or exposes an ARIA state.

Verify that the action actually changes the product state it claims to control.

Examples:

- a sort button changes the sort order and its state;
- a toggle changes the represented setting;
- a tab changes the active panel;
- a retry action performs a retry;
- a success message corresponds to committed success;
- a loading state ends when the operation ends.

Visual state, accessibility state, application state, and user-visible outcome should agree.

## Avoid false precision

For normal audits, prefer ranked findings with evidence and impact over a single numeric design score.

A score can be useful when the user explicitly asks for comparison or tracking, but it must not hide:

- a task-blocking issue;
- an accessibility failure;
- missing runtime evidence;
- uncertainty about user behavior;
- differences in severity between findings.
