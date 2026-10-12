# Accessibility Review

For web interfaces, use current WCAG 2.2 guidance as the default reference when the project does not specify another standard. Do not claim formal conformance from a lightweight review.

Useful primary sources:

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [WAI Easy Checks](https://www.w3.org/WAI/test-evaluate/preliminary/)
- [WAI Forms Tutorial](https://www.w3.org/WAI/tutorials/forms/)
- [WAI-ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [W3C Evaluating Web Accessibility](https://www.w3.org/WAI/test-evaluate/)

## Platform scope

Choose the correct platform model before applying detailed checks.

### Web

Use semantic HTML first, then ARIA only when native semantics are insufficient. WCAG 2.2 and WAI-ARIA APG are the primary references for conformance and complex web-widget behavior.

### Apple platforms

Prefer standard SwiftUI/UIKit controls and system semantics when they satisfy the interaction. Review with the platform's accessibility APIs and conventions, including VoiceOver, Dynamic Type, meaningful accessibility labels/actions, focus where relevant, and modal/presentation behavior.

Primary references:
- [Apple accessibility for UIKit](https://developer.apple.com/documentation/uikit/accessibility_for_uikit)
- [Apple Dynamic Type](https://developer.apple.com/videos/play/wwdc2024/10074/)

### Android

Prefer standard Android/Compose controls and semantics. Review TalkBack descriptions/state, text scaling, touch targets, keyboard/D-pad focus where relevant, and input-mode/device behavior.

Primary references:
- [Android: Make apps more accessible](https://developer.android.com/guide/topics/ui/accessibility/apps)
- [Android accessibility principles](https://developer.android.com/guide/topics/ui/accessibility/principles)

Android's commonly recommended 48dp touch target is platform guidance. Do not confuse it with WCAG 2.2's web target-size success criterion, which uses a different minimum and exceptions.

### Cross-platform rule

Do not copy a web ARIA role, CSS measurement, or keyboard convention into a native interface merely because the concept has the same name. Verify the platform's actual interaction and accessibility contract.

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

## Text scaling and adaptive layout

When the platform supports system text scaling, verify that important content and controls remain usable at enlarged sizes. Prefer adaptive layout over clipping, truncating essential instructions, or disabling text scaling.

For native mobile flows also consider:

- software-keyboard overlap and safe-area behavior;
- orientation and device-size changes when supported;
- platform back/dismiss conventions;
- focus restoration after modal or navigation transitions;
- accessibility labels that describe purpose rather than visual appearance.

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
