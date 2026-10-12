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
