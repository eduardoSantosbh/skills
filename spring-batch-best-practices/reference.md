# Spring Batch Component Reference

This reference is based on the patterns present in this repository, especially the examples in `ch07` through `ch13`.

## ItemReader Models

### ListItemReader

Use for tests, demos, fixtures, and small in-memory inputs. Do not use for large production datasets because the full input is already in memory.

Best practices:
- Keep it stateless in production-like tests.
- Prefer it for isolated step tests where persistence is not the behavior under test.
- Do not use it to simulate restart behavior unless the test explicitly controls state.

### FlatFileItemReader

Use for delimited or fixed-width files. This is the default choice for CSV and formatted text ingestion.

Best practices:
- Configure `.name(...)`, `.resource(...)`, tokenizer, field names, and mapper explicitly.
- Use `@StepScope` when the input file comes from `jobParameters`.
- Prefer `targetType(...)` for simple bean mapping and a `FieldSetMapper` for validation, type conversion, or custom parsing.
- Treat parse errors separately from business validation errors.
- In multithreaded steps, verify thread safety and restart tradeoffs before using `.saveState(false)`.

### MultiResourceItemReader

Use when one logical input spans many files.

Best practices:
- Configure a delegate reader with its own stable name and field mapping.
- Pass resources through job parameters or a deterministic resolver.
- Sort resources explicitly when ordering matters.
- Ensure restart metadata can identify both the current resource and position inside it.

### StaxEventItemReader

Use for XML documents split by fragment root element.

Best practices:
- Set the fragment root element name explicitly.
- Use a tested unmarshaller and validate representative XML samples.
- Avoid loading whole documents into memory.
- Treat malformed XML as a parse failure, not as business validation.

### JsonItemReader

Use for JSON arrays or streams where each element maps to an item.

Best practices:
- Use a stable object mapper configuration.
- Keep schema assumptions explicit in tests.
- Decide how unknown fields and invalid records should behave.

### JdbcCursorItemReader

Use for simple database reads where a cursor is acceptable.

Best practices:
- Configure fetch size, SQL, row mapper, and data source explicitly.
- Keep transactions and connection lifetime in mind; cursors can hold database resources open.
- Prefer paging when reads are very large, long-running, or sensitive to cursor timeouts.

### JdbcPagingItemReader

Use for large relational reads and restart-friendly pagination.

Best practices:
- Define stable sort keys that are unique or effectively unique.
- Avoid paging over a dataset that changes during the job unless the business accepts it.
- Tune page size with chunk size and database load.

### JpaPagingItemReader And HibernateCursorItemReader

Use when the domain model and ORM mappings are central to the job.

Best practices:
- Clear persistence context between pages or chunks when needed.
- Avoid lazy loading surprises inside processors and writers.
- Prefer DTO queries for large exports when full entities are unnecessary.

### RepositoryItemReader And Store-Specific Readers

Use repository, Mongo, Neo4j, GemFire, or similar readers when the backing store abstraction is already part of the application.

Best practices:
- Keep method arguments, sorting, and page size explicit.
- Confirm repository methods return stable ordering.
- Avoid hiding expensive queries behind generic repository names.

### Custom ItemStreamReader

Use for grouped records, lookahead logic, generated data, or protocols not covered by built-in readers.

Best practices:
- Persist minimal restart state in `ExecutionContext`.
- Use `getExecutionContextKey(...)` from `ItemStreamSupport` or otherwise namespace keys.
- Delegate `open`, `update`, and `close` when wrapping another stream reader.
- Make end-of-input return `null` and reserve exceptions for failures.

## ItemProcessor Models

### Simple ItemProcessor

Use for direct transformation, enrichment, or normalization.

Best practices:
- Keep processing deterministic for the same input.
- Avoid accumulating unbounded state across items.
- Keep external service calls isolated behind a service with timeouts and test doubles.

### Filtering Processor

Returning `null` means the item is filtered out.

Best practices:
- Use `null` only for expected business filtering.
- Do not return `null` for validation failures that should be audited, skipped, or fixed.
- Test counts and downstream effects, not just returned objects.

### ValidatingItemProcessor And BeanValidatingItemProcessor

Use for business or bean-validation rules.

Best practices:
- Decide between fail-fast validation and filtering invalid records.
- Keep validator messages actionable.
- Test both valid and invalid paths.

