# State and Responsive Matrix

Use this when UI behavior varies by async state, permissions, content volume, or viewport.

Create only the rows that matter to the feature.

| Surface | State | Narrow | Wide | Keyboard | Content stress | Expected recovery |
| --- | --- | --- | --- | --- | --- | --- |
| Example form | default | check | check | check | long label | n/a |
| Example form | validation error | check | check | check | long error | edit + resubmit |
| Example result | loading | check | check | n/a | n/a | wait/cancel if supported |
| Example result | empty | check | check | check | zero items | next useful action |
| Example result | server error | check | check | check | multi-line status | retry/back |

## State selection

Common candidates:

- first load;
- refresh;
- empty;
- minimum content;
- typical content;
- maximum/long content;
- success;
- validation error;
- dependency/server error;
- permission denied;
- disabled/read-only;
- slow/offline;
- destructive confirmation.

Do not force every state into every feature.

## Viewport selection

Use project-supported sizes first. At minimum for responsive web work, include one representative narrow viewport and one normal desktop/wide viewport. Add a middle size when the layout materially changes there.

Do not treat a single screenshot at one width as proof of responsive quality.

For web interfaces where standards-related reflow matters, 320 CSS px and 200% zoom are useful checks. A narrower width can be added as a stress test, but label it as a project/engineering stress case rather than a universal requirement.

## Content stress

Test realistic content variation when layout depends on content:

- long names/labels;
- localization expansion when relevant;
- many rows/items;
- zero rows/items;
- large numbers;
- validation text;
- multi-line status text.

Use representative stress cases, not deliberately absurd strings that the product contract forbids.

When relevant, also exercise:
- localization expansion;
- RTL direction;
- supported light/dark themes;
- high-contrast/forced-color mode;
- software-keyboard overlap on mobile forms/dialogs.
