# Matching Engine

Matching engine (*order matching system*) de **ativo único**, **em memória**,
escrita em **Python puro** — sem dependências externas.

```
matching_engine/
    orders.py    modelo de dados (o que é uma ordem)
    book.py      livro de ofertas (onde as ordens ficam)
    engine.py    cruzamento, cancelamento, alteração e pegged
    cli.py       interpretador de comandos e REPL
tests/           84 testes (unittest)
```

## Como rodar

```bash
python -m matching_engine                    # modo interativo
python -m unittest discover -s tests -v      # testes
```

## Comandos

| Comando | Exemplo |
|---|---|
| `limit <buy\|sell> <price> <qty>` | `limit buy 10 100` |
| `market <buy\|sell> <qty>` | `market sell 200` |
| `peg <bid\|offer> <buy\|sell> <qty>` | `peg bid buy 150` |
| `cancel order <id>` | `cancel order ord-1` |
| `modify order <id> [price <p>] [qty <q>]` | `modify order ord-1 price 9.98 qty 50` |
| `print book` | mostra o livro |
| `exit` | encerra |

---

## Arquitetura

Três camadas, com dependência apenas para baixo:

**`orders.py`** define o dado. Não conhece o livro nem a engine.

**`book.py`** guarda as ordens e responde onde elas estão. Não decide nada: não
sabe cruzar, não sabe o que é um negócio. Cada lado é um dicionário
`preço → fila de ordens`, e a fila preserva a ordem de chegada.

**`engine.py`** aplica as regras. É a única camada que decide se duas ordens
cruzam, a que preço, e o que acontece com a sobra.

**`cli.py`** traduz texto em chamadas e formata a saída. A engine não imprime
nada — por isso os testes verificam o resultado sem capturar `stdout`, e uma API
HTTP poderia reusar a engine sem tocar neste arquivo.

Cada ordem carrega duas informações distintas, e a diferença entre elas é o que
sustenta os requisitos 4 e 5:

| Campo | O que é | Muda? |
|---|---|---|
| `order_id` | identidade (`ord-1`) | nunca |
| `sequence` | posição na fila | sim, quando a ordem perde prioridade |

---

## Decisões técnicas

### 1. Limit agressiva é executada

O enunciado permite ignorar ou preencher. A engine **preenche**, por dois
motivos.

Ignorar deixaria o livro **cruzado** — melhor compra ≥ melhor venda, duas ordens
paradas uma na frente da outra sem negociar. Nenhuma bolsa permite esse estado, e
a próxima ordem a mercado executaria a um preço pior do que o disponível.

Além disso, executar elimina um caso especial: uma ordem a mercado passa a ser
apenas *uma limit sem limite de preço*, e as duas percorrem o mesmo caminho.

Se sobrar quantidade, a sobra entra no livro **no preço limite da ordem** — o
preço que o cliente pediu, não o preço a que ele executou.

Um livro cruzado também abriria espaço para arbitragem instantânea: participantes de alta frequência poderiam comprar a um preço inferior ao mesmo tempo em que vendem a um preço superior, obtendo lucro sem risco até que a inconsistência fosse corrigida. Em um mercado real, mecanismos de matching devem impedir esse estado para preservar a eficiência e a justiça da formação de preços.

Além disso, um livro permanentemente cruzado comprometeria a confiança no sistema, pois indicaria falhas de transparência, inconsistências na priorização das ordens ou problemas na infraestrutura responsável pelo processamento dos negócios.

### 2. O negócio sai pelo preço da ordem passiva

A engine utiliza o modelo de execução pelo preço da ordem passiva (*maker price*).
Assim, uma `limit sell 20 100` seguida de uma `limit buy 25 100` gera um negócio a
20, não a 25.

A ordem agressora define apenas o limite que aceita pagar ou receber, enquanto a
ordem que já estava no livro representa a liquidez disponível. Essa escolha é
compatível com a prioridade preço-tempo utilizada em muitos mercados de livro
contínuo.

### 3. A saída de negócios é agregada por faixa de preço

