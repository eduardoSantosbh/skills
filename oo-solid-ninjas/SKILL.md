---
name: oo-solid-ninjas
description: Guides the design of cohesive, loosely coupled, and encapsulated object-oriented classes using SOLID principles as taught in 'Orientação a Objetos e SOLID para Ninjas' by Maurício Aniche. Use when reviewing or designing Java classes for flexibility, identifying design smells, applying SRP, DIP, OCP, LSP, or ISP, improving encapsulation, or evaluating cohesion and coupling. Do not use for procedural code design, database schema design, frontend/UI architecture, or general code formatting tasks.
---

# OO e SOLID para Ninjas — Projetando Classes Flexíveis

Baseado no livro de Maurício Aniche (Casa do Código/Alura, 2023). O objetivo é sempre criar **classes coesas, pouco acopladas e bem encapsuladas** — o triângulo fundamental da OO de qualidade.

> Pense no sistema como um quebra-cabeças: o **formato** das peças (interfaces, contratos) importa mais do que o **desenho** interno (implementação). Se o formato for estável, você troca o desenho quando quiser.

---

## Step 1: Diagnosticar o problema de design

Ao analisar uma classe ou conjunto de classes, identifique o sintoma principal:

| Sintoma | Princípio violado | Referência |
|---|---|---|
| Classe que nunca para de crescer | SRP | `references/cohesion-coupling-encapsulation.md` |
| Mudança exige alteração em N arquivos | Encapsulamento / SRP | `references/cohesion-coupling-encapsulation.md` |
| Classe muito acoplada a implementações concretas | DIP | `references/solid-principles.md` |
| Adicionar novo comportamento exige `if` | OCP | `references/solid-principles.md` |
| Subclasse quebra contrato da superclasse | LSP | `references/solid-principles.md` |
| Interface grande, implementações forçadas a fingir | ISP | `references/solid-principles.md` |
| Invocações em cadeia (`a.getB().getC()`) | Lei de Demeter | `references/cohesion-coupling-encapsulation.md` |
| Classe com só getters/setters, sem comportamento | Modelo Anêmico | `references/cohesion-coupling-encapsulation.md` |
| God class, Feature Envy, Shotgun Surgery | Design Smells | `references/design-smells-and-metrics.md` |

Se o sintoma não estiver claro, leia `references/design-smells-and-metrics.md` para identificar o mau cheiro.

---

## Step 2: Aplicar a técnica correta

### 2A — Coesão / SRP

1. Identificar **por quantos motivos a classe pode mudar**. Se mais de um, ela não é coesa.
2. Separar responsabilidades em classes menores, cada uma com uma única razão para mudar.
3. Se os comportamentos são similares (mesmo "esqueleto"), criar uma **interface** que representa a abstração e uma **implementação por variante**.
4. Se as responsabilidades são distintas (sem padrão comum), simplesmente separar em classes sem interface.
5. Verificar se controllers estão com regras de negócio. Controllers devem apenas coordenar — mover regras para classes de domínio ou serviço.

### 2B — Acoplamento / DIP

1. Listar todas as dependências concretas da classe (`new ConcreteClass()` dentro dela).
2. Para cada dependência que muda com frequência ou tem múltiplas implementações, **criar uma interface**.
3. Remover as instanciações concretas de dentro da classe.
4. **Receber as dependências pelo construtor** (não por setters — o compilador garante a presença).
5. Verificar se a interface criada é coesa (poucas responsabilidades, contrato simples e estável).

Leia `references/solid-principles.md` — seção DIP para detalhes sobre estabilidade de módulos.

### 2C — Extensibilidade / OCP

1. Identificar os **pontos de variação** — onde os `if`s se acumulam para tratar variantes do comportamento.
2. Criar uma **interface** para cada ponto de variação (ex.: `TabelaDePreco`, `ServicoDeEntrega`).
3. Criar uma **implementação concreta** por variante.
4. Fazer a classe principal receber as implementações pelo construtor.
5. Verificar: agora é possível adicionar uma nova variante sem tocar na classe principal?

### 2D — Encapsulamento

