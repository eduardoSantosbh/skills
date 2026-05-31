# Skill: CompositeItemProcessor no Spring Batch

## Objetivo

Use esta skill quando precisar explicar, implementar ou revisar o uso de `CompositeItemProcessor` no **Spring Batch**.

O `CompositeItemProcessor` é usado para encadear vários `ItemProcessor`s em uma única cadeia de processamento. Cada processor recebe o resultado do processor anterior, formando um fluxo sequencial de transformação dos dados.

---

## Quando usar

Use `CompositeItemProcessor` quando o processamento de um item tiver várias etapas independentes, por exemplo:

```text
ler CSV
 → validar campos
 → normalizar dados
 → aplicar regra de negócio
 → converter para entidade
 → gravar no banco
```

Ele é útil para evitar um único `ItemProcessor` muito grande, cheio de responsabilidades misturadas.

---

## Conceito principal

No Spring Batch, um `ItemProcessor<I, O>` recebe um objeto de entrada do tipo `I` e retorna um objeto de saída do tipo `O`.

Exemplo conceitual:

```text
ItemReader<Input>
        ↓
CompositeItemProcessor<Input, Output>
        ↓
ItemWriter<Output>
```

Dentro do `CompositeItemProcessor`:

```text
Processor 1: Input → Input
Processor 2: Input → DTO
Processor 3: DTO → Entity
```

O tipo final retornado pelo último processor será o tipo recebido pelo `ItemWriter`.

---

## Exemplo prático

### Cenário

Imagine um batch que lê transações de um CSV e precisa:

1. Validar a transação;
2. Normalizar os dados;
3. Converter para entidade;
4. Gravar no banco.

---

## Estrutura sugerida

```text
domain
 └── Transaction.java

application
 └── processor
     ├── ValidateTransactionProcessor.java
     ├── NormalizeTransactionProcessor.java
     └── ConvertTransactionProcessor.java

infrastructure
 └── batch
     └── TransactionBatchConfig.java
```

---

## Processor de validação

```java
package com.example.application.processor;

import com.example.application.dto.TransactionInput;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.stereotype.Component;

@Component
public class ValidateTransactionProcessor
        implements ItemProcessor<TransactionInput, TransactionInput> {

    @Override
    public TransactionInput process(TransactionInput item) {
        if (item.valorVenda() == null || item.valorVenda().signum() <= 0) {
            return null;
        }

        if (item.numeroCliente() == null || item.numeroCliente().isBlank()) {
            return null;
        }

        return item;
    }
}
```

Quando um `ItemProcessor` retorna `null`, o item é filtrado e não segue para o `ItemWriter`.

---

## Processor de normalização

```java
package com.example.application.processor;

import com.example.application.dto.TransactionInput;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.stereotype.Component;

@Component
public class NormalizeTransactionProcessor
        implements ItemProcessor<TransactionInput, TransactionInput> {

    @Override
    public TransactionInput process(TransactionInput item) {
        return new TransactionInput(
                item.bandeira().trim().toUpperCase(),
                item.numeroCartao(),
                item.produto(),
                item.plataforma().trim().toUpperCase(),
                item.valorVenda(),
                item.numeroCliente().trim(),
                item.dataProcessamento()
        );
    }
}
```

---

## Processor de conversão

```java
package com.example.application.processor;

import com.example.application.dto.TransactionInput;
import com.example.domain.Transaction;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.stereotype.Component;

@Component
public class ConvertTransactionProcessor
        implements ItemProcessor<TransactionInput, Transaction> {

    @Override
    public Transaction process(TransactionInput item) {
        return new Transaction(
                item.bandeira(),
                item.numeroCartao(),
                item.produto(),
                item.plataforma(),
                item.valorVenda(),
                item.numeroCliente(),
                item.dataProcessamento()
        );
    }
}
```

---

## Configuração do CompositeItemProcessor

```java
package com.example.infrastructure.batch;

import com.example.application.dto.TransactionInput;
import com.example.application.processor.ConvertTransactionProcessor;
import com.example.application.processor.NormalizeTransactionProcessor;
import com.example.application.processor.ValidateTransactionProcessor;
import com.example.domain.Transaction;
import org.springframework.batch.item.support.CompositeItemProcessor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class TransactionProcessorConfig {

    @Bean
    public CompositeItemProcessor<TransactionInput, Transaction> transactionCompositeProcessor(
            ValidateTransactionProcessor validateProcessor,
            NormalizeTransactionProcessor normalizeProcessor,
            ConvertTransactionProcessor convertProcessor
    ) {
        CompositeItemProcessor<TransactionInput, Transaction> processor =
                new CompositeItemProcessor<>();

        processor.setDelegates(List.of(
                validateProcessor,
                normalizeProcessor,
                convertProcessor
        ));

        return processor;
    }
}
```

