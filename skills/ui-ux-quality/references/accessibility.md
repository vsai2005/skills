# Accessibility Review

For web interfaces, use current WCAG 2.2 guidance as the default reference when the project does not specify another standard. Do not claim formal conformance from a lightweight review.

Useful primary sources:

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [WAI Easy Checks](https://www.w3.org/WAI/test-evaluate/preliminary/)
- [WAI Forms Tutorial](https://www.w3.org/WAI/tutorials/forms/)
- [WAI-ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [W3C Evaluating Web Accessibility](https://www.w3.org/WAI/test-evaluate/)

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
- dialogs manage entry/exit focus appropriately, keep focus within modal context, and restore it logically on close;
- composite widgets use the expected arrow-key/Tab model rather than making every internal item a separate Tab stop;
- keyboard users can dismiss or leave temporary UI;
- hover-only actions have keyboard/focus equivalents.

## Visual access

Check:

- text and meaningful UI contrast;
- meaning is not conveyed by color alone;
- text remains usable at 200% browser zoom when applicable;
- content reflows without loss around the WCAG-relevant narrow width when applicable;
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

## Additional WCAG 2.2 risk checks

When the feature touches these areas, also inspect:

- dragging has an equivalent non-drag interaction where required;
- authentication does not block password managers, paste, or other accessible completion methods;
- multi-step data entry does not unnecessarily require users to enter the same information again;
- help mechanisms remain consistently placed when the criterion applies;
- focused content is not obscured by sticky or overlay UI.

Use the exact current WCAG text for conformance decisions rather than relying on a shortened checklist.

## Verification depth

For meaningful changes, scale evidence with risk:

1. source/semantic inspection;
2. automated checks already available in the project;
3. keyboard-only task completion;
4. zoom/reflow and focus-obscuring checks;
5. screen-reader or other assistive-technology walkthrough for complex/high-impact flows.

Design-system component accessibility does not prove the assembled page or workflow is accessible.

## Tooling limits

Automated scanners can catch some markup, contrast, naming, and rule violations. They do not establish:

- sensible reading order;
- understandable labels;
- good error recovery;
- logical task flow;
- correct focus behavior in every dynamic interaction;
- full WCAG conformance.

Combine automated checks with knowledgeable human evaluation. W3C notes that no evaluation tool alone can determine whether a site meets accessibility standards. For high-impact flows, include assistive-technology testing when practical.
