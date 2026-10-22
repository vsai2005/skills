# AI Asset Generation for Cinematic Web Scenes

Use this reference when creating scene plates, transparent foregrounds, texture source material, concept frames, or static fallbacks.

## Generate for a role

Every asset prompt should state the compositing role.

Examples:

- distant background plate;
- foreground branch silhouette;
- architectural extension;
- foggy skyline;
- editoral scene still;
- transparent machinery cutout;
- texture source;
- reduced-motion poster.

Do not generate “a cool cinematic image” without knowing where it sits in the final stack.

## Keep a stable style preamble

For a coherent set, define a reusable preamble containing:

- world;
- mood;
- palette;
- material character;
- light direction/temperature;
- lens/composition;
- realism/stylization level;
- exclusions.

Reuse that preamble across related assets, then add role-specific instructions.

## Plate prompt pattern

Describe:

- camera/lens character;
- horizon and perspective;
- focal or intentionally empty region;
- light direction;
- fog/atmosphere;
- palette;
- edge behavior for compositing;
- no text/logos/captions;
- exact aspect ratio.

Keep important subjects away from areas reserved for DOM copy.

## Foreground alpha prompt pattern

Describe:

- single isolated foreground element or cluster;
- transparent background;
- camera side/orientation;
- light direction matching the live scene;
- crisp natural edge detail;
- no cast background;
- no text;
- no frame;
- composition leaving intended openings.

After generation, inspect the alpha edge at 100% and against both light and dark backgrounds.

## Concept frames

Concept images are targets, not implementation truth.

Extract from them:

- camera;
- silhouette;
- palette;
- light;
- depth;
- materials;
- foreground framing;
- atmosphere.

Do not blindly rebuild every hallucinated architectural detail.

## Texture generation

For tileable material sources, request:

- orthographic/flat capture;
- even illumination;
- no perspective;
- no dramatic shadow;
- seamless/tileable when supported;
- correct material type and scale.

Derive normal/roughness carefully or use authored material sources when quality matters.

## Asset QA

Before shipping:

- remove accidental text/logos;
- inspect seams;
- verify transparency;
- check color-space handling;
- compress appropriately;
- confirm dimensions are justified by screen occupancy;
- remove duplicates;
- record source/model/prompt/rights.

## Rights and originality

Reference images can guide composition and technique. Do not copy unlicensed artwork, code, proprietary logos, or distinctive protected assets into the final work.

When a reference repository grants an open-source license, preserve required attribution/notice for copied or substantially adapted material.

When rights are unclear, derive high-level principles and create original implementation/assets.

## Provenance manifest

For every generated production asset, record:

- filename;
- purpose;
- model/provider;
- date;
- prompt or prompt identifier;
- input references;
- edits;
- rights note;
- output dimensions;
- final compression format.

This makes later replacement, auditing, and style consistency much easier.
