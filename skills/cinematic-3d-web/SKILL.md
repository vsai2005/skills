---
name: cinematic-3d-web
description: Build or improve premium cinematic web experiences that combine Three.js/WebGL, scroll-directed camera choreography, generated image plates or transparent foreground assets, lighting/materials/atmosphere, post-processing, responsive fallbacks, and screenshot-based visual iteration. Use for immersive 3D landing pages, architectural scenes, product worlds, editorial scroll stories, or fixing flat/generic AI-generated 3D.
---

# Cinematic 3D Web

Build the final frame, not merely a 3D scene.

The quality target is a coherent visual production system: art direction, camera composition, depth layering, real-time 3D, generated or photographed plates when useful, atmosphere, typography, interaction, performance, and rendered verification. Do not assume that more polygons, more bloom, or more shaders mean better work.

## 1. Classify the experience before building

Choose the smallest production mode that can satisfy the visual goal.

- Pure DOM/CSS: use when depth is decorative and real 3D adds no meaningful value.
- Focused Three.js moment: use for one hero object, product viewer, sculpture, globe, room, or short interactive scene.
- Scroll-directed 3D world: use when several narrative beats share one spatial world and camera path.
- Hybrid cinematic composition: use when the target frame needs more visual richness than real-time geometry alone can justify. Combine live 3D with image plates, alpha foregrounds, DOM typography, and restrained post-processing.
- Pre-rendered video: use when photographic realism and an exact camera path matter more than real-time interaction.

Do not build everything in WebGL by default. Use [references/hybrid-compositing.md](references/hybrid-compositing.md) when deciding which layer owns each visual element.

## 2. Write the visual contract

Before implementation, define:

- purpose and primary user action;
- focal subject;
- three mood words;
- world metaphor or setting;
- palette with one dominant field and at most one or two accents;
- camera language;
- foreground, midground, and background plan;
- typography relationship to the scene;
- motion grammar;
- target viewports and input types;
- reduced-motion behavior;
- WebGL failure fallback;
- performance class;
- asset provenance and reuse rights.

Do not begin with “make it cinematic.” Specify what the frame should communicate and how the eye should travel through it.

Use [assets/production-brief-template.md](assets/production-brief-template.md) for substantial work.

## 3. Design shots before geometry

Treat each major scroll state as a film shot.

For each shot, record:

- camera position and target;
- focal subject and silhouette;
- foreground framing;
- negative space reserved for copy;
- dominant light direction and color contrast;
- atmosphere density;
- visible scene layers;
- transition in and out;
- scroll weight or interaction trigger;
- mobile reinterpretation.

Build a 3–7 shot ledger before detailed modeling when the experience is scroll-driven.

Load [references/art-direction-shot-design.md](references/art-direction-shot-design.md) for shot composition, visual hierarchy, and camera planning.

## 4. Decompose the final frame into layers

Prefer a deliberate hybrid stack:

1. Background field, sky, distant environment, or image plate.
2. Real-time world geometry and primary subject.
3. Lighting, fog, particles, weather, and emissive effects.
4. Generated or photographed scene plates when they replace expensive distant detail.
5. Alpha foreground cutouts for branches, machinery, grass, debris, architecture, or framing.
6. DOM typography, navigation, labels, and controls.
7. Post-processing and subtle screen-space finish.

A layer must have a reason to exist. Do not hide weak composition behind grain, blur, bloom, particles, or glass.

## 5. Build in the correct order

Use this order unless the project provides a stronger local workflow:

1. Page and viewport contract.
2. Camera blockout.
3. Large silhouettes and scale.
4. Shot-to-shot spatial continuity.
5. Primary materials.
6. Key, fill, rim, practical, and environmental lighting.
7. Fog and atmospheric perspective.
8. Generated plates or foreground assets.
9. Post-processing.
10. Typography and UI.
11. Scroll or pointer choreography.
12. Responsive adaptation.
13. Performance tuning.
14. Rendered verification.

Do not spend time on micro-detail before the camera, silhouette, and light read correctly.

## 6. Treat camera and light as first-class systems

A scene can be technically complex and still look flat if the camera is generic.

Require:

- a clear focal length choice;
- intentional horizon and subject placement;
- foreground occlusion or framing when appropriate;
- camera targets independent from raw object origins;
- stable interpolation between authored shot states;
- lighting ratios that preserve dark areas instead of illuminating everything evenly.

