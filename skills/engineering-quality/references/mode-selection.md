# Mode Selection

Use the fewest modes that fully cover the task.

| Signal | Primary mode | Add another mode when |
| --- | --- | --- |
| "build", "add", "implement", new capability | structure-feature | shared boundaries or final readiness need deeper review |
| bug report, failing test, regression, crash, wrong result | debug-root-cause | the correct fix requires structural cleanup or boundary changes |
| "refactor", "clean up", split giant file, modernize without behavior change | refactor-safely | public contracts or package dependencies are affected |
| cross-package change, circular dependency, service/domain ownership, API boundary | guard-architecture | implementation/refactor work is also requested |
| cheap vs heavy checks, deferred suites, shared-code test trigger | tiered-testing | final readiness needs completion evidence |
| already-red suite, pre-existing failure question | baseline-compare | the candidate also contains a new defect to fix |
| intermittent/flaky/rerun-pass failure | flaky-test-triage | a confirmed root cause then needs code repair |
| "is this ready", "review the patch", "verify", pre-merge | verify-change | a newly found defect must be fixed |
| unfamiliar/large repo, unclear owner, stale/noisy context | context-engineering | implementation still needs a specialist afterwards |
| changing framework/SDK/cloud/database behavior | source-grounded-development | source facts must be translated into local implementation |
| high-risk or explicit second review | independent-review | reviewer findings then feed verify-change |
| auth/authz/secrets/untrusted command/file/network/value boundary | security-hardening | architecture or verification may also be required |
| technical docs, procedures, release notes, review comments, or explanations needing controlled clear English | asd-ste100-writing | exact identifiers/contract text must still be preserved |
| prose that is correct but stiff, repetitive, generic, or machine-like | humanizer-writing | technical procedures may first need asd-ste100-writing; preserve facts and real author voice |
| feature + regressions + refactor + final hardening | engineering-quality | coordinate only the needed subworkflows |

## Avoid false multi-mode work

A feature that needs one small helper extraction is still primarily a feature task. A bug fix that renames a variable is still a bug task. Do not route to the coordinator merely because a change has normal implementation details.

## Escalate architecture attention

Treat a change as architecture-sensitive when it affects one or more of:

- package/module dependency direction;
- shared domain rules used by several features;
- public API or event schemas;
- persistence models or migrations;
- auth/authz boundaries;
- plugin/provider interfaces;
- task queues, concurrency, transactions, or distributed coordination;
- code-generation boundaries;
- deployment/runtime topology.
