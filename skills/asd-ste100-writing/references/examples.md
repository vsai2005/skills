# Examples

## Wordy instruction

Before:

```text
Due to the fact that the service is currently unavailable, it is recommended that the operator should utilize the Restart Service button in order to attempt a restart.
```

After:

```text
If the service is unavailable, select Restart Service.
```

## Ambiguous reference

Before:

```text
Update the cache after the database returns the record because it can be stale.
```

After:

```text
After the database returns the record, update the cache. The cached record can be stale.
```

Use a more precise noun if the intended stale object is different.

## Noun-heavy wording

Before:

```text
Perform a verification of the configuration before execution of the migration.
```

After:

```text
Verify the configuration before you run the migration.
```

## Preserve identifiers

Before:

```text
If `AuthPolicyV2` rejects the request with `E4017`, do not rename or paraphrase those identifiers.
```

After:

```text
If `AuthPolicyV2` returns `E4017`, do not continue.
```

The code identifier and error code remain exact.
