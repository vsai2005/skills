# Art Direction and Shot Design

Use this reference when the scene is technically functional but visually generic, when several scroll chapters need one coherent visual language, or before expensive modeling.

## Start from the frame

A strong 3D web experience is designed from the viewer's frame inward.

Prioritize in this order:

1. focal subject;
2. silhouette;
3. camera angle and lens character;
4. foreground/midground/background separation;
5. light hierarchy;
6. negative space for copy;
7. material detail;
8. micro-effects.

If the first five are weak, additional detail usually increases noise rather than quality.

## Build a visual hierarchy

Every shot needs:

- one primary focal point;
- one supporting secondary feature at most;
- a clear dark/light structure;
- an intentional reading path;
- enough quiet area for text.

Avoid equal visual weight across the entire screen.

A useful composition test is to blur or squint at the frame. The major masses and focal light should still read.

## Use depth deliberately

Plan at least three depth bands when the concept allows it:

- foreground: framing, partial occlusion, texture, parallax;
- midground: subject and meaningful interaction;
- background: atmosphere, architecture, skyline, sky, distant plate.

Foreground elements are especially useful because small camera movement produces large parallax, creating depth without expensive geometry.

## Camera language

Choose a coherent camera grammar rather than arbitrary positions.

Examples:

- low dolly forward -> monumental, entering;
- lateral track -> observational, editorial;
- crane up/down -> reveal scale or hierarchy;
- slow orbit -> sculptural/product focus;
- narrow lens through foreground -> compressed, cinematic;
- wider lens close to subject -> immersive, spatial.

Avoid default camera.position = (0, 2, 5) as a final authored shot.

## Focal length is art direction

A wide field of view exaggerates depth and makes close foreground objects dominant. A narrower field compresses space and can make architecture or landscapes feel more photographic.

Choose focal character first, then reposition the camera. Do not use field of view only to “fit everything.”

## Negative space is part of the scene

If copy sits over a 3D world, reserve a quiet zone in the composition.

Do not solve every collision with dark CSS gradients after the fact. Move the camera, subject, or light so the scene naturally supports the text.

## Shot continuity

For scroll worlds, consecutive shots should feel like one journey.

Preserve at least one continuity anchor where possible:

- same landmark;
- same horizon;
- same dominant light;
- same motion direction;
- same world axis;
- same foreground motif.

Hard changes are allowed when narratively earned, but random camera teleporting makes the experience feel like disconnected demos.

## Shot ledger quality checks

For every shot, ask:

- What is the first thing the eye sees?
- Why is the camera here?
- What is in front of the subject?
- What is behind it?
- Where can text safely live?
- Where is the brightest region?
- Which surfaces should remain dark?
- What changes from the previous shot?
- What remains continuous?
- What is the simpler mobile interpretation?

If the answers are vague, the shot is not ready for detailed production.

## Mobile reinterpretation

Do not merely crop a desktop composition.

Mobile may require:

- closer camera;
- simpler silhouette;
- different foreground framing;
- text moved above/below the visual stage;
- reduced parallax;
- fewer simultaneous layers;
- shallower depth;
- static keyframes instead of continuous motion.

Preserve the story and focal hierarchy, not identical pixel placement.
