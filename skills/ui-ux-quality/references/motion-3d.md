# Motion, Sliding Interactions, and 3D

Use this reference when the brief calls for meaningful animation, page transitions, sliding interactions, scroll storytelling, immersive visuals, or 3D.

## 1. Motion carries a burden of proof

Start with the user/product purpose.

Motion can:

- preserve spatial continuity;
- explain cause and effect;
- reveal hierarchy;
- show state change;
- guide attention;
- make direct manipulation feel physical;
- communicate progress;
- support narrative storytelling;
- demonstrate a spatial/3D product.

Motion should not:

- delay routine actions;
- hide content behind unnecessary choreography;
- make scrolling harder;
- compete with reading;
- replace status/error clarity;
- exist only because the library is installed.

## 2. Choose the smallest capable motion layer

Use this hierarchy:

```text
no animation
  -> CSS transition/keyframes
  -> native browser animation/view-transition APIs
  -> Motion for React component/layout/gesture motion
  -> GSAP for complex timelines/ScrollTrigger/SVG/scene choreography
  -> Three.js / React Three Fiber for actual 3D
  -> specialist authored-asset runtimes only when the asset/workflow requires them
```

Do not install a heavier engine when a lower layer already solves the interaction.

Do not let two animation engines control the same property on the same element.

## 3. Motion grammar must be coherent

Define a small motion system:

- durations by interaction scale;
- easing/spring character;
- entrance/exit relationship;
- direction rules;
- distance/scale limits;
- stagger behavior;
- reduced-motion behavior.

Repeated interactions should feel like the same product.

Avoid a page where every component uses a different easing, duration, direction, and bounce style.

## 4. Sliding interactions need spatial logic

Drawers, sheets, tabs, carousels, slides, and panels should move according to a stable spatial model.

Examples:

- side drawer -> enters from the side it occupies;
- bottom sheet -> rises from the bottom;
- master-detail -> preserves directional continuity;
- carousel -> movement follows ordering;
- dismiss -> reverses or logically completes entry;
- route transition -> preserves the relationship between origin and destination when useful.

Do not make motion direction arbitrary.

## 5. Prefer continuity over decorative entrances

Useful advanced patterns include:

- shared-element/layout transitions;
- FLIP-style reordering;
- expanding card -> detail continuity;
- image/product morphs;
- contextual route transitions;
- progressive disclosure tied to user action.

These often feel more premium than making every section fade upward.

## 6. Scroll storytelling is opt-in

Use scroll-linked choreography for story-led surfaces such as:

- product launches;
- portfolios;
- explainers;
- interactive case studies;
- spatial/technical narratives.

Possible patterns:

- pinned stages;
- progress-linked diagrams;
- image/video/3D state changes;
- restrained parallax;
- horizontal story segments when the content model clearly supports them;
- text/image sequencing tied to narrative progress.

Avoid replacing native scrolling by default. Smooth-scroll libraries can affect keyboard paging, find-in-page, scroll anchoring, assistive technology, and vestibular comfort.

If custom/smoothed scrolling is justified, verify native-feeling navigation, keyboard behavior, anchor links, reduced motion, mobile behavior, and fallback.

## 7. 3D must communicate something

Good uses:

- product viewer/configurator;
- architecture/spatial explanation;
- scientific/technical visualization;
- maps/worlds;
- interactive object inspection;
- branded hero where spatial depth is central to the visual concept.

Usually poor defaults:

- checkout;
- settings;
- ordinary forms;
- routine CRUD/admin;
- dense operational dashboards;
- core accessibility-critical tasks without an equivalent non-3D representation.

Before adding 3D, answer:

1. What does depth help the user understand or feel?
2. What is the 2D/static fallback?
3. Does the main task remain usable before/without WebGL?
4. What is the low-power/mobile strategy?
5. What happens under reduced motion?
6. Is the scene worth the bundle, GPU, memory, and asset cost?

## 8. 3D performance is part of UX

For Three.js/R3F work, consider:

- lazy/progressive asset loading;
- compressed and appropriately sized textures/models;
- resource reuse;
- instancing repeated geometry;
- level of detail;
- avoiding unnecessary continuous renders;
- adaptive device pixel ratio/quality;
- reducing expensive post-processing on weaker devices;
- pausing work when hidden/off-screen;
- avoiding React state updates every frame for animation values.

For mostly static R3F scenes, on-demand rendering can save battery/GPU work.

Test on representative weaker hardware, not only a developer machine.

## 9. Animation performance rules

Prefer compositor-friendly transforms and opacity for common DOM motion.

Avoid repeated layout thrashing or unnecessary animation of layout-heavy properties when transforms can express the same result.

For complex timelines:

- sequence rather than start hundreds of effects at once;
- clean up timelines/listeners/triggers on unmount/navigation;
- keep per-frame work outside unnecessary component re-renders;
- pause inactive/off-screen animation;
- verify mobile and low-power behavior.

A visually impressive interaction that drops frames or heats the device is not premium.

## 10. Reduced motion changes the experience, not only duration

When users request reduced motion:

- remove or simplify large spatial movement, parallax, spinning, zooming, and continuous motion;
- keep state changes understandable;
- prefer fades/instant changes where appropriate;
- preserve the same content and task result;
- stop decorative autoplay/loops when needed.

Do not merely multiply every duration by 0.5 and call it accessible.

## 11. Performance/fallback contract for expressive surfaces

For every major cinematic/3D feature, document:

```text
primary experience
-> reduced-motion version
-> low-capability/mobile version
-> unsupported/failed-render fallback
```

The fallback should still communicate the product.

## 12. Technology selection

Reuse the project's installed stack first.

Typical fit:

| Need | Prefer |
| --- | --- |
| hover/press/simple reveal | CSS |
| React enter/exit, layout, shared element, gesture | Motion |
| complex dependent timeline | GSAP |
| scroll pin/scrub/story choreography | GSAP ScrollTrigger |
| real WebGL scene | Three.js |
| React-owned Three.js scene | React Three Fiber |
| simple state-to-state browser transition | native View Transitions when support/fallback fits |

These are selection heuristics, not mandatory dependencies.

## 13. Verify motion in the real product

Check at least the important applicable cases:

- normal interaction;
- fast repeated interaction/interruption;
- back/forward or route changes;
- mobile/touch;
- keyboard;
- reduced motion;
- resize/orientation;
- slow asset load;
- lower-capability device;
- off-screen/inactive behavior;
- 3D/rendering failure fallback.

Do not approve motion from a code diff alone.