1. Para cada método público, responder: **"O quê ele faz?"** (deve ser respondível pelo nome). **"Como ele faz?"** (não deve ser respondível de fora).
2. Se uma regra de negócio está fora da classe que detém os dados, mover para dentro (eliminar "Intimidade Inapropriada").
3. Aplicar **Tell, Don't Ask**: em vez de perguntar estado para decidir externamente, dar uma ordem ao objeto.
4. Remover `setters` desnecessários. Preferir métodos com semântica de negócio.
5. Getters de coleções: retornar `Collections.unmodifiableList()`.
6. Construtor rico: passar obrigatórios no construtor; nunca permitir objeto em estado inválido.

### 2E — Herança / LSP

1. Verificar se a subclasse pode ser usada no lugar da superclasse sem surpresas (teste mental de substituição).
2. Se a subclasse sobrescreve métodos com `throw new UnsupportedOperationException()` → Refused Bequest → trocar por composição.
3. Se a herança é apenas para reutilizar código (não para polimorfismo) → trocar por composição.
4. Leia `references/solid-principles.md` — seção LSP para o problema do Quadrado/Retângulo.

### 2F — Interfaces magras / ISP

1. Verificar se alguma implementação da interface é forçada a implementar métodos que não usa.
2. Dividir interfaces grandes em interfaces menores e específicas por cliente.
3. Repositórios: criar interfaces específicas (`BuscadorDePedidosPorCliente`) em vez de interfaces CRUD genéricas.

---

## Step 3: Verificar a qualidade da solução

Após refatorar, validar com as perguntas abaixo:

**Coesão:**
- [ ] A classe muda por um único motivo?
- [ ] Ela para de crescer quando não há mudança naquele motivo?

**Acoplamento:**
- [ ] A classe depende de interfaces/abstrações, não de implementações concretas?
- [ ] Adicionar uma nova implementação não requer alterar esta classe?

**Encapsulamento:**
- [ ] Consigo dizer o que cada método público faz pelo nome, mas não como?
- [ ] Não há regras de negócio espalhadas fora da classe dona dos dados?
- [ ] A Lei de Demeter está sendo respeitada?

**Testabilidade:**
- [ ] É possível instanciar a classe e invocar seus métodos em um teste sem infraestrutura real?
- [ ] As dependências podem ser substituídas por mocks facilmente?

> **Regra de ouro:** "Se está difícil de testar, é porque o código pode ser melhorado."

---

## Step 4: Métricas (quando solicitado)

Se o usuário pede para avaliar a qualidade geral de um módulo ou codebase, ler `references/design-smells-and-metrics.md` e reportar:

1. **Complexidade ciclomática** de métodos críticos (número de `if + for + while + 1`)
2. **LCOM** — métodos da classe usam os mesmos atributos? (coesão)
3. **Acoplamento eferente** (Ce) — quantas classes esta classe depende?
4. **Acoplamento aferente** (Ca) — quantas classes dependem dela?
5. Presença de **design smells** identificados na seção de maus cheiros

---

## Notas importantes

- **Flexibilidade tem custo.** Um simples `if` pode ser a solução certa. Flexibilize apenas onde há necessidade real de extensão. "Seja parcimonioso. Flexibilize código que realmente precisa disso."
- **Escrita incremental.** Código de qualidade é incremental: modelo, observo, aprendo, melhoro.
- **Padrões de projeto** são soluções recorrentes para problemas de coesão e acoplamento. Observer, Visitor, Strategy, Decorator, Factory são aliados diretos dos princípios SOLID.
- **Arquitetura hexagonal (ports and adapters):** domínio separado de infraestrutura. Se a classe tem regras de negócio, não deve conhecer infraestrutura. Se conhece infraestrutura, não deve ter regras de negócio.

---

## Error Handling

- **Sintoma ambíguo:** Se não for claro qual princípio está sendo violado, ler `references/design-smells-and-metrics.md` primeiro para identificar o mau cheiro, depois mapear para o princípio correspondente na tabela do Step 1.
- **Conflito entre princípios:** Coesão e acoplamento são forças opostas. Se aumentar a coesão (mais classes) gera acoplamento excessivo, avaliar se uma interface intermediária resolve o equilíbrio. Lembrar: balança coesão vs acoplamento é fundamental.
- **Herança legada difícil de remover:** Se a hierarquia de herança já está estabelecida e é custosa de refatorar, ao menos garantir que novas adições usem composição. Não aplicar LSP retroativamente em código sem cobertura de testes.
- **Escopo de refatoração grande demais:** Priorizar o ponto de maior dor (classe que mais muda, ou com maior acoplamento eferente). Refatoração OO é incremental; não é necessário acertar tudo de uma vez.
