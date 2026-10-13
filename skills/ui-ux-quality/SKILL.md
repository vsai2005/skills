---
name: ui-ux-quality
description: Audit or improve user-facing interfaces when hierarchy, interaction states, responsive behavior, accessibility, consistency, or rendered evidence are primary. Not for backend-only work or ordinary feature architecture.
---

# UI/UX Quality

Treat interface quality as product behavior, not decoration. Judge the rendered experience users actually consume.

## 1. Establish the UI contract

Identify:

- target user and primary task;
- page/flow purpose and primary action;
- preserved brand/design-system constraints;
- important devices, inputs, states, and accessibility expectations.

Separate **observed evidence** from **usability hypotheses**. Heuristic review can identify likely risks; it cannot prove what users notice, prefer, or successfully complete.

## 2. Inspect the existing product system

Before redesigning, inspect local layout, spacing, typography, color tokens, shared components, navigation, form/feedback patterns, responsive behavior, and accessibility utilities.

Prefer the existing coherent system. Choose components/tokens by semantic intent. Prefer native semantics or established accessible primitives before custom widgets.

Use [references/review-checklist.md](references/review-checklist.md) for broad audits and [references/usability-design-system.md](references/usability-design-system.md) for heuristics, semantic roles, component contracts, or research uncertainty.

## 3. Review hierarchy, states, and recovery

Make the next useful action clear. Check purpose, heading/content order, grouping, information density, labels, status, risk, and destructive actions.

Review applicable interaction states, not only the happy path:

```text
default -> loading -> success
            |           |
            v           v
          error       updated
```

Also consider empty, disabled, validation, permission, offline/slow, destructive-confirmation, and partial-data states when relevant.

For forms, require persistent associated labels, useful validation, plain-language recovery, preserved input after recoverable failure, and clear required/optional/destructive actions.

Use [references/state-responsive-matrix.md](references/state-responsive-matrix.md) when flows have several dynamic states or viewports.

## 4. Verify responsive and accessible behavior

Check representative narrow, wide, and product-critical intermediate layouts for overflow, clipped actions, unusable navigation, dense tables/cards, viewport-breaking dialogs/drawers, sticky obstruction, and harmful text wrapping. Include zoom/text resize and realistic content expansion when relevant; check localization/RTL only when supported by the product.

Apply the accessibility model of the actual platform:

- Web: WCAG 2.2 AA and established interaction patterns when applicable.
- Apple: native SwiftUI/UIKit semantics, VoiceOver, Dynamic Type, focus, and platform modality.
- Android: native/Compose semantics, TalkBack, text scaling, touch/focus conventions.

Do not transplant web-only ARIA/keyboard rules into native apps.

Use [references/accessibility.md](references/accessibility.md) for the focused pass. Automated accessibility tooling is useful evidence, not proof of full usability or conformance.

## 5. Check interaction truth and consistency

Verify that actions give feedback, destructive behavior is deliberate, cancel/back/undo exist when recovery reasonably needs them, essential actions are not hover-only, and errors/retries preserve user context.

Visual state, accessibility state, application state, and actual user-visible outcome must agree.

When repeated spacing, typography, control, color, card/table/list, loading, or error inconsistencies share an owner, fix the shared component/token rather than patching instances.

## 6. Load expressive-design rules only when needed

For premium, expressive, distinctive, or non-template work, use [references/premium-visual-direction.md](references/premium-visual-direction.md). Require product-specific composition, typography, imagery/content, restraint, and authentic evidence. Do not fabricate metrics, logos, testimonials, awards, or capabilities.

For animation, sliding interactions, transitions, scroll storytelling, or 3D, use [references/motion-3d.md](references/motion-3d.md). Choose the smallest capable technology, require coherent spatial logic, reduced-motion/static fallback, and include performance in UX quality.

Do not treat gradients, glass, rounded cards, custom cursors, smooth scrolling, or 3D as automatic quality.

## 7. Inspect rendered evidence

Source inspection is insufficient when UI/UX is the requirement.

When feasible, inspect representative runtime evidence such as:

- screenshots at important viewports/themes/states;
- keyboard navigation;
- browser/e2e flows;
- accessibility/semantic inspection;
- real loading/error/empty states;
- shared-component behavior;
- zoom/reflow/content stress;
- existing visual-regression/component-story evidence.

Use [references/rendered-verification.md](references/rendered-verification.md) to choose evidence depth without adding unnecessary tooling.

If runtime evidence is unavailable, state that limitation instead of presenting code review as visual proof.

## 8. Prioritize, delegate, and report

Prioritize roughly by:

```text
severity ~= task blockage x frequency x recovery difficulty
```

Fix blocked/misleading core tasks, inaccessible/unrecoverable interaction, and broken responsive behavior before cosmetic polish.

This skill owns UI/UX judgment. Delegate deeper ownership when needed:

- feature/code placement -> `structure-feature`;
- cross-layer source-to-consumer audit -> `project-quality-orchestrator`;
- trust-boundary work -> `security-hardening`;
- controlled technical prose -> `asd-ste100-writing`;
- final merge-readiness evidence -> `verify-change`.

For substantial work, report the task/surfaces reviewed, viewport/state coverage, high-impact findings with evidence, shared-owner causes, fixes, runtime checks actually performed, unavailable checks, and remaining risk.

For each important finding prefer:

```text
location -> evidence -> user impact -> owning cause -> smallest correct repair -> verification
```

Do not turn taste into a defect, heuristic review into invented user research, or a numeric score into a substitute for blocking findings.

Load [references/research-basis.md](references/research-basis.md) only when provenance or methodology comparison is relevant.
