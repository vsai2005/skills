# Visual Verification and Performance

Use this reference after the first working render and during every major polish pass.

## The rendered loop

For each authored shot:

1. capture the target/reference;
2. capture the implementation at the same viewport;
3. compare major visual categories;
4. choose the largest owning gap;
5. make one coherent repair;
6. re-render the same shot;
7. repeat.

Do not change five unrelated visual systems between comparisons unless the root cause spans them.

## Gap taxonomy

### Composition
Symptoms:
- focal point unclear;
- visual weight scattered;
- copy collides with subject;
- empty or crowded regions feel accidental.

Owners:
camera, subject placement, layer framing, typography layout.

### Camera
Symptoms:
- generic game-camera feel;
- wrong scale;
- too much distortion;
- scene looks like a model viewer rather than a shot.

Owners:
FOV/focal length, position, target, horizon, near foreground.

### Lighting
Symptoms:
- everything equally visible;
- no focal contrast;
- black materials with bright ambient wash;
- random colored lights.

Owners:
light hierarchy, exposure, environment, material roughness.

### Material
Symptoms:
- plastic look;
- wrong texture scale;
- surfaces have identical roughness;
- reflections do not fit the world.

Owners:
PBR values, maps, UV scale, environment.

### Atmosphere
Symptoms:
- no depth separation;
- particles feel decorative;
- distant background too sharp;
- fog hides everything equally.

Owners:
fog curve, particle volume, light/fog color relationship.

### Layer integration
Symptoms:
- generated plate looks pasted on;
- foreground edge mismatch;
- inconsistent grain/black level;
- parallax exposes flatness.

Owners:
perspective, color grade, sharpness, motion amplitude, masks.

### Motion
Symptoms:
- scroll feels floaty;
- reverse scroll differs;
- too many simultaneous animations;
- camera never settles.

Owners:
progress mapping, easing, section timing, state source of truth.

## Viewport matrix

At minimum for substantial public work, verify representative:

- narrow mobile around 390 px;
- tablet/intermediate around 768 px;
- desktop around 1024–1440 px;
- any product-critical breakpoint.

Check orientation changes when mobile landscape matters.

## Performance ladder

Treat quality as tiers.

Example dimensions:

- render scale/DPR;
- shadow count/resolution;
- post-processing passes;
- particle draw range;
- reflection/refraction updates;
- texture resolution;
- animation frequency.

Reduce the most expensive invisible dimension first.

## Frame-time thinking

Do not optimize only by triangle count.

Cinematic scenes can be fill-bound due to:

- high DPR;
- transparent layers;
- full-screen post-processing;
- bloom chains;
- particles;
- large overdraw;
- multiple render targets.

Measure before deciding the bottleneck.

## Adaptive quality

A useful adaptive controller can:

- sample frame time over a stable window;
- reduce render scale after sustained poor performance;
- recover slowly after sustained headroom;
- clamp to minimum/maximum quality;
- avoid oscillating every few frames.

Do not let adaptation visibly change composition.

## Browser evidence

Record what was actually checked:

- load;
- console;
- network/local assets;
- anchor navigation;
- forward/reverse scroll;
- fast flick;
- resize;
- mobile menu;
- reduced motion;
- WebGL fallback;
- representative screenshots;
- constrained performance when feasible.

A source-code review is not proof that the rendered experience looks correct.

## Completion rule

Stop adding effects when the frame already meets the visual contract.

The final pass should usually remove or reduce something:

- redundant glow;
- extra particle layer;
- unnecessary blur;
- excessive parallax;
- duplicate foreground;
- expensive shadow;
- noisy copy transition.

Restraint is part of premium visual quality.