Use [references/threejs-production.md](references/threejs-production.md) for scene, camera, scroll, resize, cleanup, and implementation rules.

Use [references/materials-lighting-atmosphere.md](references/materials-lighting-atmosphere.md) for material response, light hierarchy, fog, particles, and post-processing.

## 7. Generate assets as part of the composition

Generated imagery is not a substitute for scene design. Use it to solve specific layer problems.

Generate:

- distant environment plates;
- editorial stills;
- texture source material;
- transparent foreground framing;
- matte-painted extensions;
- posters or static fallbacks.

For every asset, preserve a consistent style preamble and record:

- purpose;
- model/provider;
- prompt;
- source reference;
- dimensions;
- transparency requirement;
- rights/reuse note;
- compression/export path.

Never claim generated imagery is live 3D. Never copy unlicensed reference artwork or code.

Load [references/asset-generation.md](references/asset-generation.md) for prompt patterns and asset QA.

## 8. Use one scroll conductor

For scroll-driven work, derive one normalized progress value or a small set of section-local progress values. Map those values to authored states.

Typical controlled properties:

- camera position;
- camera target;
- focal length;
- world rotation;
- light intensity or color;
- fog density;
- foreground opacity/blur;
- plate opacity;
- typography reveal;
- chapter navigation state.

Native document scrolling must remain reversible. Do not hijack the wheel merely to create drama.

Reduced motion must preserve the complete reading experience with stable states, still frames, or simplified transitions.

## 9. Use a rendered visual loop

Source inspection is not enough.

For each important viewport or shot:

1. Render the current implementation.
2. Capture a screenshot.
3. Compare against the approved visual contract or reference.
4. Classify the largest gap.
5. Fix the owning cause.
6. Re-render the same shot.
7. Repeat until no material gap remains.

Classify gaps as:

- composition;
- camera;
- silhouette;
- scale;
- lighting;
- material;
- atmosphere;
- layering;
- typography;
- motion;
- performance;
- responsive behavior.

Do not compensate for a camera problem with more geometry or for a lighting problem with more bloom.

Use [references/visual-verification-performance.md](references/visual-verification-performance.md).

## 10. Performance is part of visual quality

Start with a quality ladder, not one maximum setting.

High capability may enable higher DPR, shadows, heavier post-processing, denser particles, and richer reflections.

Lower capability should reduce the expensive dimensions first:

- pixel count;
- shadow resolution/count;
- particle density;
- post-processing passes;
- reflection/refraction cost;
- texture resolution;
- continuous animation.

Prefer adaptive render scale over removing the focal composition.

Pause or reduce work when the page is hidden or the 3D stage is off-screen. Dispose WebGL resources during teardown in application frameworks.

## 11. Preserve accessibility and product truth

The cinematic layer must not break the product.

Require:

- semantic DOM content outside the canvas;
- visible keyboard focus;
- readable contrast;
- usable mobile navigation;
- no essential hover-only interaction;
- reduced-motion behavior;
- a meaningful static/WebGL-failure fallback;
- alt text or equivalent semantics for meaningful non-decorative imagery;
- controls with accessible names.

Use ui-ux-quality for broader usability, responsive, and accessibility review.

## 12. Compose with other skills deliberately

Use other skills only when their ownership is needed:

- ui-ux-quality -> hierarchy, states, accessibility, responsive usability, rendered experience;
- source-grounded-development -> version-sensitive Three.js/R3F/WebGL APIs or external generation tooling;
- context-engineering -> large unfamiliar repos or noisy front-end codebases;
- structure-feature -> integrate the experience cleanly into an existing product;
- tiered-testing -> separate cheap render/build checks from heavy browser/GPU checks;
- independent-review -> fresh visual/technical review for high-risk launches;
- verify-change -> final evidence and merge-readiness.

This skill owns cinematic visual production logic. It does not replace those specialists.

## 13. Definition of done

Do not call the work complete because the scene renders.

For substantial work, require:

- visual contract;
- shot ledger;
- layer map;
- asset manifest;
- desktop and mobile behavior;
- reduced-motion/WebGL fallback;
- no failed local assets;
- no relevant console errors;
- stable forward and reverse scroll behavior;
- representative screenshots;
- performance evidence on at least one constrained profile when feasible;
- remaining limitations stated explicitly.

The final question is:

Does the rendered frame communicate the intended idea with deliberate composition, depth, light, material, and motion while remaining usable and performant?

If not, continue at the largest owning gap instead of adding random polish.
