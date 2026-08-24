# Roadmap — Matching Engine

Este roadmap organiza o desenvolvimento da Matching Engine em 10 etapas, começando pela estrutura básica já implementada e avançando até a entrega final.

## 1. Estrutura inicial do projeto

- [x] Criar repositório Git/GitHub.
- [x] Configurar branch `main` e repositório remoto.
- [x] Criar ambiente virtual `.venv`.
- [x] Configurar `.gitignore`.
- [x] Criar estrutura de pacotes e testes.
- [x] Criar README inicial.

---

## 2. Modelo de ordens e livro básico

- [x] Criar `orders.py`.
- [x] Implementar `Side` com `BUY` e `SELL`.
- [x] Implementar `OrderType` com `LIMIT` e `MARKET`.
- [x] Criar classe `Order` com `side`, `type`, `qty` e `price`.
- [x] Utilizar `Decimal` para preços.
- [x] Criar `book.py`.
- [x] Separar ordens BUY e SELL.
- [x] Agrupar ordens por preço.
- [x] Utilizar FIFO dentro do mesmo preço.
- [x] Implementar Best Bid e Best Offer.
- [x] Criar e executar `test_book.py`.

---

## 3. Matching Engine básica

- [ ] Criar `engine.py`.
- [ ] Criar classe `MatchingEngine`.
- [ ] Integrar a engine ao `OrderBook`.
- [ ] Implementar Market Buy.
- [ ] Implementar Market Sell.
- [ ] Implementar execução total e parcial.
- [ ] Permitir execução contra várias ordens e vários níveis de preço.
- [ ] Garantir que Market Orders não permaneçam no livro.
- [ ] Gerar trades no formato:

```text
Trade, price: <price>, qty: <qty>
```

---

## 4. Matching de Limit Orders e testes da engine

- [ ] Inserir Limit Orders que não cruzam o livro.
- [ ] Implementar Limit Buy agressiva.
- [ ] Implementar Limit Sell agressiva.
- [ ] Respeitar o preço limite da ordem.
- [ ] Manter no livro a quantidade restante após execução parcial.
- [ ] Criar `test_engine.py`.
- [ ] Testar Market Buy e Market Sell.
- [ ] Testar execuções totais e parciais.
- [ ] Testar múltiplas ordens e múltiplos preços.
- [ ] Reproduzir o exemplo original do desafio.

Decisão técnica:

```text
Limit Orders que cruzarem o livro serão executadas.
Caso reste quantidade, a sobra permanecerá no livro no preço limite.
```

---

## 5. Interface de linha de comando

- [ ] Criar `cli.py`.
- [ ] Interpretar comandos `limit` e `market`.
- [ ] Interpretar BUY e SELL.
- [ ] Converter preço para `Decimal`.
- [ ] Converter quantidade para `int`.
- [ ] Exibir trades.
- [ ] Tratar comandos inválidos.
- [ ] Criar `__main__.py`.
- [ ] Permitir execução com:

```bash
python -m matching_engine
```

---

## 6. Visualização do livro e prioridade

- [ ] Implementar `print book`.
- [ ] Mostrar BUY do maior para o menor preço.
- [ ] Mostrar SELL do menor para o maior preço.
- [ ] Mostrar preço e quantidade.
- [ ] Garantir prioridade por preço.
- [ ] Garantir FIFO dentro do mesmo preço.
- [ ] Criar testes específicos de visualização e prioridade.

Regra:

```text
1. Melhor preço.
2. Ordem de chegada.
```

---

## 7. IDs, cancelamento e alteração de ordens

- [ ] Adicionar ID único às ordens.
- [ ] Permitir localizar ordens por ID.
- [ ] Implementar `cancel order <id>`.
- [ ] Remover ordens canceladas do livro.
- [ ] Permitir alteração de preço.
- [ ] Permitir alteração de quantidade.
- [ ] Reposicionar ordem após mudança de preço.
- [ ] Fazer a ordem perder prioridade quando necessário.
- [ ] Executar matching caso a alteração gere cruzamento.
- [ ] Criar testes de cancelamento e alteração.

Decisão prevista:

```text
Mudança de preço = perde prioridade.
Redução de quantidade = pode manter prioridade.
Aumento de quantidade = perde prioridade.
```

---

## 8. Pegged Orders

- [ ] Adicionar tipo `PEG`.
- [ ] Criar referências `BID` e `OFFER`.
- [ ] Implementar `peg bid`.
- [ ] Implementar `peg offer`.
- [ ] Fazer Pegged Orders acompanharem automaticamente o preço de referência.
- [ ] Reprecificar quando Best Bid ou Best Offer mudar.
- [ ] Definir comportamento quando não houver referência.
- [ ] Evitar referências recursivas entre Pegged Orders.
- [ ] Executar matching caso a reprecificação gere cruzamento.
- [ ] Criar testes de Pegged Orders.

---

## 9. Validações, casos de borda e revisão técnica

- [ ] Validar preço e quantidade.
- [ ] Tratar livro vazio.
- [ ] Tratar falta de liquidez.
- [ ] Tratar IDs inexistentes.
- [ ] Tratar cancelamentos e alterações inválidas.
- [ ] Garantir consistência das quantidades após trades.
- [ ] Revisar estruturas de dados utilizadas.
- [ ] Documentar complexidades.
- [ ] Avaliar otimizações somente se necessárias.
- [ ] Garantir que todas as decisões técnicas possam ser explicadas.

---

## 10. Testes finais, documentação e entrega

- [ ] Executar todos os testes:

```bash
python -m unittest discover -s tests -v
```

- [ ] Testar manualmente todos os exemplos do enunciado.
- [ ] Atualizar README.
- [ ] Documentar arquitetura, decisões técnicas, complexidades e limitações.
- [ ] Revisar histórico Git e mensagens dos commits.
- [ ] Garantir que `.venv` e arquivos temporários não estejam versionados.
- [ ] Conferir `git status`.
- [ ] Fazer push final.
- [ ] Clonar o repositório em outro diretório.
- [ ] Validar instalação, testes e execução do zero.

---

## Estado atual

```text
Estrutura do projeto     ✓
orders.py                ✓
book.py                  ✓
test_book.py             ✓

Próxima etapa:
engine.py
```
