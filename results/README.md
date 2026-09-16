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

## Valores de referência

Os seguintes vencedores devem ser reproduzidos com os pesos-base:

| Contexto | BT vencedora | Score |
|---|---|---:|
| Tempo Real | BT Drone Crítico | 0.811 |
| Equipe Iniciante | BT Sistema Médico | 0.877 |
| Ambiente Dinâmico | BT Configurável | 0.838 |

Na análise de sensibilidade são avaliadas 1.615 configurações por contexto. As estabilidades esperadas dos vencedores-base são 91.3%, 100.0% e 100.0%, respectivamente.

A documentação técnica completa deste experimento está em [`docs/experimento_sintetico.md`](../docs/experimento_sintetico.md).
