---
name: cinematic-3d-web
description: Build or improve cinematic web experiences with Three.js/WebGL, authored scroll camera shots, hybrid 3D plus image/foreground layers, lighting/materials/atmosphere, AI visual assets, responsive fallbacks, and screenshot-driven iteration. Use for immersive landing pages, product worlds, or flat AI 3D.
---

# Cinematic 3D Web

Build the final frame, not merely a 3D scene.

Use this skill when visual quality depends on coordinated art direction, camera composition, real-time 3D, layered imagery, atmosphere, motion, performance, and rendered verification. More polygons, bloom, particles, or shaders are not substitutes for composition.

## 1. Choose the production mode

Use the smallest capable mode:

- DOM/CSS when depth is decorative.
- Focused Three.js for one interactive hero, product, room, sculpture, or spatial object.
- Scroll-directed 3D world when several narrative beats share one continuous space.
- Hybrid cinematic composition when live 3D should be enriched with image plates, alpha foregrounds, or DOM layers.
- Pre-rendered video when exact photographic motion matters more than real-time control.

Do not force every visible detail into WebGL. Load [references/hybrid-compositing.md](references/hybrid-compositing.md) when layer ownership is uncertain.

## 2. Define the visual contract

Before detailed implementation, record:

- page purpose and primary action;
- focal subject and three mood words;
- world/setting and palette;
- material language;
- camera language;
- foreground, midground, and background plan;
- typography relationship to the scene;
- motion grammar;
- target viewports/inputs;
- reduced-motion and WebGL-failure behavior;
- performance class;
- asset provenance and reuse rights.

Use [assets/production-brief-template.md](assets/production-brief-template.md) for substantial work.

## 3. Design shots before geometry

Treat each important scroll state as a film shot. For every shot define:

- camera position, target, and lens/FOV character;
- focal subject and silhouette;
- foreground framing and depth bands;
- negative space for copy;
- dominant light direction/temperature;
- atmosphere;
- transition to the next shot;
- scroll weight or trigger;
- mobile reinterpretation.

For a scroll world, build a 3–7 shot ledger before detailed modeling. Load [references/art-direction-shot-design.md](references/art-direction-shot-design.md).

## 4. Compose the final frame in layers

A useful hybrid stack is:

1. background field, sky, distant environment, or plate;
2. real-time geometry and primary subject;
3. fog, particles, weather, and emissive effects;
4. generated or photographed scene plates where dense static detail is cheaper;
5. alpha foregrounds for near-camera framing;
6. semantic DOM typography, navigation, labels, and controls;
7. restrained post-processing/screen-space finish.

Every layer needs a role. Do not hide weak camera or lighting behind blur, grain, glow, or particles.

## 5. Build in visual-priority order

Prefer:

1. viewport/page contract;
2. camera blockout;
3. large silhouettes and scale;
4. shot continuity;
5. primary materials;
6. key/fill/rim/practical/environment lighting;
7. fog and atmospheric perspective;
8. generated plates/foreground assets;
9. post-processing;
10. typography/UI;
11. scroll or pointer choreography;
12. responsive adaptation;
13. performance tuning;
14. rendered verification.

Do not spend on micro-detail before camera, silhouette, scale, and light read correctly.

Use [references/threejs-production.md](references/threejs-production.md) for renderer/camera/scroll/lifecycle rules and [references/materials-lighting-atmosphere.md](references/materials-lighting-atmosphere.md) for the visual systems.

## 6. Author camera, light, and scroll as systems

Avoid a generic final camera such as a centered default position looking at the origin. Author shot states as data and keep camera position, look target, focal character, light/fog state, and world state explicit.

For scroll-driven work, derive one normalized progress source or a small set of section-local progress values. Map camera, target, lights, fog, foregrounds, plates, and UI state from that conductor. Native document scrolling must remain reversible.

Reduced motion must preserve the full reading experience with stable keyframes, stills, or simplified transitions.

## 7. Generate assets for explicit compositing roles

AI imagery is a production layer, not a replacement for scene design.

Useful roles include:

- concept frame;
- distant environment plate;
- editorial still;
- transparent foreground framing;
- texture source;
- matte extension;
- reduced-motion/static poster.

Keep a stable style preamble across related assets. Record purpose, model/provider, prompt/reference, dimensions, transparency, edits, rights, and final path.

Never present a still plate as live 3D. Never copy unlicensed reference code or artwork. Load [references/asset-generation.md](references/asset-generation.md).

## 8. Iterate from rendered evidence

Source review is not visual proof.

For each important shot and viewport:

1. capture the implementation;
2. compare with the approved contract/reference;
3. classify the largest gap;
4. fix its owning cause;
5. re-render the same shot;
6. repeat until no material gap remains.

Classify gaps as composition, camera, silhouette, scale, lighting, material, atmosphere, layering, typography, motion, performance, or responsive behavior.

Do not repair a camera problem with more geometry or a lighting problem with more bloom.

Load [references/visual-verification-performance.md](references/visual-verification-performance.md).

## 9. Treat performance as visual quality

Use a quality ladder rather than one maximum setting. Tune the expensive dimensions first:

- render scale/DPR;
- shadow count/resolution;
- particle density;
- post-processing passes;
- reflection/refraction cost;
- texture resolution;
- continuous animation frequency.

Prefer preserving the focal composition while reducing invisible GPU cost. Pause or reduce work when hidden/off-screen and dispose WebGL resources when the app lifecycle requires it.

## 10. Preserve product usability

The cinematic layer must not break the product. Keep semantic DOM content outside the canvas, visible focus, usable mobile navigation, readable contrast, accessible control names, reduced motion, and a meaningful static/WebGL-failure fallback. Essential actions must not depend on hover or the 3D renderer.

Use `ui-ux-quality` for broader responsive, accessibility, and usability review.

## 11. Compose with specialist skills only when needed

- `ui-ux-quality` -> hierarchy, states, accessibility, responsive usability.
- `source-grounded-development` -> version-sensitive Three.js/R3F/WebGL or generation APIs.
- `context-engineering` -> unfamiliar/noisy repositories.
- `structure-feature` -> integration into an existing product architecture.
- `tiered-testing` -> cheap vs heavy browser/GPU verification.
- `independent-review` -> fresh high-risk visual/technical review.
- `verify-change` -> final evidence and merge readiness.

This skill owns cinematic production reasoning, not those specialists' domains.

## 12. Definition of done

For substantial work, require:

- visual contract;
- shot ledger;
- layer map;
- asset/provenance manifest;
- desktop and mobile behavior;
- reduced-motion/WebGL fallback;
- no failed required assets or relevant console errors;
- stable forward/reverse scroll behavior;
- representative rendered screenshots;
- constrained-device/performance evidence when feasible;
- explicit remaining limitations.

The completion question is simple: does the rendered frame communicate the intended idea through deliberate composition, depth, light, material, and motion while remaining usable and performant?

If not, repair the largest owning gap instead of adding random polish.

Load [references/research-basis.md](references/research-basis.md) only when provenance, reference boundaries, or Kage/MengTo attribution questions are relevant.
