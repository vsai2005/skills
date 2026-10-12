# Rendered UI Verification

Use the project's existing browser, component, accessibility, or visual-regression tooling when available. Do not introduce a new browser stack merely to satisfy this checklist unless the task warrants it.

## Evidence ladder

Prefer the strongest practical evidence for the claim:

```text
source inspection
  -> rendered static inspection
  -> real interaction/state check
  -> keyboard/manual accessibility check
  -> assistive-technology check where risk justifies it
  -> real-user evidence when the claim is about user behavior
```

Higher layers do not make lower layers useless. They answer different questions.

## Render the important states

For the touched user task, inspect representative applicable states rather than only the default view:

- default/ready;
- hover/focus/pressed/selected where meaningful;
- loading or pending;
- success;
- empty;
- validation error;
- dependency/server error;
- permission denied/read-only;
- long/large content;
- destructive confirmation;
- slow/offline behavior when relevant.

If the product supports light/dark themes or multiple brands, test the touched semantic states in the relevant themes rather than assuming token parity.

## Responsive and reflow checks

Use project-supported viewports first.

For web interfaces, when feasible also check:

- content reflow around 320 CSS px for WCAG-related risk;
- 200% browser zoom for text/layout loss;
- an intermediate viewport where the layout structure changes;
- sticky headers/footers with keyboard focus;
- software-keyboard behavior for mobile forms/dialogs when important.

A narrower stress width such as 280px can be useful as an engineering stress test, but do not present it as a universal WCAG requirement.

## Content resilience

Use realistic stress content:

- long names and labels;
- translated strings or expected localization expansion;
- large numbers;
- multi-line validation/status copy;
- many and zero items;
- long unbroken values only when the product can legitimately receive them.

When the product supports RTL languages, inspect logical ordering, alignment, directional icons, and component behavior in RTL.

## Accessibility verification levels

A practical sequence is:

1. semantic/source inspection;
2. existing automated scanner or accessibility test if available;
3. keyboard-only completion of the important flow;
4. zoom/reflow and focus-obscuring checks;
5. screen-reader or other assistive-technology walkthrough when the change is high-impact or the component is complex.

Automated tools cannot establish full accessibility. W3C explicitly requires knowledgeable human evaluation for questions tools cannot determine.

Primary reference: [W3C evaluating web accessibility](https://www.w3.org/WAI/test-evaluate/).

## Dialogs and composite widgets

For dialogs, menus, tabs, listboxes, grids, comboboxes, toolbars, and similar widgets, check the established interaction model rather than inventing key behavior.

For a modal dialog, relevant checks commonly include:

- focus moves inside on open;
- focus remains in the modal while it is active;
- Escape closes when that matches the product requirement;
- closing returns focus to the trigger or another logical workflow target;
- initial focus does not hide important content or bias a dangerous irreversible action;
- the dialog has an accessible name and useful description when appropriate.

Reference: [WAI-ARIA APG dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/).

## Visual regression evidence

When the repository already uses screenshot or component-story baselines:

- update a baseline only after confirming the visual change is intended;
- compare relevant states and viewports;
- do not accept a new baseline merely because the diff is large;
- distinguish anti-aliasing/noise from a semantic layout or state regression.

Visual snapshots protect appearance. They do not prove interaction or usability.

## Performance as UX

For user-facing latency, verify the experience around the delay rather than optimizing speculative micro-performance.

Check whether:

- the user gets timely system-status feedback;
- layout does not jump unnecessarily;
- repeated actions are guarded from accidental duplication;
- slow operations preserve context;
- loading placeholders do not falsely imply content that may never arrive.

Measure actual performance only when making performance claims.
