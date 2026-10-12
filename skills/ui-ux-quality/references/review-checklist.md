# UI/UX Review Checklist

Use this reference for a broad product-interface review. Apply only sections relevant to the surface being changed.

## Purpose and hierarchy

- Can a user identify the page purpose quickly?
- Is the primary action clear?
- Are secondary/destructive actions visually subordinate or separated appropriately?
- Do headings, grouping, and order match the user's task sequence?
- Is important status visible without forcing the user to infer it?
- Is dense information progressively disclosed when possible?

## Usability heuristics

Use the detailed [usability and design-system review](usability-design-system.md) when needed. For a quick pass, ask:

- Does the interface communicate current system status?
- Does it use the user's language and familiar concepts?
- Can users cancel, go back, undo, or recover where appropriate?
- Does it follow established conventions instead of creating new ones without reason?
- Does it prevent likely mistakes before showing an error?
- Does it expose choices/context so users recognize rather than memorize?
- Does it provide efficient repeated use where the product needs it?
- Is the screen focused on information needed for the task?

Do not claim these questions substitute for observing real users.

## Navigation and orientation

- Is the current location understandable?
- Are back/cancel paths predictable?
- Do labels use the user's language instead of internal implementation terms?
- Are repeated navigation patterns consistent?
- Does navigation still work with keyboard and narrow layouts?

## Forms

- Visible persistent labels are present.
- Required/optional expectations are clear.
- Instructions appear before or near the decision they affect.
- Validation messages identify the field/problem and useful recovery.
- Entered data survives recoverable errors.
- Submit controls expose loading/disabled state appropriately.
- Duplicate submission is prevented when material.
- Sensitive/destructive actions communicate consequence.

## Feedback and system status

Check relevant states:

- initial/default;
- loading;
- empty;
- partial data;
- success;
- validation error;
- server/network error;
- permission denied;
- offline/slow dependency;
- retry;
- destructive confirmation.

The UI should not leave the user guessing whether an action happened.

## Responsive behavior

At representative narrow and wide sizes, check:

- overflow;
- clipping;
- wrapping;
- fixed/sticky overlays;
- tables and dense data;
- navigation collapse;
- dialogs/drawers;
- touch/pointer targets;
- control ordering;
- visibility of primary actions.

## Consistency and semantic intent

Compare equivalent components for:

- spacing and alignment;
- typography;
- button hierarchy;
- control height;
- icon style;
- radius/elevation;
- color semantics;
- loading/empty/error patterns;
- terminology;
- semantic role of primary, secondary, destructive, warning, success, selected, and disabled states.

A token or component that merely looks similar is not automatically the correct semantic choice.

When several screens share the same defect, inspect the shared component/token/template before patching each instance.

## Trust and error prevention

- Risky actions clearly state consequence.
- Irreversible actions require proportionate friction.
- Confirmations are not overused for harmless actions.
- Important user work is not silently discarded.
- Retry behavior does not create duplicate value-changing actions.
- Success messages do not claim completion before the operation is actually committed.

## Content and internationalization resilience

When relevant, check:

- long labels and translated-string expansion;
- numbers, dates, and text direction;
- RTL layout and directional icons;
- 200% zoom/text growth;
- light/dark or multi-brand themes;
- high-contrast/forced-color behavior where supported.

## Evidence

Prefer rendered/browser evidence for user-facing claims. Record which viewport, state, input method, interaction path, theme, and content stress case were actually checked.

Distinguish:
- **observed defect** from rendered/runtime evidence;
- **standards violation** from a cited rule or project contract;
- **usability hypothesis** that still needs user evidence;
- **aesthetic preference** that should not be reported as a defect.