### CompositeItemProcessor

Use when each item must pass through a fixed pipeline of processors.

Best practices:
- Order processors from validation/normalization to enrichment to final transformation.
- Keep each delegate small and independently testable.
- Document whether a delegate may filter by returning `null`.
- Verify that the output type of each delegate matches the input type of the next delegate.
- For detailed implementation examples and a checklist, see [SKILL_CompositeItemProcessor_SpringBatch.md](SKILL_CompositeItemProcessor_SpringBatch.md).

### ClassifierCompositeItemProcessor

Use when different item classes or business categories require different processors.

Best practices:
- Keep classifier logic simple and covered by tests.
- Make a default route explicit when possible.
- Verify output type compatibility with the step writer.

### ScriptItemProcessor

Use for externally supplied transformation rules only when runtime flexibility is more important than compile-time safety.

Best practices:
- Treat scripts as deployable configuration with version control.
- Validate script inputs and outputs.
- Avoid scripts for core business logic that changes rarely.

### AsyncItemProcessor

Use when processing is expensive and thread-safe parallelism improves throughput.

Best practices:
- Pair with `AsyncItemWriter`.
- Ensure the delegate processor and dependencies are thread-safe.
- Measure throughput and failure behavior; async adds operational complexity.

## ItemWriter Models

### FlatFileItemWriter

Use for delimited, formatted, or custom text output.

Best practices:
- Configure `.name(...)`, `.resource(...)`, and line aggregation explicitly.
- Use headers and footers for control totals when downstream systems need them.
- Decide append versus overwrite behavior deliberately.
- Make restart behavior and partial file handling explicit.

### StaxEventItemWriter

Use for XML output.

Best practices:
- Configure root tag, marshaller, resource, and writer name.
- Validate XML output shape with sample files.
- Use callbacks for headers or footers only when they are part of the contract.

### JdbcBatchItemWriter

Use for relational writes.

Best practices:
- Prefer named parameters and `.beanMapped()` when item names match SQL parameters.
- Make writes idempotent with natural keys, upserts, or unique constraints.
- Tune chunk size with database batch limits.
- Keep SQL simple; complex routing belongs in processor/classifier logic.

### RepositoryItemWriter And Store-Specific Writers

Use when the application already writes through repositories or data-store templates.

Best practices:
- Verify batch behavior; some repository writes still perform per-item operations.
- Keep transaction semantics clear.
- Avoid repositories when direct batch APIs are required for performance.

### CompositeItemWriter

Use when every item must be written to multiple destinations.

Best practices:
- Ensure delegates share compatible transaction behavior.
- Consider failure order: if delegate 2 fails after delegate 1 wrote, restart behavior must be safe.
- Use only when duplicating every item is intentional.

### ClassifierCompositeItemWriter

Use when each item routes to one writer based on type or business condition.

Best practices:
- Keep classifier routes explicit and tested.
- Ensure every possible item has a destination or deliberate failure.
- Prefer this over conditionals inside a monolithic writer.

### MultiResourceItemWriter

Use when output must roll over across files.

Best practices:
- Configure item count limit, delegate writer, and suffix creator.
- Make generated filenames deterministic and collision-free.
- Test rollover and restart from the middle of a resource.

### SimpleMailMessageItemWriter

Use for notification-style output, not high-volume durable processing.

Best practices:
- Keep email sending outside critical data persistence when possible.
- Use retry limits and operational monitoring.
- Avoid sending duplicate messages on restart.

### AsyncItemWriter

Use with `AsyncItemProcessor`.

Best practices:
- Do not use it alone as a general writer accelerator.
- Verify exception propagation from futures.
- Test ordering assumptions if downstream systems depend on order.

## Job And Step Configuration

### Chunk-Oriented Steps

Best practices:
- Use chunk processing for most read-process-write workloads.
- Pick chunk size based on memory, transaction cost, remote call latency, and restart granularity.
- Keep the input and output types explicit with `.<I, O>chunk(size)`.
- Add skip/retry only for known recoverable exceptions.

### Job Parameters And Scope

Best practices:
- Pass runtime resources and filters through job parameters.
- Use `@StepScope` for beans that read job parameters.
- Keep identifying parameters stable so the job repository reflects business runs correctly.

### Job Identity And Restart

