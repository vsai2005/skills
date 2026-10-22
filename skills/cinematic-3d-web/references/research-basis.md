# Research Basis and Reference Boundaries

This skill synthesizes general cinematic-web, Three.js, compositing, rendering, UI/UX, and agent-workflow practices.

## Reference patterns studied

A useful public case study is MengTo/kage, a cinematic Three.js page that combines:

- live procedural WebGL architecture and atmosphere;
- scroll-directed camera movement;
- generated WebP scene plates;
- transparent foreground artwork;
- DOM editorial typography;
- restrained post-processing;
- mobile and reduced-motion behavior;
- adaptive rendering/performance work.

The important lesson is architectural: the final image is composed from several technologies instead of forcing every visual detail into real-time 3D.

Kage's repository currently states that no license is granted for reuse or redistribution of its original code or artwork. Treat it as a design/architecture reference only unless the license changes.

MengTo/Skills is a separate MIT-licensed repository containing reusable web-design skills, including Three.js, scroll storytelling, weather, particles, and related techniques. If code or substantial text is directly copied or adapted from MIT-licensed material, preserve the required copyright and license notice.

## General principles retained

- design shots before detailed geometry;
- use the smallest renderer that satisfies the goal;
- separate semantic UI from decorative WebGL;
- prefer native reversible scroll;
- combine 3D with plates/cutouts when it improves quality and efficiency;
- cap/adapt pixel ratio;
- treat lighting, fog, and material response as primary quality systems;
- use rendered screenshots as verification evidence;
- provide reduced-motion and WebGL-failure behavior;
- preserve asset provenance and rights.

## What this skill intentionally does not do

It does not:

- reproduce Kage's temple design;
- copy Kage code or artwork;
- mandate one color palette;
- mandate Three.js for every premium interface;
- equate Awwwards-style motion with good UX;
- require heavy post-processing;
- claim that generated concept art is a faithful 3D reconstruction;
- substitute aesthetic scoring for runtime evidence.

The goal is transferable production reasoning and original implementation.