A matching engine mantém cada execução individualmente, pois cada negócio representa
um evento separado entre ordens distintas.

Entretanto, para simplificar a visualização no terminal e seguir o formato do
enunciado, a CLI agrupa execuções consecutivas que ocorreram no mesmo preço.

Assim, duas execuções internas:

```
Trade, price: 20, qty: 100
Trade, price: 20, qty: 50
```

são exibidas como:

```
Trade, price: 20, qty: 150
```

Internamente cada execução continua sendo um `Trade` separado — é o registro correto de quem
negociou com quem; `aggregate_trades` junta os consecutivos de mesmo preço apenas
na hora de imprimir.

### 4. Prioridade na alteração de ordem

| Alteração | Prioridade | Motivo |
|---|---|---|
| mudar o preço | **perde** | é outra oferta: pede lugar numa fila onde nunca esteve |
| aumentar a quantidade | **perde** | o excedente não esperou na fila |
| diminuir a quantidade | **mantém** | devolve lugar; ninguém atrás é prejudicado |

O princípio único: **prioridade se conquista esperando**. Qualquer alteração que
peça *mais* ao mercado reinicia a espera; alteração que peça *menos*, não.

Só a primeira linha é exigida pelo enunciado; as outras duas seguem a convenção
dos mercados reais. Na prática, "perder prioridade" é
apenas atribuir um `sequence` novo à ordem, e a fila se reorganiza sozinha.

Se o novo preço cruzar o livro, a ordem alterada executa, coerente com a
decisão 1.

### 5. Pegged reprecificada conserva a prioridade

O enunciado demonstra sem escrever. No exemplo do
requisito 5, a ordem pegged de 150 chega **depois** das demais, mas quando o bid
sobe para 10.1 ela aparece **na frente** da limit de 300 que criou aquele nível:

```
150 @ 10.1     <- pegged
300 @ 10.1     <- limit que criou o nível
```

Então a reprecificação **não** manda a ordem para o fim da fila. O contraste com
a decisão 4 é o que explica: lá quem mudou o preço foi o cliente, e ele paga por
isso; aqui quem mudou foi a engine, sem ninguém pedir — não seria justo punir.

Implementação: a pegged mantém o `sequence` original, e `OrderBook.add` a insere
na posição correspondente da fila em vez de acrescentá-la ao fim.

Pelo mesmo motivo, o preço de uma pegged **não pode ser alterado à mão**: ele
pertence à engine. Alterar a quantidade é permitido.

A ordem nunca saiu do livro. Ela estava lá, negociável, a cada instante. Mudou de faixa, mas não de posição na sala.

### 6. O preço de referência ignora as próprias pegged

`best_limit_price` considera apenas ordens LIMIT. Sem isso, uma pegged poderia
seguir outra e o sistema entraria em laço — A segue B, B segue A. As pegged
perseguem o mercado formado por _"ordens de verdade"_.

### 7. Pegged sem referência

Uma pegged só existe se houver um preço para seguir:

- **na criação**, sem bid (ou offer) formado por ordens limit, a ordem é recusada
  com `reference price unavailable`;
- **depois de criada**, se a referência desaparecer, a ordem é retirada do livro
  e fica suspensa, voltando sozinha assim que uma nova referência surgir.

Ao voltar, recebe `sequence` novo: ela esteve fora do livro, e o tempo em que não
esteve disponível para negociar não conta como espera na fila.

### 8. Pegged agressiva executa até a referência se estabilizar

Duas das quatro combinações nascem cruzando o livro: `peg offer buy` compra ao
melhor preço de venda, e `peg bid sell` vende ao melhor preço de compra.

Nesses casos a ordem varre um nível, a referência muda, e ela precisa ser
**reavaliada no novo preço** antes de entrar no livro. Sem esse laço, a ordem seria
inserida num preço que cruza o lado oposto e o livro ficaria cruzado — o estado
que a decisão 1 existe para evitar.

O laço termina porque cada volta ou consome liquidez (reduzindo o lado oposto) ou
encontra a referência inalterada (preço que perseguia é alterado).

