---
name: spring-batch-best-practices
description: Apply Spring Batch best practices for ItemReader, ItemProcessor, ItemWriter, Step, and Job configuration. Use when designing, reviewing, implementing, or refactoring Spring Batch jobs, especially projects with FlatFileItemReader, JDBC readers/writers, XML/JSON readers, multi-resource processing, validators, CompositeItemProcessor, composite processors, classifier writers, async processing, partitioning, remote chunking, @SpringBatchTest, JobLauncherTestUtils, @StepScope, @JobScope, ExecutionContext, JobParameters, cloud-native batch, remote partitioning, or BatchConfigurer.
---

# Spring Batch Best Practices

## Quick Start

Use this skill for any Spring Batch code. Prefer the project's existing style, then apply these checks:

1. Identify the batch model: file, database, XML/JSON, repository, multi-resource, composite, classifier, async, partitioned, remote, or cloud-native.
2. Confirm restartability: reader/writer names, `ExecutionContext` keys, `saveState`, idempotent writes, and job parameters.
3. Keep components scoped correctly: `@StepScope` for step-parameterized beans, `@JobScope` for job-level beans, singleton for stateless processors.
4. Make chunk size, transaction boundaries, skip/retry rules, and listener behavior explicit.
5. Validate with focused tests for readers, processors, writers, and complete jobs.

## Reader Rules

- Use builder APIs and always provide stable `.name(...)` values for restart metadata.
- Use `@StepScope` when a reader depends on `jobParameters` or `stepExecutionContext`, especially `Resource`, date ranges, IDs, or SQL fragments.
- For custom stateful readers, implement `ItemStreamReader` or extend `ItemStreamSupport`; persist only minimal restart state in `ExecutionContext`.
- For database reads, prefer paging for large or mutable result sets; cursor readers are simpler but hold a database cursor open.
- In multithreaded steps, only use thread-safe readers or disable state intentionally with `.saveState(false)`.

## Processor Rules

- Keep processors deterministic and side-effect light. Enrichment is acceptable, but external calls should be bounded or delegated to a service.
- Returning `null` filters an item; throwing an exception fails/skips/retries based on step policy. Never mix these meanings accidentally.
- Use `ValidatingItemProcessor` or `BeanValidatingItemProcessor` for validation; decide whether invalid records fail the job or are filtered.
- Use `CompositeItemProcessor` for sequential transformations; use `ClassifierCompositeItemProcessor` when routing by item type or business rule.
- For async processing, pair `AsyncItemProcessor` with `AsyncItemWriter` and verify delegate thread safety.

## Writer Rules

- Prefer batch-oriented writers (`JdbcBatchItemWriter`, `FlatFileItemWriter`, `StaxEventItemWriter`) over per-item writes.
- Make writes idempotent when restart or retry is possible.
- Use `CompositeItemWriter` when every item must go to every destination; use `ClassifierCompositeItemWriter` when each item routes to one destination.
- For file writers, configure stable names, resources, line aggregation, headers/footers, and deletion/append behavior explicitly.
- For multi-resource writers, define predictable suffix creation and verify rollover behavior.

## Job and Step Rules

- Name jobs and steps with stable business names; changing names changes job repository metadata identity.
- Use job parameters for all runtime inputs. Add `RunIdIncrementer` only when repeated non-identifying runs are intended.
- Choose chunk size from transaction cost, memory use, database batch size, and restart granularity.
- Add skip/retry/fault-tolerant configuration only for known recoverable failures.
- Use listeners for cross-cutting behavior: file download/upload, auditing, metrics, and cleanup.
- For scaling, prefer the simplest model that meets throughput: multithreaded step → parallel flows → partitioning → remote partitioning → remote chunking.

## Testing Rules

- Annotate integration tests with `@SpringBatchTest` + `@ExtendWith(SpringExtension.class)` to get `JobLauncherTestUtils` and `JobRepositoryTestUtils` auto-wired.
- Use `@ContextConfiguration` to load only the job configuration and collaborators under test; avoid loading the full application context.
- Add `BatchAutoConfiguration.class` to `@ContextConfiguration` when using `@SpringBatchTest` outside a full `@SpringBootTest`.
- Use `@JdbcTest` with `@Transactional(propagation = Propagation.NOT_SUPPORTED)` for database-backed step tests to prevent test-managed transactions from interfering with batch transactions.
- Test validators and processors as plain unit tests (no Spring context) with mocks before writing integration tests.
- Test readers with `ExecutionContext` directly using `open(ctx)` / `read()` / `close()` calls against real sample resources.
- Test writers against an embedded database or a temporary file.
- Use `JobLauncherTestUtils.launchJob(JobParameters)` for full job flow and `launchStep(String)` for isolated step testing.

## Cloud-Native Rules

- Use a `JobExecutionListener` (`beforeJob`) to download remote resources (S3, GCS) before the step runs and store paths in `JobExecutionContext`.
- Retrieve stored paths with `@StepScope` + `@Value("#{jobExecutionContext['localFiles']}")` in readers.
- Use `MultiResourceItemReader` with `@StepScope` when the input file list is only known at runtime.
- Keep cloud credentials and bucket names in job parameters or externalized configuration, not hardcoded.
- In containerized deployments, configure `JobRepository` against a shared external database so multiple instances share job metadata.

## Review Checklist

- [ ] Reader and writer names are stable and unique.
- [ ] `@StepScope` used for parameterized components; `@JobScope` for job-level beans.
- [ ] Restart behavior is intentional and tested.
- [ ] Processor filtering versus failure semantics are explicit.
- [ ] Writers are idempotent or target constraints prevent duplicates.
- [ ] Chunk size and transaction scope are justified.
- [ ] Skip/retry limits match business tolerance.
- [ ] Job parameters cover all runtime inputs.
- [ ] `@SpringBatchTest` used on integration tests; plain unit tests for isolated components.
- [ ] Tests exist for readers, processors, writers, and job launch paths.

## Additional Reference

For detailed guidance by component model, testing patterns, cloud-native patterns, and remote scaling examples, see [reference.md](reference.md).

For deep guidance on `CompositeItemProcessor` pipelines including type compatibility and a checklist, see [SKILL_CompositeItemProcessor_SpringBatch.md](SKILL_CompositeItemProcessor_SpringBatch.md).
