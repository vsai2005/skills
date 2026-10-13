---
name: ui-ux-quality
description: Audit or improve user-facing interfaces when hierarchy, interaction states, responsive behavior, accessibility, consistency, or rendered evidence are primary. Not for backend-only work or ordinary feature architecture.
---

# UI/UX Quality

Treat interface quality as product behavior, not decoration. A UI is not good because the source looks clean; it is good when users can understand, operate, recover from, and trust the rendered experience.

## 1. Define the user task before judging the screen

Identify:

- the target user and their primary task;
- the page or flow purpose;
- the primary action and important secondary actions;
- required information and decisions;
- preserved product identity, brand, and design-system constraints;
- important devices, input methods, and accessibility expectations.

Do not redesign the product identity merely because another style is fashionable.

Separate **observed evidence** from **usability hypotheses**. A heuristic review can identify likely risks, but it cannot replace real-user evidence when the question is what users notice, understand, prefer, or successfully complete.

## 2. Inspect the existing product system first

Before proposing visual changes, inspect the real local conventions:

- layout and spacing scale;
- typography and color tokens;
- shared components and interaction patterns;
- navigation model;
- form patterns;
- feedback/toast/dialog conventions;
- responsive behavior;
- accessibility utilities.

Prefer a coherent existing system over introducing a second visual language. Choose components and tokens by semantic intent, not by whichever visual value looks close enough. Prefer native semantics or an established accessible primitive before creating a custom widget.

Use [references/review-checklist.md](references/review-checklist.md) for a detailed audit when the task is broad. Use [references/usability-design-system.md](references/usability-design-system.md) when usability heuristics, semantic token roles, component behavior contracts, or research uncertainty are material.

## 3. Check hierarchy and comprehension

The interface should make the next useful action obvious.

Review:

- whether the page purpose is clear quickly;
- whether one primary action dominates when appropriate;
- heading and content order;
- grouping and proximity;
- readable information density;
- labels that describe intent rather than implementation;
- whether status, risk, and destructive actions are visually distinct.

Fix hierarchy before polishing shadows, gradients, or micro-animation.

For broader usability reviews, apply relevant established heuristics such as system-status visibility, match to user language, user control, consistency, error prevention, recognition over recall, and error recovery. Do not force a finding for every heuristic.

## 4. Review the complete interaction state model

Do not review only the happy-path screenshot.

For each important flow, consider applicable states:

```text
default -> loading -> success
            |           |
            v           v
          error       updated
```

Also inspect empty, disabled, validation, permission-denied, offline/slow, destructive-confirmation, and partial-data states when relevant.

Use [references/state-responsive-matrix.md](references/state-responsive-matrix.md) when a flow has several dynamic states or viewports.

## 5. Make forms understandable and recoverable

For forms and data-entry flows:

- keep visible, associated labels;
- ask only for information needed for the task;
- place instructions near the control they explain;
- validate at a useful time without punishing normal input;
- explain errors in plain language and identify how to fix them;
- preserve entered data after recoverable failures;
- show progress for multi-step flows;
- make required, optional, destructive, and irreversible actions clear.

Placeholder text is not a substitute for a persistent label.

## 6. Verify responsive behavior, not only breakpoints

Check representative narrow and wide layouts and any product-critical intermediate size.

Look for:

- horizontal overflow;
- clipped or hidden actions;
- unreadably dense tables/cards;
- controls that become too small or too close;
- navigation that becomes unusable;
- sticky elements that hide content or focus;
- dialogs/drawers that exceed the viewport;
- text wrapping that changes meaning or hierarchy.

Do not invent new breakpoints when the existing system already defines them unless evidence shows they are insufficient.

For web interfaces with reflow risk, include zoom/text-resize behavior and realistic content expansion when feasible. Check localization or RTL behavior when the product supports those contexts instead of treating English left-to-right content as the universal case.

## 7. Treat accessibility as a quality baseline

Apply the accessibility model of the actual platform.

- Web: use WCAG 2.2 AA as the default reference target when applicable, plus established web interaction patterns.
- Apple platforms: prefer native SwiftUI/UIKit semantics and controls, and check VoiceOver, Dynamic Type, focus, and platform modality.
- Android: prefer platform/Compose semantics and controls, and check TalkBack, text scaling, touch target guidance, keyboard/D-pad focus when relevant, and platform conventions.

Do not transplant web-only ARIA roles or keyboard models into native interfaces. Follow stricter project, platform, or legal requirements when provided.

At minimum inspect:

- whether native/project primitives can own the interaction before custom widget code;
- semantic structure and accessible names;
- keyboard reachability and logical focus order;
- visible, unobscured focus;
- labels/instructions and programmatic relationships;
- contrast and non-color-only meaning;
- pointer target size/spacing;
- error identification and recovery;
- motion/reduced-motion behavior when motion is used;
- screen-reader-relevant state changes when applicable.

Use [references/accessibility.md](references/accessibility.md) for the focused pass and platform-specific scope.