Best practices:
- Use stable job and step names.
- Add `RunIdIncrementer` only when repeated executions with the same business parameters should create new instances.
- Test restart for jobs that write files or insert rows.

### Listeners

Best practices:
- Use listeners for cross-cutting concerns: staging files, cleanup, auditing, metrics, and notifications.
- Keep business transformation in processors, not listeners.
- Make listener side effects idempotent.

### Scaling Models

Best practices:
- Use a multithreaded step only when reader, processor, and writer are thread-safe or deliberately stateless.
- Use parallel steps when flows are independent.
- Use partitioning when one dataset can be split by range, resource, or key.
- Use remote partitioning when workers need independent step execution.
- Use remote chunking when reading is centralized and processing/writing is distributed.

### Testing

Best practices:
- Test custom validators and processors as plain unit tests.
- Test readers with real sample resources and explicit `ExecutionContext`.
- Test writers against an embedded database or temporary file when possible.
- Use job launcher tests for complete flow, parameters, and restart behavior.

---

## Testing Patterns

### Unit Testing Components

Test `ItemProcessor`, `ItemValidator`, and `FieldSetMapper` implementations as plain unit tests with no Spring context:

```java
class CustomerItemValidatorTests {

    @Mock
    private NamedParameterJdbcTemplate template;
    private CustomerItemValidator validator;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        this.validator = new CustomerItemValidator(template);
    }

    @Test
    void shouldFailValidationForUnknownCustomer() {
        when(template.queryForObject(any(), any(Map.class), eq(Long.class))).thenReturn(0L);
        assertThrows(ValidationException.class, () -> validator.validate(new Customer()));
    }
}
```

### Integration Testing with Real Database

Use `@JdbcTest` to get an embedded database and `@Transactional(propagation = NOT_SUPPORTED)` to prevent the test transaction from wrapping batch transactions:

```java
@ExtendWith(SpringExtension.class)
@JdbcTest
@Transactional(propagation = Propagation.NOT_SUPPORTED)
class CustomerItemValidatorIntegrationTests {

    @Autowired
    private DataSource dataSource;
    private CustomerItemValidator validator;

    @BeforeEach
    void setUp() {
        this.validator = new CustomerItemValidator(new JdbcTemplate(dataSource));
    }
}
```

### Full Job Integration Test

Use `@SpringBatchTest` to get `JobLauncherTestUtils` auto-configured, and load only the classes the job needs via `@ContextConfiguration`:

```java
@ExtendWith(SpringExtension.class)
@JdbcTest
@ContextConfiguration(classes = {
    ImportJobConfiguration.class,
    CustomerItemValidator.class,
    BatchAutoConfiguration.class
})
@SpringBatchTest
@Transactional(propagation = Propagation.NOT_SUPPORTED)
class ImportCustomerUpdatesTests {

    @Autowired
    private JobLauncherTestUtils jobLauncherTestUtils;

    @Autowired
    private DataSource dataSource;

    @Test
    void shouldImportAllCustomers() throws Exception {
        JobExecution execution = jobLauncherTestUtils.launchJob(
            new JobParametersBuilder()
                .addString("customerFile", "classpath:customers.csv")
                .toJobParameters()
        );
        assertEquals(BatchStatus.COMPLETED, execution.getStatus());
    }
}
```

Best practices:
- Add `BatchAutoConfiguration.class` when using `@SpringBatchTest` outside `@SpringBootTest`.
- Use `launchStep(String stepName)` for isolated step testing when the full job is expensive.
- Keep SQL schema scripts under `src/test/resources/schema.sql` so `@JdbcTest` finds them automatically.
- Verify `JobExecution.getStatus()` and record counts, not just absence of exceptions.

---

## Cloud-Native Batch Patterns

### Downloading Files Before Processing

Use a `JobExecutionListener` to download remote files and store paths in `JobExecutionContext` before any step runs:

```java
public class DownloadingJobExecutionListener implements JobExecutionListener {

    @Override
    public void beforeJob(JobExecution jobExecution) {
        // Download from S3/GCS, store result path
        String localPath = downloadFile(jobExecution.getJobParameters());
        jobExecution.getExecutionContext().put("localFiles", localPath);
    }

    @Override
    public void afterJob(JobExecution jobExecution) {
        // Clean up temp files or upload results
    }
}
```

Register on the job:

