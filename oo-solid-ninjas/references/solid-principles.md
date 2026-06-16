# SOLID Principles Reference

## SRP — Single Responsibility Principle
**Definição:** A classe deve ter uma, e apenas uma, razão para mudar.

**Identificando violações:**
- Classes que crescem indefinidamente (nunca param de crescer)
- Classes com muitos métodos diferentes e não relacionados
- Classes modificadas com frequência por motivos distintos
- Controllers com regras de negócio misturadas com infraestrutura

**Solução:**
- Separar responsabilidades em classes menores
- Dois comportamentos "pertencem" à mesma responsabilidade se ambos mudam juntos
- Métodos privados melhoram legibilidade, mas responsabilidades distintas exigem classes distintas

**Exemplo de sintoma:** `CalculadoraDeSalario` com `if` para cada tipo de cargo → extrair interface `RegraDeCalculo` e criar uma classe por regra.

---

## DIP — Dependency Inversion Principle
**Definição:**
- Módulos de alto nível não devem depender de módulos de baixo nível. Ambos devem depender de abstrações.
- Abstrações não devem depender de detalhes. Detalhes devem depender de abstrações.

**Chave:** Sempre que uma classe for depender de outra, ela deve depender sempre de um módulo mais **estável** do que ela mesma. Abstrações tendem a ser estáveis; implementações são instáveis.

**Solução:**
- Programar voltado para interfaces
- Receber dependências via construtor (não instanciar dentro da classe)
- Criar interfaces que representem contratos estáveis

**Diferença DIP vs Injeção de Dependência:** DIP é o princípio (depender de abstrações); injeção de dependência é o mecanismo (passar dependências pelo construtor/framework).

---

## OCP — Open/Closed Principle
**Definição:** Classes devem ser **abertas para extensão**, mas **fechadas para modificação**.

**Chave:** O sistema deve evoluir por meio de novos códigos, não por alterações em códigos já existentes.

**Como alcançar:**
1. Identificar os pontos de variação (ex.: diferentes regras de preço, diferentes tipos de frete)
2. Criar abstrações (interfaces) para esses pontos
3. Receber as implementações pelo construtor
4. Adicionar novos comportamentos criando novas implementações, sem tocar na classe original

**Benefício colateral:** Classes abertas são altamente testáveis via mock objects.

---

## LSP — Liskov Substitution Principle
**Definição:** Subclasses devem ser substituíveis por suas superclasses sem alterar o comportamento correto do programa.

**Violações clássicas:**
- Subclasse lança exceção em método que a superclasse não lança
- Subclasse ignora comportamento que a superclasse garante
- Problema clássico: `Quadrado extends Retangulo` — ao alterar largura, o quadrado altera também a altura, quebrando o contrato

**Acoplamento pai-filho:** Herança cria forte acoplamento. Mudança na superclasse impacta todas as subclasses. Prefira composição quando a substituição não for natural.

**Quando usar herança:**
- DSLs, frameworks, quando o polimorfismo é genuíno e a substituição funciona
- Prefira `final` em classes e métodos que não devem ser sobrescritos

---

## ISP — Interface Segregation Principle
**Definição:** Clientes não devem ser forçados a depender de interfaces que não utilizam.

**Interfaces magras:** Quanto mais enxuta a interface, mais estável ela tende a ser (menos razões para mudar) e mais fácil de ser implementada.

**Repositórios DDD:** Criar interfaces específicas por necessidade do cliente (`RepositorioDeCliente`, `BuscadorDePedidos`) em vez de uma interface genérica com todos os métodos CRUD.

**Fábricas vs Injeção de Dependência:**
- Fábricas (Factory GoF) para construção manual de objetos complexos
- Frameworks de DI (Spring) para injeção automática em produção

---

## Relação entre os princípios
- **SRP + DIP → OCP:** Classes coesas que dependem de abstrações tornam-se naturalmente abertas para extensão
- **LSP:** Garante que a hierarquia de herança seja válida e substituível
- **ISP:** Mantém as abstrações pequenas e estáveis, reforçando o DIP
