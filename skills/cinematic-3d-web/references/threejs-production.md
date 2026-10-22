# Three.js Production Rules

Use this reference for the real-time scene, camera system, renderer lifecycle, and scroll choreography.

## Scene architecture

Prefer a small number of stable systems:

- renderer;
- scene;
- authored camera rig;
- world root;
- lighting root;
- atmosphere/FX root;
- asset registry;
- scroll/interaction conductor;
- quality controller.

Do not create unrelated render loops for every visual effect.

## Camera rig

Separate:

- camera position;
- camera look target;
- optional roll;
- focal length/FOV;
- section-specific offsets.

Author shot states as data, not scattered magic numbers.

A shot can conceptually contain:

position
target
fov
lightState
fogState
worldState
foregroundState

Interpolate between complete states with easing that does not change endpoints.

## Scroll choreography

Use native document scroll.

Compute normalized progress from stable DOM boundaries. Prefer requestAnimationFrame-coalesced updates rather than doing heavy scene work directly in the scroll event.

For chaptered pages:

- calculate each section's local progress;
- select the active transition;
- interpolate from shot A to B;
- derive nav/foreground state from the same source of truth.

Backward scroll must reconstruct prior states exactly.

## Resize and viewport truth

Use the actual layout viewport dimensions used by CSS. Update:

- renderer size;
- render target sizes;
- camera aspect/projection;
- resolution-dependent shader uniforms;
- layout-derived scissor rectangles.

Mobile browser chrome and viewport behavior can make window.innerWidth/innerHeight misleading in some layouts. Verify the actual CSS box instead of assuming.

## Device pixel ratio

Do not render at unbounded devicePixelRatio.

Start with a cap appropriate to the project and adapt down when GPU time is poor. Pixel count often dominates fill-heavy cinematic scenes.

Treat DPR as a quality dial.

## Shadows

Use shadows only where they change the composition.

Common strategy:

- one important shadow-casting directional/spot light;
- low-cost practical lights without shadows;
- baked or fake contact shadows for minor objects;
- lower shadow map resolution on mobile.

Multiple soft shadow lights can destroy frame time quickly.

## Materials and textures

Share geometry/materials/textures when repeated.

Use texture compression and sensible dimensions. Avoid several 4K maps for objects that never occupy more than a small part of the screen.

Dispose resources when replacing scenes or unmounting routes.

## Particles and weather

Anchor dense effects where the camera can actually see them.

Prefer pooled buffers and draw-range/density control to constant allocation.

Use the scene's motion grammar. Particles are atmosphere, not confetti.

## Post-processing

Keep the chain short.

Typical cinematic needs can often be met with:

- tone mapping/color treatment;
- restrained bloom;
- vignette;
- grain;
- optional depth/fog treatment.

Do not stack expensive effects until you have measured the need.

## Render loop policy

Render continuously only when something visibly changes.

Possible modes:

- continuous: particles/weather/ambient animation;
- demand: product viewer at rest;
- scroll-active: update while scrolling and briefly settle;
- visibility-gated: pause when page hidden/off-screen.

A hybrid page should not burn the GPU merely because WebGL exists.

## Failure and reduced motion

If WebGL initialization fails:

- keep semantic page content;
- show an authored poster or plate;
- hide broken controls;
- avoid blank black canvases.

For reduced motion:

- stop continuous camera travel;
- use stable keyframes;
- reduce or remove particle motion;
- preserve content order and scene identity.

## Debug controls

During production, temporary controls can expose:

- camera coordinates/FOV;
- shot index/progress;
- quality tier;
- DPR;
- draw calls/triangles;
- light toggles;
- fog density;
- post-processing toggles.

Remove or gate them before shipping.

## Validation

Verify:

- resize;
- orientation change;
- fast scroll flick;
- reverse scroll;
- browser back/anchor navigation;
- WebGL failure path;
- reduced motion;
- hidden-tab pause;
- no resource leaks after route transitions when applicable;
- no missing local assets or console errors.
