# Version Grounding

Before relying on external API behavior, identify:

```text
dependency/tool
local declared version
resolved version if available
runtime/service version if different
source consulted
behavior that differs by version
```

When the exact version is unknown, state the uncertainty and avoid irreversible implementation choices that depend on it.

For migrations, prefer expansion-compatible steps when old and new versions can overlap.
