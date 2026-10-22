# Hybrid 2D/3D Compositing

Use this reference when pure Three.js looks empty, overly synthetic, too expensive, or when the target has cinematic detail that does not need to be interactive geometry.

## The main principle

Do not ask one renderer to own every pixel.

A premium browser frame can combine:

- WebGL geometry for spatial elements that need parallax, lighting, or interaction;
- still image plates for distant detail;
- alpha foreground cutouts for framing and near-camera richness;
- DOM for crisp accessible typography and controls;
- CSS for masks, scrims, grain, blur handoffs, and simple compositing;
- video only when the exact photographic motion is more valuable than real-time control.

## Decide ownership by behavior

Use WebGL when an element must:

- move correctly in 3D;
- cast/receive light or shadow;
- respond to camera parallax;
- rotate or deform;
- participate in interaction;
- anchor spatial continuity.

Use an image plate when an element is:

- distant;
- mostly static;
- detail-dense;
- expensive to model;
- not required to react physically;
- better represented as art direction than simulation.

Use an alpha foreground when an element:

- frames the viewport;
- creates strong parallax with small movement;
- needs organic complexity;
- can remain billboard-like without exposing the illusion.

Use DOM when content must remain semantic, selectable, navigable, focusable, or responsive.

## Layer order

A common stack is:

background field or distant plate
-> 3D world
-> atmospheric WebGL
-> midground plate or decorative card
-> alpha foreground
-> DOM content
-> subtle screen-space finish

This order is not mandatory. The rule is that depth cues must agree.

## Match the layers

The hybrid illusion fails when the plate and 3D world disagree.

Match:

- perspective;
- horizon;
- dominant light direction;
- color temperature;
- fog/haze;
- grain/sharpness;
- black level;
- motion amount;
- scale cues.

If a generated foreground is razor sharp while the 3D midground is foggy, it may look pasted on unless that sharpness is intentional.

## Use occlusion to hide complexity

Foreground objects can deliberately cover transitions, low-detail geometry, or layer seams. This is normal cinematography, not a hack, when the composition remains coherent.

## Plate motion

Do not over-animate still plates.

Use small controlled movement:

- 1–4% scale drift;
- slight translate tied to camera;
- opacity/fog handoff;
- small blur change;
- mask reveal.

Large fake parallax exposes the flatness.

## Foreground motion

Near-camera cutouts can use:

- stronger parallax;
- small wind displacement;
- section-local fade/blur;
- subtle rotation;
- pinned presence during one shot.

Avoid having every layer float independently.

## Cards and editorial windows

A flat generated still can feel integrated when:

- its color grade matches the world;
- its practical light is echoed by live CSS/WebGL glow;
- the frame uses scene-consistent borders/materials;
- movement is restrained;
- it appears at a meaningful narrative beat.

Do not present a static image as a live 3D viewport if it is not one.

## Quality traps

Avoid:

- making all distant scenery 3D “because it is a 3D site”;
- using random foreground PNGs without matching light;
- large translucent glass panels hiding the scene;
- identical blur on every handoff;
- too many independent parallax rates;
- bloom on image plates that already contain baked bloom;
- plate text/logos accidentally generated into art.

The goal is one believable final composition, not proof that every layer uses the same technology.
