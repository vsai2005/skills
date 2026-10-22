---
name: cinematic-3d-web
description: Build cinematic Three.js/WebGL sites with shot design, hybrid layers, scroll, and QA.
---

# Cinematic 3D Web

Build the final frame, not merely a 3D scene. Coordinate art direction, camera, layers, atmosphere, motion, performance, and rendered verification.

## 1. Choose the production mode

Use the smallest capable mode:

- DOM/CSS for decorative depth.
- Focused Three.js for one interactive hero or spatial object.
- Scroll-directed 3D world when several beats share one continuous space.
- Hybrid composition when live 3D benefits from plates, alpha foregrounds, or DOM.
- Pre-rendered video when exact photographic motion matters more than real-time control.

Do not force every pixel into WebGL. Use [references/hybrid-compositing.md](references/hybrid-compositing.md) when layer ownership is unclear.

## 2. Define the visual contract

Before detailed implementation, record:

- purpose, primary action, and focal subject;
- three mood words, world/setting, palette, and material language;
- camera language and foreground/midground/background plan;
- typography relationship and motion grammar;
- target viewports/inputs;
- reduced-motion and WebGL-failure behavior;
- performance class;
- asset provenance and reuse rights.

Use [assets/production-brief-template.md](assets/production-brief-template.md) for substantial work.

## 3. Design shots before geometry

For each important scroll state define:

- camera position, target, and lens/FOV character;
- focal subject/silhouette;
- depth bands and foreground framing;
- negative space for copy;
- dominant light direction/temperature;
- atmosphere;
- transition, scroll weight/trigger, and mobile reinterpretation.

For scroll worlds, create a 3–7 shot ledger before detailed modeling. Use [references/art-direction-shot-design.md](references/art-direction-shot-design.md).

## 4. Compose in layers

A useful hybrid stack:

1. background field, sky, distant environment, or plate;
2. real-time geometry and primary subject;
3. fog, particles, weather, and emissive effects;
4. generated/photographed plates for dense static detail;
5. alpha foregrounds for near-camera framing;
6. semantic DOM typography/navigation/controls;
7. restrained post-processing.

Every layer needs a role; effects must not conceal weak composition.

## 5. Build in visual-priority order

Prefer:

1. viewport/page contract;
2. camera blockout;
3. silhouettes and scale;
4. shot continuity;
5. materials;
6. key/fill/rim/practical/environment lighting;
7. fog and atmospheric perspective;
8. generated plates/foregrounds;
9. post-processing;
10. typography/UI;
11. scroll/pointer choreography;
12. responsive adaptation;
13. performance tuning;
14. rendered verification.

Do not spend on micro-detail before camera, silhouette, scale, and light read correctly.

Use [references/threejs-production.md](references/threejs-production.md) for renderer/camera/scroll/lifecycle rules and [references/materials-lighting-atmosphere.md](references/materials-lighting-atmosphere.md) for visual systems.

## 6. Author camera, light, and scroll as systems

Author shot states as data. Keep camera position, look target, focal character, light/fog state, and world state explicit.

For scroll work, derive one normalized progress source or a small set of section-local values. Map camera, target, lights, fog, foregrounds, plates, and UI from that conductor. Native document scrolling must remain reversible.

Reduced motion must preserve the full reading experience with stable keyframes, stills, or simplified transitions.

## 7. Generate assets for explicit roles

AI imagery is a production layer, not a substitute for scene design. Useful roles include concept frames, plates, transparent foregrounds, texture sources, and static posters.

Keep a stable style preamble across related assets. Record purpose, model/provider, prompt/reference, dimensions, transparency, edits, rights, and final path.

Never present a still as live 3D or copy unlicensed reference code/artwork. Use [references/asset-generation.md](references/asset-generation.md).

## 8. Iterate from rendered evidence

Source review is not visual proof. For each important shot/view:

1. capture the implementation;
2. compare with the approved contract/reference;
3. classify the largest gap;
4. fix its owning cause;
5. re-render the same shot;
6. repeat until no material gap remains.

Classify gaps as composition, camera, silhouette, scale, lighting, material, atmosphere, layering, typography, motion, performance, or responsiveness.

Do not repair a camera problem with more geometry or a lighting problem with more bloom. Use [references/visual-verification-performance.md](references/visual-verification-performance.md).

## 9. Treat performance as visual quality

Use a quality ladder. Tune expensive dimensions first:

- render scale/DPR;
- shadow count/resolution;
- particle density;
- post-processing passes;
- reflection/refraction cost;
- texture resolution;
- continuous animation frequency.

Preserve focal composition while reducing invisible GPU cost. Pause/reduce work when hidden or off-screen and dispose WebGL resources when lifecycle requires it.

## 10. Preserve product usability

Keep semantic DOM content, visible focus, usable mobile navigation, readable contrast, reduced motion, accessible controls, and a meaningful WebGL fallback. Essential actions must not depend on hover or the 3D renderer.

Use `ui-ux-quality` for broader responsive, accessibility, and usability review.

## 11. Compose with specialists only when needed

- `ui-ux-quality` -> hierarchy, states, accessibility, responsive usability.
- `source-grounded-development` -> version-sensitive Three.js/R3F/WebGL or generation APIs.
- `context-engineering` -> unfamiliar/noisy repositories.
- `structure-feature` -> integration into existing product architecture.
- `tiered-testing` -> cheap vs heavy browser/GPU verification.
- `independent-review` -> fresh high-risk visual/technical review.
- `verify-change` -> final evidence and merge readiness.

This skill owns cinematic production reasoning, not those specialists' domains.

## 12. Definition of done

For substantial work require:

- visual contract, shot ledger, and layer map;
- asset/provenance manifest;
- desktop/mobile behavior;
- reduced-motion/WebGL fallback;
- no failed required assets or relevant console errors;
- stable forward/reverse scroll;
- representative rendered screenshots;
- constrained-device/performance evidence when feasible;
- explicit remaining limitations.

Completion test: does the rendered frame communicate the idea through deliberate composition, depth, light, material, and motion while remaining usable and performant?

If not, repair the largest owning gap instead of adding random polish.

Load [references/research-basis.md](references/research-basis.md) only when provenance, reference boundaries, or Kage/MengTo attribution is relevant.
