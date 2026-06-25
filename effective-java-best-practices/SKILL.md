---
name: effective-java-best-practices
description: Applies Effective Java 3rd Edition best practices to Java code reviews and design decisions. Use when reviewing Java code for object creation patterns, class design, generics, enums, lambdas, streams, concurrency, or serialization. Use when advising on static factory methods, builder pattern, immutability, composition vs inheritance, or exception handling. Do not use for non-Java languages, general OOP theory without code context, or build tooling issues.
---

# Effective Java Best Practices

## Procedures

**Step 1: Identify the Domain**

Determine which chapter's concerns apply to the code or question at hand:

| Domain | Chapter | Key Items |
|--------|---------|-----------|
| Object Creation | 2 | 1–9 |
| Methods Common to All Objects | 3 | 10–14 |
| Classes and Interfaces | 4 | 15–25 |
| Generics | 5 | 26–33 |
| Enums and Annotations | 6 | 34–41 |
| Lambdas and Streams | 7 | 42–48 |
| Methods | 8 | 49–56 |
| General Programming | 9 | 57–68 |
| Exceptions | 10 | 69–77 |
| Concurrency | 11 | 78–84 |
| Serialization | 12 | 85–90 |

Read `references/items-by-chapter.md` for the full item list when deeper detail is needed.

**Step 2: Apply Object Creation Rules (Chapter 2)**

*Item 1 — Use static factory methods instead of constructors*

Prefer static factory methods over public constructors. They have names, can return cached instances, can return subtypes, and can return different types per call.

Follow these naming conventions:
- `from(T t)` — type-conversion, single parameter: `Date.from(instant)`
- `of(T... ts)` — aggregation, multiple parameters: `EnumSet.of(JACK, QUEEN, KING)`
- `valueOf(T t)` — verbose alternative to `from`/`of`: `BigInteger.valueOf(Integer.MAX_VALUE)`
- `getInstance(options)` — returns described instance, possibly cached: `StackWalker.getInstance(options)`
- `newInstance(classObject, len)` — guarantees a new instance each call: `Array.newInstance(classObject, arrayLen)`
- `getType(path)` — factory in a different class, returns the type: `Files.getFileStore(path)`
- `newType(path)` — factory in a different class, new instance: `Files.newBufferedReader(path)`
- `type(legacy)` — concise alternative to `getType`/`newType`: `Collections.list(legacyLitany)`

Signal the pattern in class/interface Javadoc when factory methods are the intended entry point.

*Item 2 — Use a Builder when many constructor parameters exist*

Apply the Builder pattern when a constructor or static factory would require four or more parameters, especially when many are optional. Separate required parameters (Builder constructor) from optional ones (setter-style methods that return `this`). End the chain with `build()`.

Use hierarchical builders (abstract `Pizza.Builder<T extends Builder<T>>`) for class hierarchies.

*Item 3 — Enforce the singleton property with a private constructor or an enum type*

Three approaches — static field, static factory, or single-element enum. Prefer the enum approach (`enum Elvis { INSTANCE; }`) unless the singleton must extend a superclass. Use static factory when flexibility (e.g., per-thread singleton) is needed later.

*Item 4 — Enforce noninstantiability with a private constructor*

Utility classes (pure static methods/fields) must declare `private UtilityClass() { throw new AssertionError(); }` to block instantiation and subclassing.

*Item 5 — Prefer dependency injection over hardwiring resources*

Pass dependencies (e.g., a `Lexicon`) into the constructor rather than using singletons or statics. Use `Supplier<T>` for factory parameters.

*Item 6 — Avoid creating unnecessary objects*

Cache expensive objects (compiled `Pattern`, boxed primitives). Prefer primitives; watch autoboxing loops. Never create a `String` with `new String("…")`.

*Item 7 — Eliminate obsolete object references*

Null out array slots, cache entries, and listener registrations when they are no longer needed in self-managed memory (stacks, caches, observer lists).

*Item 8 — Avoid finalizers and cleaners*

Use `Cleaner` or `AutoCloseable` + try-with-resources instead of `finalize()`. Finalizers are unpredictable and slow.

*Item 9 — Prefer try-with-resources over try-finally*

Any resource implementing `AutoCloseable` must be opened in a try-with-resources statement. This produces shorter, cleaner code and correctly handles exceptions from both the body and `close()`.

**Step 3: Apply Class and Interface Rules (Chapter 4)**

*Item 15 — Minimize accessibility*

Make every class, interface, and member as inaccessible as possible. Public classes must never have public mutable fields.

*Item 16 — Use accessor methods, not public fields*

Replace public instance fields with private fields plus public getters (and setters if mutable).

*Item 17 — Minimize mutability*

Five rules for immutable classes:
1. No state-mutating methods.
2. Class must not be extensible (`final class` or private constructor + static factory).
3. All fields `final`.
4. All fields `private`.
5. Exclusive access to mutable components (defensive copies).

Immutable objects are thread-safe; reuse them freely. Provide a companion mutable class (e.g., `StringBuilder`) for performance-sensitive accumulation.

*Item 18 — Favor composition over inheritance*

Never inherit across package boundaries unless the relationship is truly IS-A. Wrap the existing class in a forwarding class (`ForwardingSet`) and add features via the wrapper (`InstrumentedSet`).

*Item 19 — Design and document for inheritance, or prohibit it*

Override-safe classes must document self-use of overridable methods. Classes not designed for subclassing must be declared `final` or given private constructors.

