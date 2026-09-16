# Resultados

Esta pasta contém as saídas reproduzíveis geradas pelos scripts do repositório.

## Experimento sintético

Execute, a partir da raiz do repositório:

```bash
python src/experimento_sintetico_wsm.py
```

Arquivos gerados:

- `relatorio_experimento_sintetico.txt`: relatório textual completo da execução;
- `resultados_sinteticos.csv`: métricas, valores normalizados, posições e scores das 12 BTs nos três contextos;
- `sensibilidade_pesos_sinteticos.csv`: distribuição das vitórias observadas na análise de sensibilidade.

Os vencedores esperados com os pesos-base são Drone Crítico (Tempo Real), Sistema Médico (Equipe Iniciante) e Configurável (Ambiente Dinâmico).

## Experimento Nav2

Execute:

```bash
python src/extrator_nav2_metricas.py
```

O resultado consolidado é gravado em:

```text
results/nav2/resultados_nav2.csv
```

Esse arquivo contém os atributos estruturais, proxies `S`, `R`, `M`, `L`, valores de `f3`, informações de parametrização e adaptabilidade `f2` das cinco BTs reais analisadas.

O experimento Nav2 não produz um score multicritério final porque o critério de desempenho `f1` não foi medido em cenários comparáveis.

## Documentação técnica

- [`docs/experimento_sintetico.md`](../docs/experimento_sintetico.md)
- [`docs/experimento_nav2.md`](../docs/experimento_nav2.md)
