# State and Responsive Matrix

Use this when UI behavior varies by async state, permissions, content volume, or viewport.

Create only the rows that matter to the feature.

| Surface | State | Narrow | Wide | Keyboard | Expected recovery |
| --- | --- | --- | --- | --- | --- |
| Example form | default | check | check | check | n/a |
| Example form | validation error | check | check | check | edit + resubmit |
| Example result | loading | check | check | n/a | wait/cancel if supported |
| Example result | empty | check | check | check | next useful action |
| Example result | server error | check | check | check | retry/back |

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
