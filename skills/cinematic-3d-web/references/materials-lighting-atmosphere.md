# Materials, Lighting, Atmosphere, and Finish

Use this reference when a scene feels like plastic, evenly lit, game-prototype-like, or visually shallow.

## Material response before material complexity

A material reads through its response to light.

For important surfaces, consider:

- base color/albedo;
- roughness;
- normal variation;
- metalness only when physically appropriate;
- emissive contribution;
- texture scale/direction;
- edge/age variation;
- environment reflection.

A flat color on MeshStandardMaterial often reads as colored plastic because it lacks surface-scale variation and context.

## Shared procedural libraries

When architecture repeats boards, stone, metal, plaster, fabric, or ground:

- generate or load the source texture set once;
- reuse it with different tiling/color multipliers;
- preserve physically plausible scale;
- avoid unique high-resolution textures for every object.

## Light hierarchy

Design lights by role.

- Key: shapes the focal subject.
- Fill: controls shadow readability without flattening the image.
- Rim/back: separates silhouette from background.
- Practical: lantern, screen, sign, lamp, emissive fixture.
- Environment: sky/moon/room ambience.

Do not make every practical light cast shadows.

## Preserve darkness

Cinematic contrast requires unlit or underlit regions.

If every object is equally visible:

- reduce ambient intensity;
- tighten the key;
- let fog/background absorb distant contrast;
- use practical pools of light;
- reserve the brightest values for the focal region.

The goal is legibility, not uniform exposure.

## Color temperature

Warm/cool contrast is a powerful depth tool.

Examples:

- cool environment + warm practical subject;
- warm sunset field + cool metallic accent;
- neutral studio + one branded emissive color.

Avoid using five unrelated neon colors merely to signal “futuristic.”

## Fog and atmospheric perspective

Atmosphere separates depth bands.

Distant objects should generally lose:

- contrast;
- saturation;
- detail;
- sharpness.

Use scene fog, depth haze, particles, or plates consistently. The background should not be sharper and higher-contrast than the focal subject unless deliberately stylized.

## Particles

Particles should explain the world:

- dust;
- rain;
- snow;
- embers;
- pollen;
- mist droplets;
- sparks;
- drifting leaves.

Control density, velocity, scale, depth, and light response. Avoid generic floating dots in every scene.

## Weather

Weather should alter more than particles.

Rain can affect:

- surface roughness;
- puddles/reflections;
- fog;
- light contrast;
- drop direction;
- splashes.

Snow can affect:

- accumulated surface color;
- visibility;
- wind;
- particle density;
- scene palette.

A storm that only increases particle count feels like a UI toggle, not a world state.

## Bloom

Bloom should come from intentionally bright emissive/HDR regions.

Use it to support:

- lamps;
- screens;
- energy cores;
- reflected highlights;
- moon/sky accents.

If every bright edge blooms, the frame loses hierarchy.

## Vignette and grain

Use finish to unify layers, not to conceal defects.

Grain can help generated plates and WebGL sit in one image. Vignette can guide the eye. Both should remain subtle enough that users do not notice the effect before the content.

## Tone and exposure

Tune exposure after light placement, not before.

A common failure loop is:

scene too dark -> raise exposure -> shadows disappear -> add more lights -> scene flattens.

Instead, fix light ratios and material response first.

## Verification

Capture the same shot with:

- post-processing on/off;
- fog on/off;
- practical lights on/off.

If the frame only works because of bloom or grain, the underlying composition probably needs work.
