# Accessibility Review

For web interfaces, use current WCAG 2.2 guidance as the default reference when the project does not specify another standard. Do not claim formal conformance from a lightweight review.

Useful primary sources:

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [WAI Easy Checks](https://www.w3.org/WAI/test-evaluate/preliminary/)
- [WAI Forms Tutorial](https://www.w3.org/WAI/tutorials/forms/)

## Structure and names

Check that meaningful structure is represented semantically rather than only visually.

- headings form a sensible hierarchy;
- landmarks/regions are appropriate;
- controls have accessible names;
- form controls have associated labels;
- related controls are grouped when needed;
- icons that act as controls expose a meaningful name.

Prefer native semantic elements before adding ARIA.

## Keyboard and focus

Verify important flows without a mouse when feasible.

Check:

- every interactive control is reachable;
- focus order follows the task;
- focus is visible;
- sticky overlays do not hide the focused element;
- dialogs manage entry/exit focus appropriately;
- keyboard users can dismiss or leave temporary UI;
- hover-only actions have keyboard/focus equivalents.

## Visual access

Check:

- text and meaningful UI contrast;
- meaning is not conveyed by color alone;
- text remains usable when zoomed;
- content does not become unusable because of horizontal scrolling at common zoom/narrow widths;
- pointer targets have adequate size or spacing;
- focus styling is perceivable.

WCAG 2.2 adds AA criteria such as Focus Not Obscured (Minimum) and Target Size (Minimum); use the current standard text for exact conformance decisions.

## Forms and errors

Check that:

- labels remain visible;
- instructions are understandable;
- errors are associated with the affected field or step;
- the message explains how to recover;
- error indication is not color-only;
- focus moves intentionally when a blocking error summary or dialog requires it;
- previously entered valid data is preserved where possible.

## Dynamic state

For async updates, dialogs, toasts, validation, and route changes, confirm assistive-technology users can discover important state changes when appropriate.

Do not add live-region announcements for every minor visual update. Announce information users need to continue the task.

## Motion and media

When motion/animation is used:

- honor reduced-motion preferences where appropriate;
- avoid unnecessary flashing or movement;
- do not make essential understanding depend on animation alone.

## Tooling limits

Automated scanners can catch some markup, contrast, naming, and rule violations. They do not establish:

- sensible reading order;
- understandable labels;
- good error recovery;
- logical task flow;
- correct focus behavior in every dynamic interaction;
- full WCAG conformance.

Combine automated checks with keyboard and rendered/runtime inspection.
