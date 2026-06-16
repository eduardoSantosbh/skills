# Coesão, Acoplamento e Encapsulamento

## Coesão (Capítulo 2)

**Definição:** Uma classe coesa é aquela que possui uma única responsabilidade — ela não para de crescer por um único motivo.

### Sinais de classe não coesa
- Cresce indefinidamente por múltiplos motivos
- Tem muitos `if/else` baseados em tipo/cargo/categoria
- Difícil de reutilizar isoladamente
- Muitas dependências para fazer uma única operação

### Como alcançar coesão
1. Identificar por que a classe cresce (quais são os eixos de mudança)
2. Criar abstrações para agrupar comportamentos similares (ex.: interface `RegraDeCalculo`)
3. Separar responsabilidades em classes menores
4. Usar padrões de projeto: Decorator, Chain of Responsibility, State, Strategy

### Controllers gordos
Controllers devem apenas coordenar processos (converter do mundo HTTP para o domínio). Regras de negócio pertencem a classes de domínio. Infraestrutura pertence a DAOs, serviços externos, etc.

### Métodos privados vs extração de classe
- Métodos privados: melhoram legibilidade do método público (implementação complexa de UMA responsabilidade)
- Nova classe: quando o trecho representa uma responsabilidade genuinamente separada e reutilizável

---

## Acoplamento (Capítulo 3)

**Definição:** Nível de dependência entre classes. Alto acoplamento = frágil, difícil de reutilizar.

### Tipos de acoplamento
- **Estrutural:** visível nos `imports` — classe A usa classe B diretamente
- **Lógico:** implícito por convenções arquiteturais (ex.: nome do método Rails = nome do arquivo HTML) — perigoso porque não aparece no código

### Estabilidade de classes
- **Estável:** mudada raramente; muitas classes dependem dela; ex.: `List`, `String`
- **Instável:** muda com frequência; poucas dependências externas
- **Regra:** dependa sempre de módulos mais estáveis que você mesmo

### Estratégias para reduzir acoplamento
1. Extrair interfaces para criar contratos estáveis (as implementações ficam instáveis, as interfaces ficam estáveis)
2. Agrupar dependências que trabalham juntas em uma única classe intermediária (reduz o "fan-out")
3. Usar padrões: Observer, Visitor, Factory

### Balança coesão vs acoplamento
Mais coesão = mais classes = mais acoplamento. O objetivo não é eliminar um, mas encontrar o equilíbrio certo: **classes muito coesas que dependem de abstrações estáveis**.

---

## Encapsulamento (Capítulo 5)

**Definição:** A classe esconde **como** faz o trabalho. Expõe apenas **o quê** ela faz.

### Dois ganhos do encapsulamento
1. **Facilidade de alterar implementação:** troca-se a implementação sem impactar o resto do sistema
2. **Redução de pontos de mudança:** regra de negócio em um único lugar; mudança propagada automaticamente

### Lei de Demeter
Evitar invocações em cadeia: `a.getB().getC().getD().metodo()`. Cada "." adicional é uma dependência indireta.

**Regra:** Um método deve interagir apenas com:
- Seus próprios atributos
- Seus parâmetros
- Objetos que ele mesmo criou

**Exceção aceita:** Cadeia de getters puramente para recuperar dados para exibição (camada de view) é menos problemática.

### Getters de coleções
Nunca retorne coleções mutáveis diretamente:
```java
// Ruim:
public List<Pagamento> getPagamentos() { return pagamentos; }
// Bom:
public List<Pagamento> getPagamentos() {
    return Collections.unmodifiableList(pagamentos);
}
```

### Modelo anêmico — antipadrão
Classes com apenas atributos + getters/setters (sem comportamento) são código procedural disfarçado de OO. A lógica fica espalhada em classes "BLL", "Service", "Delegate" que manipulam os dados de fora.

**Solução:** Coloque o comportamento perto dos dados. `Fatura` deve saber quando está paga; `ContaCorrente` deve saber como depositar e sacar.

### Teste como verificador de encapsulamento
Se o teste é difícil de escrever, provavelmente o design tem problemas. Um teste bem escrito instancia uma classe, invoca um método, verifica a saída — simples. Se não for simples, é sinal de:
- Alto acoplamento (muitas dependências para instanciar)
- Baixa coesão (muitos comportamentos num só lugar)
- Encapsulamento ruim (estado exposto demais)

---

## Herança x Composição (Capítulo 6)

### Quando herança funciona
- O relacionamento é genuinamente "é um" (não "tem um comportamento de")
- A substituição LSP é válida: a subclasse pode ser usada no lugar da superclasse sem surpresas
- DSLs e frameworks onde o contrato é claro e estável

### Quando preferir composição
- Para reutilizar comportamento sem criar hierarquia frágil
- Quando a herança criaria acoplamento forte entre pai e filho
- Quando o LSP seria violado

### Pacotes como unidade de organização
Agrupe classes que mudam juntas e são usadas juntas no mesmo pacote. Evite pacotes por "camada técnica" (`controllers/`, `services/`, `daos/`) — prefira pacotes por "funcionalidade" (`notafiscal/`, `pagamento/`, `cliente/`).