---

## Configuração no Step

```java
@Bean
public Step transactionStep(
        JobRepository jobRepository,
        PlatformTransactionManager transactionManager,
        ItemReader<TransactionInput> reader,
        CompositeItemProcessor<TransactionInput, Transaction> processor,
        ItemWriter<Transaction> writer
) {
    return new StepBuilder("transactionStep", jobRepository)
            .<TransactionInput, Transaction>chunk(100, transactionManager)
            .reader(reader)
            .processor(processor)
            .writer(writer)
            .build();
}
```

---

## Regra importante sobre tipos

Este fluxo está correto:

```text
ValidateTransactionProcessor:
TransactionInput → TransactionInput

NormalizeTransactionProcessor:
TransactionInput → TransactionInput

ConvertTransactionProcessor:
TransactionInput → Transaction
```

Resultado final:

```text
CompositeItemProcessor<TransactionInput, Transaction>
```

Este fluxo estaria errado:

```text
Processor 1: TransactionInput → Transaction
Processor 2: TransactionInput → Transaction
```

Porque o segundo processor espera `TransactionInput`, mas receberia `Transaction`.

---

## Boas práticas

- Separe cada responsabilidade em um processor pequeno.
- Evite colocar validação, normalização, enriquecimento e conversão dentro de uma única classe.
- Use nomes claros para os processors.
- Use `return null` apenas quando quiser filtrar o item.
- Use exceção quando o item representar uma falha real de processamento e você quiser trabalhar com skip, retry ou listener.
- Garanta que todos os processors da cadeia tenham tipos compatíveis.
- Crie testes unitários para cada processor separadamente.

Exemplos de nomes:

```text
ValidateTransactionProcessor
NormalizeTransactionProcessor
EnrichTransactionProcessor
ConvertTransactionProcessor
```

---

## Exemplo aplicado a transações financeiras

Para um microsserviço de transações financeiras, um fluxo profissional poderia ser:

```text
CSV ou fila
   ↓
ValidateTransactionProcessor
   ↓
NormalizeTransactionProcessor
   ↓
EnrichTransactionProcessor
   ↓
ConvertToTransactionEntityProcessor
   ↓
ItemWriter
   ↓
Banco SQL
```

Exemplo de etapas:

```text
Validar valorVenda
Validar numeroCliente
Normalizar bandeira
Normalizar plataforma
Converter dataProcessamento
Criar entidade Transaction
Persistir no banco
```

---

## Template de resposta para entrevista

`CompositeItemProcessor` é um recurso do Spring Batch usado para encadear vários `ItemProcessor`s em sequência. Ele ajuda a separar responsabilidades dentro do processamento batch. Por exemplo, em vez de criar um único processor para validar, normalizar, enriquecer e converter dados, posso criar processors separados e combiná-los em um `CompositeItemProcessor`. Assim, o código fica mais limpo, testável e aderente ao princípio da responsabilidade única.

---

## Checklist rápido

Antes de usar `CompositeItemProcessor`, valide:

```text
[ ] O processamento tem mais de uma responsabilidade?
[ ] Cada processor tem uma função clara?
[ ] A saída de cada processor é compatível com a entrada do próximo?
[ ] O último processor retorna o mesmo tipo esperado pelo ItemWriter?
[ ] Itens inválidos devem ser filtrados com null ou gerar exceção?
[ ] Cada processor possui teste unitário separado?
```

---

## Resumo

Use `CompositeItemProcessor` quando quiser montar uma pipeline de processamento dentro de um Step do Spring Batch.

Ele melhora:

```text
organização
testabilidade
manutenção
separação de responsabilidades
clareza do fluxo batch
```

Em vez de fazer isso:

```text
Um processor gigante com tudo dentro
```

Prefira isso:

```text
Validação → Normalização → Enriquecimento → Conversão
```

Esse é um uso profissional em projetos batch com Spring.