```java
@Bean
public Job job(JobExecutionListener listener) throws Exception {
    return jobBuilderFactory.get("s3jdbc")
        .listener(listener)
        .start(loadStep())
        .build();
}
```

### Reading Dynamic Paths from ExecutionContext

Use `@StepScope` + SpEL to retrieve paths stored by the listener:

```java
@Bean
@StepScope
public MultiResourceItemReader<?> reader(
    @Value("#{jobExecutionContext['localFiles']}") String paths) {

    MultiResourceItemReader<Foo> reader = new MultiResourceItemReader<>();
    reader.setName("multiReader");
    reader.setDelegate(delegateReader());
    reader.setResources(parsePaths(paths));
    return reader;
}
```

Best practices:
- Always use `jobExecutionContext` (not `jobParameters`) to pass data produced at runtime between steps.
- Keep the listener focused on infrastructure: download, cleanup, path resolution. Keep business logic in processors.
- In Kubernetes/cloud deployments, configure a persistent `JobRepository` database (not in-memory H2) so restarts survive pod restarts.

---

## Remote Partitioning Pattern

Use Spring Integration messaging to distribute step execution to worker processes. The master partitions the dataset; workers execute steps independently.

### Master Configuration

```java
@Configuration
@Profile("master")
@EnableBatchIntegration
public class MasterConfiguration {

    private final RemotePartitioningMasterStepBuilderFactory masterStepBuilderFactory;

    @Bean
    public DirectChannel requests() {
        return new DirectChannel();
    }

    @Bean
    public IntegrationFlow outboundFlow(AmqpTemplate amqpTemplate) {
        return IntegrationFlows.from(requests())
            .handle(Amqp.outboundAdapter(amqpTemplate).routingKey("requests"))
            .get();
    }

    @Bean
    public Step masterStep(Partitioner partitioner) {
        return masterStepBuilderFactory.get("masterStep")
            .partitioner("workerStep", partitioner)
            .outputChannel(requests())
            .gridSize(10)
            .build();
    }
}
```

### Worker Configuration

```java
@Configuration
@Profile("!master")
@EnableBatchIntegration
public class WorkerConfiguration {

    private final RemotePartitioningWorkerStepBuilderFactory workerStepBuilderFactory;

    @Bean
    public DirectChannel requests() {
        return new DirectChannel();
    }

    @Bean
    public IntegrationFlow inboundFlow(ConnectionFactory connectionFactory) {
        return IntegrationFlows
            .from(Amqp.inboundAdapter(connectionFactory, "requests"))
            .channel(requests())
            .get();
    }

    @Bean
    public Step workerStep() {
        return workerStepBuilderFactory.get("workerStep")
            .inputChannel(requests())
            .<Input, Output>chunk(100)
            .reader(partitionedReader(null))
            .processor(processor())
            .writer(writer(null))
            .build();
    }
}
```

Best practices:
- Use `@Profile("master")` and `@Profile("!master")` to activate master/worker configuration from the same JAR.
- Annotate both configurations with `@EnableBatchIntegration` to get `RemotePartitioning*StepBuilderFactory` beans.
- Always use a persistent message broker (RabbitMQ, Kafka) and a shared `JobRepository` database so the master and workers share state.
- Test partitioning logic separately from the remote integration wiring.

---

## BatchConfigurer Customization

Override `DefaultBatchConfigurer` when you need custom `JobRepository`, `JobLauncher`, or `PlatformTransactionManager` configuration:

```java
@Component
public class CustomBatchConfigurer extends DefaultBatchConfigurer {

    @Override
    protected JobRepository createJobRepository() throws Exception {
        JobRepositoryFactoryBean factory = new JobRepositoryFactoryBean();
        factory.setDataSource(dataSource());
        factory.setTransactionManager(transactionManager());
        factory.setIsolationLevelForCreate("ISOLATION_SERIALIZABLE");
        factory.setTablePrefix("BATCH_");
        factory.afterPropertiesSet();
        return factory.getObject();
    }
}
```

Best practices:
- Override only what you need; `DefaultBatchConfigurer` provides sensible defaults.
- Use `ISOLATION_SERIALIZABLE` for the job repository only when concurrent job launches conflict.
- In Spring Boot 3+, prefer `@EnableBatchProcessing(dataSourceRef = ..., transactionManagerRef = ...)` over `BatchConfigurer` which was removed.
