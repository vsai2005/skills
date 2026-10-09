# Example SDK v3 official project mirror

For SDK 3.x, text generation uses `client.responses.create(model=..., input=...)`.
The old `client.chat.completions.create(...)` call is a v2 compatibility API and must not be introduced in new v3 code.
