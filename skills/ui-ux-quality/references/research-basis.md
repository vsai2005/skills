# Research Basis for UI/UX Quality

This skill intentionally combines standards, design-system practice, usability inspection, and rendered evidence. It does not treat any single framework or component library as universally correct.

## Primary standards and guidance

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) — normative accessibility success criteria.
- [WAI-ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/) — practical widget, keyboard, focus, naming, and interaction patterns.
- [W3C Evaluating Web Accessibility](https://www.w3.org/WAI/test-evaluate/) — automated tools are useful, but knowledgeable human evaluation is still required.
- [Nielsen Norman Group: 10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) — broad inspection heuristics for status, control, consistency, error prevention/recovery, recognition, and help.

## Design-system references

The following public systems informed the skill's emphasis on accessible primitives, semantic roles, consistency, and real interaction behavior:

- [Radix Primitives philosophy](https://github.com/radix-ui/primitives/blob/main/philosophy.md) — accessibility, function, interoperability, composability, and customization.
- [React Spectrum / React Aria](https://github.com/adobe/react-spectrum) — accessible behavior, keyboard/screen-reader support, internationalization, and separation of interaction behavior from visual styling.
- [Base UI accessibility](https://base-ui.com/react/overview/accessibility) — keyboard interaction, focus management, labels, contrast responsibilities, and testing across platforms/devices.
- [U.S. Web Design System accessibility](https://designsystem.digital.gov/documentation/accessibility/) — automated and manual testing, screen readers, keyboard, zoom, touch, community feedback, and page-level user testing.
- [GOV.UK Design System error messages](https://design-system.service.gov.uk/components/error-message/) — specific, recoverable errors and preservation of entered data.
- [GitHub Primer responsive guidance](https://primer.style/product/getting-started/foundations/responsive/) — responsive behavior includes device/input affordances, not only breakpoint rearrangement.
- [Adobe Spectrum inclusive design](https://spectrum.adobe.com/foundations/inclusivity/inclusive-design) — prevention, context-sensitive help, inclusive interaction, and internationalization.
- [Figma design-systems learning](https://help.figma.com/hc/en-us/articles/14552901442839-Overview-Introduction-to-design-systems) — principles, foundations, documentation, process, accessibility, tokens, and component architecture.

## Video references

- [NN/g: 10 Usability Heuristics — From Theory to Practice (course preview)](https://www.youtube.com/watch?v=WmmBLgtkjN4) — emphasizes applying heuristics to real interfaces rather than memorizing labels.
- [Figma Config: Auditing design systems for accessibility](https://www.youtube.com/watch?v=cIUdgKnhAc8) — emphasizes auditing accessibility from design through code and treating contrast as only one part of accessibility.
- [Google Developers: A11ycasts](https://developers.google.com/web/shows/) — practical platform-level accessibility checks and real-world fixes, including keyboard and focus behavior.

These videos are supporting material. Standards and current project behavior remain stronger evidence for conformance or implementation decisions.

## Native-platform references

- [Apple accessibility for UIKit](https://developer.apple.com/documentation/uikit/accessibility_for_uikit) — standard controls provide accessibility behavior; custom UI must expose the correct accessibility information and interactions.
- [Apple Dynamic Type](https://developer.apple.com/videos/play/wwdc2024/10074/) — adaptive text and layout behavior for users who choose larger content sizes.
- [Android: Make apps more accessible](https://developer.android.com/guide/topics/ui/accessibility/apps) — platform accessibility semantics, descriptions, touch targets, and assistive-technology behavior.
- [Android accessibility principles](https://developer.android.com/guide/topics/ui/accessibility/principles) — clear semantics, operability, and platform-aware accessibility.

These sources are intentionally separated from the web WCAG/APG material so the skill does not apply web implementation rules to native apps.

## External agent-workflow comparison

The public [plugin87/ux-ui-agent-skills](https://github.com/plugin87/ux-ui-agent-skills) repository was reviewed as an example of a much heavier UI-specific agent system.

Useful ideas adopted in a smaller provider-neutral form include:

- real-render verification rather than source-only inspection;
- state-aware accessibility checks;
- semantic token usage by intent;
- responsive/content stress;
- Nielsen-style heuristic review;
- explicit separation of measurable gates from subjective critique.

Ideas intentionally **not** copied as defaults:

- dozens of mandatory UI gates for every task;
- one universal aesthetic doctrine;
- hard dependency on a browser/runtime toolchain;
- a single weighted UI score as the main readiness signal.

This repository keeps the UI/UX skill selective and progressive-disclosure based. Existing project tooling should be reused when possible.

## Community feedback signals

Community discussions around Radix, React Aria, Base UI, and shadcn repeatedly show a practical tradeoff: stronger accessibility behavior can increase implementation/API complexity, while simpler developer experience can leave more responsibility with product teams.

Treat that as a reason to inspect the local stack and behavior contract rather than declaring one library universally best.

Community opinion is not a standard and should not override project evidence or primary documentation.
