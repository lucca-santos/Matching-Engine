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

- [x] Criar `engine.py`.
- [x] Criar classe `MatchingEngine`.
- [x] Integrar a engine ao `OrderBook`.
- [x] Implementar Market Buy.
- [x] Implementar Market Sell.
- [x] Implementar execução total e parcial.
- [x] Permitir execução contra várias ordens e vários níveis de preço.
- [x] Garantir que Market Orders não permaneçam no livro.
- [x] Gerar trades no formato:

```text
Trade, price: <price>, qty: <qty>
```

---

## 4. Matching de Limit Orders e testes da engine

- [x] Inserir Limit Orders que não cruzam o livro.
- [x] Implementar Limit Buy agressiva.
- [x] Implementar Limit Sell agressiva.
- [x] Respeitar o preço limite da ordem.
- [x] Manter no livro a quantidade restante após execução parcial.
- [x] Modificar `test_engine.py`.
- [x] Testar Market Buy e Market Sell.
- [x] Testar execuções totais e parciais.
- [x] Testar múltiplas ordens e múltiplos preços.
- [x] Reproduzir o exemplo original do problema.

Decisão técnica:

```text
Limit Orders que cruzarem o livro serão executadas.
Caso reste quantidade, a sobra permanecerá no livro no preço limite.
```

---

## 5. Interface de linha de comando

- [x] Criar `cli.py`.
- [x] Interpretar comandos `limit` e `market`.
- [x] Interpretar BUY e SELL.
- [x] Converter preço para `Decimal`.
- [x] Converter quantidade para `int`.
- [x] Exibir trades.
- [x] Tratar comandos inválidos.
- [x] Criar `__main__.py`.
- [x] Permitir execução com:

```bash
python -m matching_engine
```

---

## 6. Visualização do livro e prioridade

- [x] Implementar `print book`.
- [x] Mostrar BUY do maior para o menor preço.
- [x] Mostrar SELL do menor para o maior preço.
- [x] Mostrar preço e quantidade.
- [x] Garantir prioridade por preço.
- [x] Garantir FIFO dentro do mesmo preço.
- [x] Criar testes específicos de visualização e prioridade.

Regra:

```text
1. Melhor preço.
2. Ordem de chegada.
```

---

## 7. IDs, cancelamento e alteração de ordens

- [x] Adicionar ID único às ordens.
- [x] Permitir localizar ordens por ID.
- [x] Implementar `cancel order <id>`.
- [x] Remover ordens canceladas do livro.
- [x] Permitir alteração de preço.
- [x] Permitir alteração de quantidade.
- [x] Reposicionar ordem após mudança de preço.
- [x] Fazer a ordem perder prioridade quando necessário.
- [x] Executar matching caso a alteração gere cruzamento.
- [x] Criar testes de cancelamento e alteração.

Decisão prevista:

```text
Mudança de preço = perde prioridade.
Redução de quantidade = pode manter prioridade.
Aumento de quantidade = perde prioridade.
```

---

## 8. Pegged Orders

- [x] Adicionar tipo `PEG`.
- [x] Criar referências `BID` e `OFFER`.
- [x] Implementar `peg bid`.
- [x] Implementar `peg offer`.
- [x] Fazer Pegged Orders acompanharem automaticamente o preço de referência.
- [x] Reprecificar quando Best Bid ou Best Offer mudar.
- [x] Definir comportamento quando não houver referência.
- [x] Evitar referências recursivas entre Pegged Orders.
- [x] Executar matching caso a reprecificação gere cruzamento.
- [x] Criar testes de Pegged Orders.

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