Automated accessibility tooling is useful evidence, but it does not prove usability or full conformance. For complex widgets, verify the expected keyboard and focus model against established platform/WAI-ARIA patterns rather than inventing interactions.

## 8. Review interaction quality

Check that the interface:

- gives immediate feedback after actions;
- prevents duplicate submission where material;
- makes destructive actions hard to trigger accidentally;
- uses confirmation only when consequence justifies interruption;
- supports cancel/back/undo where users reasonably need recovery;
- avoids surprise navigation or state loss;
- does not hide essential actions behind hover-only behavior;
- preserves user context after errors or retries.

Prefer predictable behavior over clever interaction.

Also verify **interaction truth**: visual state, accessibility state, application state, and the actual user-visible outcome should agree. A pressed/sorted/selected control that does not change the represented product state is still broken.

## 9. Preserve visual consistency

Review repeated patterns across the touched surface:

- spacing;
- typography;
- button hierarchy;
- input sizing;
- borders/radius/elevation;
- icon treatment;
- color semantics;
- card/table/list patterns;
- alignment;
- empty/error/loading presentation.

A repeated inconsistency may indicate a shared component or token problem. Fix the shared owner when that is the real cause.

### Avoid generic generated-looking sameness

Do not optimize only for "modern" or "clean." A polished UI can still feel generic when its structure, content, visual language, and motion could be swapped into many unrelated products.

When the brief asks for premium, expressive, distinctive, cinematic, or non-template design:

- define a product-specific visual direction before adding effects;
- use composition, typography, imagery, and real product content to create identity;
- reserve one or two signature moments instead of making every element compete;
- do not treat gradients, glass, rounded cards, oversized type, custom cursors, or 3D as automatic quality;
- do not fabricate product data, logos, testimonials, awards, or capabilities to make a screen look complete.

Use [references/premium-visual-direction.md](references/premium-visual-direction.md) for substantial expressive work.

### Treat motion and 3D as a system

When animation, sliding interactions, page transitions, scroll storytelling, or 3D are material:

- choose the smallest capable motion technology;
- give sliding interactions a coherent spatial model;
- prefer continuity/shared-element motion over repetitive decorative fade-ups;
- require reduced-motion behavior and a usable static/fallback state;
- treat smooth-scroll replacement as opt-in, not a premium default;
- require 3D to communicate a product/spatial idea and degrade gracefully;
- include animation/3D performance in the UX review.

Use [references/motion-3d.md](references/motion-3d.md) for the detailed selection and verification rules.

## 10. Inspect the rendered result

When UI/UX is the requirement, source inspection is insufficient.

When feasible, inspect the real interface with browser/runtime evidence such as:

- screenshots at representative viewport sizes and relevant themes/states;
- keyboard navigation;
- browser/e2e flows;
- accessibility tree or semantic inspection;
- real loading/error/empty states;
- interaction with actual shared components;
- zoom/reflow and content-stress checks when layout resilience is in scope;
- existing visual-regression/component-story evidence when the repository already provides it.

Use [references/rendered-verification.md](references/rendered-verification.md) to select evidence depth without installing unnecessary tooling.

If runtime evidence is unavailable, state that limitation instead of presenting code review as visual proof.

## 11. Prioritize by user impact

Rank findings using practical impact:

```text
severity ~= task blockage x frequency x recovery difficulty
```

Prioritize:

1. blocked or misleading core tasks;
2. inaccessible or unrecoverable interactions;
3. broken responsive/layout behavior;
4. confusing hierarchy or feedback;
5. cross-screen inconsistency;
6. cosmetic polish.

Do not spend the main effort on low-impact cosmetics while a core flow is confusing or inaccessible.

## 12. Keep ownership boundaries clear

This skill owns UI/UX quality judgment. Delegate when another workflow owns the deeper problem:

- feature/code placement -> `structure-feature`;
- source-to-consumed cross-layer audit -> `project-quality-orchestrator`;
- accessibility/security-sensitive implementation bug -> the appropriate engineering/security workflow;
- technical controlled prose -> `asd-ste100-writing`;
- final merge-readiness evidence -> `verify-change`.

Use only the specialist needed for the current phase.

## 13. Finish with evidence, not taste

For a substantial audit or redesign review, report:

- user task and surfaces reviewed;
- viewport/state coverage;
- high-impact findings with evidence;
- accessibility findings;
- design-system/shared-owner findings;
- fixes made or recommended;
- rendered/runtime checks actually performed;
- checks that could not be performed;
- remaining risk.

For each important finding prefer:

```text
location -> evidence -> user impact -> owning cause -> smallest correct repair -> verification
```

Do not label a personal aesthetic preference as a defect unless it violates an explicit product goal, design system, accessibility requirement, or measurable usability need.

Do not turn a heuristic review into invented user research, and do not hide a blocking defect behind an overall numeric UI score. Use scores only when the user explicitly asks for comparative scoring, and keep the underlying evidence and severe findings visible.

For the external standards/design-system rationale behind this workflow, load [references/research-basis.md](references/research-basis.md) only when provenance or methodology comparison is relevant.