*Item 20 — Prefer interfaces to abstract classes*

Interfaces allow multiple-type mixins, are ideal for skeletal implementations (abstract class named `AbstractXxx` implements the interface), and support non-hierarchical frameworks.

*Item 22 — Use interfaces only to define types*

Never use constant interfaces (`interface PhysicalConstants { double AVOGADROS_NUMBER = 6.022e23; }`). Export constants via a utility class or enum.

*Item 23 — Prefer class hierarchies to tagged classes*

Replace a class with a `kind` enum field and conditional behavior with a proper abstract class hierarchy.

**Step 4: Apply Generics Rules (Chapter 5)**

*Item 26 — Do not use raw types*

Always parameterize generic types. Raw types exist only for pre-generics compatibility — never use them in new code.

*Item 28 — Prefer lists to arrays*

Arrays are covariant and reifiable; generics are invariant and erased. Prefer `List<E>` to `E[]` inside generic classes.

*Item 29–30 — Favor generic types and methods*

Cast client code to `(E)` inside the generic class rather than forcing clients to cast. Use bounded type parameters (`<E extends Comparable<E>>`) and recursive type bounds when needed.

*Item 31 — Use bounded wildcards to increase API flexibility*

Producer parameters use `? extends T` (PECS: Producer Extends, Consumer Super). Consumer parameters use `? super T`. Do not use wildcards on return types.

**Step 5: Apply Enum and Annotation Rules (Chapter 6)**

*Item 34 — Use enums instead of int constants*

Enums are classes; they can have fields, methods, and abstract behavior per constant. Use a strategy enum (inner enum + abstract method) to share behavior across constants without switch statements.

*Item 36 — Use EnumSet instead of bit fields*

Replace `int` bitmask constants with `EnumSet<MyEnum>`. `EnumSet.of(...)` is as performant as a bit field.

*Item 37 — Use EnumMap instead of ordinal indexing*

Replace `array[e.ordinal()]` with `EnumMap<MyEnum, Value>` or `Collectors.groupingBy(…, () -> new EnumMap<>(…), …)`.

*Item 40 — Consistently use the @Override annotation*

Place `@Override` on every method intended to override a supertype method. The compiler catches signature mismatches.

**Step 6: Apply Lambda and Stream Rules (Chapter 7)**

*Item 42 — Prefer lambdas to anonymous classes*

Replace single-abstract-method anonymous class instances with lambda expressions. Keep lambdas to three lines or fewer; extract longer logic into a named method.

*Item 44 — Favor the use of standard functional interfaces*

Check `java.util.function` before writing a custom `@FunctionalInterface`. Key types: `Supplier<T>`, `Consumer<T>`, `Function<T,R>`, `Predicate<T>`, and their primitive specializations.

*Item 45 — Use streams judiciously*

Streams suit bulk data transformations (filter, map, reduce). Prefer loops when code needs to read or modify local variables, `return`/`break`/`continue`, or `checked` exceptions.

*Item 46 — Prefer side-effect-free functions in streams*

Use only pure functions in stream operations. Collect results with `Collectors.toList()`, `groupingBy`, `joining`, etc. — avoid `forEach` for computation.

**Step 7: Apply Exception Rules (Chapter 10)**

*Item 69 — Use exceptions only for exceptional conditions*

Never use exceptions for ordinary control flow (e.g., iterating until `ArrayIndexOutOfBoundsException`).

*Item 72 — Favor the use of standard exceptions*

Reuse `IllegalArgumentException`, `IllegalStateException`, `NullPointerException`, `IndexOutOfBoundsException`, `UnsupportedOperationException`, and `ConcurrentModificationException` before creating custom ones.

*Item 76 — Strive for failure atomicity*

A failed method call should leave the object in its original state. Validate parameters before mutation; operate on copies when needed.

**Step 8: Apply Concurrency Rules (Chapter 11)**

*Item 78 — Synchronize access to shared mutable data*

Use `synchronized` or `volatile` for any field accessed by multiple threads. `volatile` is sufficient for a single writer + multiple readers; use `AtomicLong`/`AtomicReference` for compound operations.

*Item 79 — Avoid excessive synchronization*

Never call an alien method (overridable or client-provided) from inside a synchronized block. Minimize the synchronized region.

*Item 80 — Prefer executors, tasks, and streams to threads*

Use `ExecutorService`, `ScheduledExecutorService`, and parallel streams instead of raw `Thread`. Use `ForkJoinPool` for divide-and-conquer.

*Item 81 — Prefer concurrency utilities to wait and notify*

Use `BlockingQueue`, `ConcurrentHashMap`, `CountDownLatch`, `Semaphore`, and `CyclicBarrier` instead of `Object.wait()`/`notify()`.

**Step 9: Validate and Report**

Run the read-only analysis script to detect common antipatterns in a Java source file:

```
python3 /home/devops/.claude/skills/effective-java-best-practices/scripts/analyze-java.py <path-to-java-file>
```

Report findings grouped by chapter with the item number, a one-line summary, and a concrete code suggestion.

## Error Handling

- If the code belongs to multiple domains, apply all relevant steps in order (creation → design → generics → …).
- If an item's rule conflicts with a framework constraint (e.g., JPA requires a no-arg constructor), note the exception and document it in the class Javadoc.
- If `scripts/analyze-java.py` fails, inspect `stderr` for the filename or permission issue and re-run with an absolute path.
