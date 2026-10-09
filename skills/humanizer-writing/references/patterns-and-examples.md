# Patterns and Examples

## Generic opening

Before:

```text
In today's fast-paced software landscape, it is more important than ever to ensure that systems operate efficiently and reliably.
```

After:

```text
The gateway needs to stay reliable under peak traffic.
```

Use the second version only when that statement is actually supported by the source context.

## Empty praise

Before:

```text
The new release provides a robust and seamless improvement that significantly enhances the overall user experience.
```

After:

```text
The release reduces median ingest latency by 17% in EU-West-1.
```

The rewrite is better because it uses an existing measured fact, not because it sounds more casual.

## Repetitive transitions

Before:

```text
Furthermore, the retry budget is unchanged. Additionally, there are no schema changes. Moreover, the request cap remains the same.
```

After:

```text
The retry budget is unchanged, there are no schema changes, and the request cap remains the same.
```

## Over-summary

Before:

```text
In conclusion, the rollout will take place on October 14. Overall, this demonstrates that the update is ready for deployment.
```

After:

```text
The rollout is scheduled for October 14.
```

Do not add `ready for deployment` unless the source provides evidence for that conclusion.

## Technical text after controlled-English editing

Controlled version:

```text
If error E104 remains, do not change the database configuration. Contact the support team.
```

Good humanization:

```text
If E104 remains, leave the database configuration unchanged and contact the support team.
```

Keep the controlled version when separate actions or safety emphasis matter. Naturalness must not weaken the instruction.