### 9. Ordens market nunca ficam no livro

Sobra de ordem a mercado é descartada, sem mensagem adicional — o enunciado
mostra `market buy 200` executando 150 e nada mais na saída.

### 10. `Decimal` para preço, `int` para quantidade + validação de preço e quantidade

Em ponto flutuante, `0.1 + 0.2 != 0.3`. Num livro de ofertas isso vira ordem que
deveria cruzar e não cruza. `Decimal` compara exatamente o que foi digitado.
Preços são normalizados na impressão (`20`, não `20.00`).

Quantidade é validada em todos os pontos de entrada: precisa ser inteiro
positivo. Preço precisa ser maior que zero.

### 11. `Order created:` é sempre impresso

A confirmação é sempre impressa,
porque sem ela não há como saber o identificador usado em `cancel` e `modify`.
Só ordens que **ficaram** no livro geram essa linha — uma ordem totalmente
executada não tem o que confirmar.

---

## Complexidade

`N` = ordens no livro, `L` = faixas de preço distintas, `k` = ordens numa faixa,
`M` = ordens consumidas por uma execução, `P` = pegged vivas.

| Operação | Custo | Como |
|---|---|---|
| localizar a faixa de preço | O(1) | dicionário `preço → fila` |
| inserir ordem nova | O(1) | vai para o fim da fila (`deque.append`) |
| inserir pegged reprecificada | O(k) | busca a posição pelo `sequence` |
| melhor preço (bid/offer) | O(L) | `max`/`min` sobre as chaves |
| localizar ordem por id | O(1) | dicionário `id → ordem` |
| cancelar | O(k) | remoção da fila da faixa |
| executar | O(M · L) | uma consulta ao melhor preço por ordem consumida |
| reprecificar pegged | O(P · N) | cada pegged recalcula sua referência |
| `print book` | O(L log L + N) | ordena as faixas e percorre as ordens |

### Escolha das estruturas

**Dicionário `preço → fila`**: acesso direto à faixa, sem busca. Separar os dois
lados evita comparar compra com venda o tempo todo.

**`deque` dentro da faixa**: `append` e `popleft` em O(1) garantem a ordem de
chegada, que é a segunda regra de prioridade. Uma lista comum teria `pop(0)`
em O(N).

**Dicionário `id → ordem`**: sem ele, cancelar exigiria varrer o livro inteiro
atrás do identificador.

**Caminho rápido na inserção**: uma ordem nova sempre tem o maior `sequence`, e
portanto sempre vai para o fim da fila. `OrderBook.add` verifica isso primeiro e
só percorre a fila quando uma pegged reprecificada precisa voltar para o meio.
Sem esse desvio, inserir 8.000 ordens na mesma faixa levava 2,67s; com ele, 0,03s.

---

## Testes

Comando para execução:

```bash
python -m unittest discover -s tests -v
```

84 testes cobrindo os quatro exemplos do enunciado reproduzidos literalmente,
cruzamento em um e vários níveis, execução total e parcial, prioridade por
chegada, cancelamento, alteração com e sem perda de prioridade, as quatro
combinações de pegged, suspensão e retorno por falta de referência, e entradas
inválidas.

---

## Limitações conhecidas

**O melhor preço é uma varredura.** `max()`/`min()` custa O(L) e é chamado a cada
volta do laço de matching, então a execução custa O(M · L) — dobrar o livro
quadruplica o tempo de varrê-lo. Um heap
binário com remoção preguiçosa deixaria a consulta em O(1) e a execução em
O(M · log L). Não foi implementado porque não é necessário na escala deste
exercício.

**Cancelamento é O(k), não O(1).** Achar a ordem pelo id é imediato, mas removê-la
da fila exige percorrer a faixa. Uma lista duplamente ligada com ponteiros na
própria ordem daria O(1), ao custo de uma estrutura bem mais complexa.

**Pegged suspensas não aparecem no livro.** Continuam existindo e podem ser
canceladas pelo id, mas `print book` mostra apenas o que está efetivamente
disponível para negociação — que é o que o enunciado exemplifica.
