# Regression Testing

A regression test should preserve the discovered contract, not merely the exact bug report text.

## Good pattern

For a classifier bug:

- original failing input;
- another input in the same semantic class;
- nearby input that must remain accepted;
- ambiguity boundary if one exists.

For a state bug:

- transition sequence that failed;
- invariant after each important transition;
- retry/duplicate behavior if relevant.

For a persistence bug:

- representative existing data shape;
- new data shape;
- read/write compatibility if required.

## Test location

Prefer the lowest layer that owns the incorrect behavior, then add a higher-level regression only when integration behavior itself contributed to the failure.

## Do not overfit

A test named after one customer/example can be useful, but its assertions should describe the general contract whenever possible.
