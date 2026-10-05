# Mode Selection

Use the fewest modes that fully cover the task.

| Signal | Primary mode | Add another mode when |
| --- | --- | --- |
| "build", "add", "implement", new capability | structure-feature | shared boundaries or final readiness need deeper review |
| bug report, failing test, regression, crash, wrong result | debug-root-cause | the correct fix requires structural cleanup or boundary changes |
| "refactor", "clean up", split giant file, modernize without behavior change | refactor-safely | public contracts or package dependencies are affected |
| cross-package change, circular dependency, service/domain ownership, API boundary | guard-architecture | implementation/refactor work is also requested |
| "is this ready", "review the patch", "verify", pre-merge | verify-change | a newly found defect must be fixed |
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
