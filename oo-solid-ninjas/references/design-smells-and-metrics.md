# Design Smells e Métricas de Código

## Maus Cheiros de Design (Capítulo 9)

### Refused Bequest
Subclasse herda métodos da superclasse mas os ignora ou os sobrescreve com `throw new UnsupportedOperationException()`. Sinal de que herança foi escolhida errada; provavelmente composição é melhor.

### Feature Envy
Classe que "inveja" os dados de outra classe — um método que usa muito mais métodos/atributos de outra classe do que da sua própria. Sintoma: lógica que deveria estar dentro da classe dona dos dados.
```java
// Ruim: controller manipulando Contrato diretamente
contrato.setData("23/01/2015");
contrato.fecha();
List<Pagamento> pagamentos = contrato.geraPagamentos();
// Bom: comportamento dentro de Contrato
```

### Intimidade Inapropriada
Classe que sabe mais do que deveria sobre o funcionamento interno de outra. Exemplo: classe externa com `if (nf.getValorSemImposto() > 10000)` que deveria estar encapsulado em `NotaFiscal.calculaImposto()`.

### God Class
Classe que faz tudo. Viola SRP de forma extrema. Possui dezenas de métodos, cresce indefinidamente, é responsável por múltiplos conceitos do sistema.

### Divergent Changes
Uma classe que muda por muitos motivos diferentes. Sinal de falta de coesão (SRP violado).

### Shotgun Surgery
Uma mudança conceitual que exige alteração em muitos arquivos/classes diferentes. Sinal de falta de encapsulamento — o comportamento está espalhado.

### Outros smells comuns
- Longa lista de parâmetros → agrupar em objetos
- Código duplicado → abstrair comportamento comum
- Classe de dados pura (anêmica) → adicionar comportamento relevante

---

## Métricas de Código (Capítulo 10)

### Complexidade Ciclomática
Conta o número de caminhos possíveis em um método. Fórmula: `número de ifs + número de fors + número de whiles + 1`. Valores altos indicam métodos difíceis de testar e manter.

**Referência:** Métodos com CC > 10 merecem atenção. CC > 20 é sinal de refatoração urgente.

### Tamanho de Métodos
Métodos longos são difíceis de entender e testar. Prefira métodos curtos com nomes semânticos. Extraia métodos privados para melhorar legibilidade; extraia para novas classes quando houver responsabilidade distinta.

### Coesão — LCOM (Lack of Cohesion of Methods)
Mede se os métodos de uma classe usam os mesmos atributos. LCOM alto = classe não coesa = provável candidata a SRP.

### Acoplamento Aferente e Eferente
- **Eferente (Ce):** quantas classes esta classe depende → alto = frágil
- **Aferente (Ca):** quantas classes dependem desta classe → alto = instável para mudar (impacto grande)
- **Instabilidade:** `I = Ce / (Ca + Ce)` → próximo de 0 = estável, próximo de 1 = instável

**Princípio:** Classes instáveis devem depender de classes estáveis (DIP).

### Má Nomenclatura
Nomes ruins dificultam a compreensão. Bons nomes revelam intenção. Variáveis como `x`, `aux`, `temp` são sintomas de código mal expressivo.

### Ferramentas sugeridas
- **Checkstyle:** estilo e convenções Java
- **PMD:** análise estática, detecta smells
- **FindBugs / SpotBugs:** detecta bugs potenciais
- **JDepend:** análise de dependências entre pacotes
- **Metrics (Eclipse plugin):** calcula LCOM, CC, Ce, Ca

---

## Consistência e Objetos Bem Formados (Capítulo 8)

### Construtores ricos
Passe todas as informações obrigatórias no construtor. O compilador garante que o objeto nunca existirá em estado inválido.

### Validação de dados
Valide na fronteira do sistema (entrada do usuário, APIs externas). Objetos de domínio devem sempre estar válidos.

### Tell, Don't Ask
Diga ao objeto o que fazer, não pergunte sobre seu estado para tomar decisões externas:
```java
// Ruim (ask):
if (nf.getValorSemImposto() > 10000) { valor = 0.06 * nf.getValor(); }
// Bom (tell):
double valor = nf.calculaValorImposto();
```

### Tiny Types
Encapsular primitivos em tipos específicos (`Cpf`, `Email`, `Dinheiro`) para adicionar validação e semântica.

### Getters e Setters
- **Setters:** evitar ao máximo; expõem estado interno e quebram encapsulamento. Prefira métodos com semântica de negócio (`deposita()`, `saca()`).
- **Getters:** menos danosos, mas cuidado com getters que retornam coleções mutáveis. Use `Collections.unmodifiableList()`.

### Imutabilidade
Prefira objetos imutáveis quando possível. Imutabilidade elimina bugs de estado compartilhado e simplifica o raciocínio sobre o código.
