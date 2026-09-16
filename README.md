# Seleção Multicritério de Behavior Trees — Qualificação

Repositório de apoio à qualificação da pesquisa sobre **seleção multicritério de Behavior Trees (BTs) em diferentes contextos operacionais**.

O objetivo deste repositório é manter, de forma organizada e reproduzível, os códigos, dados de entrada e resultados utilizados nos experimentos apresentados no texto de qualificação.

## Estrutura

```text
bt-multicriteria-qualification/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   └── experimento_sintetico_wsm.py
├── data/
│   └── nav2/
│       └── README.md
├── results/
│   ├── README.md
│   ├── resultados_sinteticos.csv
│   └── sensibilidade_pesos_sinteticos.csv
└── docs/
    ├── README.md
    └── experimento_sintetico.md
```

## Experimento 1 — BTs sintéticas + WSM

Arquivo principal:

```text
src/experimento_sintetico_wsm.py
```

O script:

1. define 12 perfis sintéticos controlados de Behavior Trees;
2. calcula o critério de desempenho `f1`;
3. calcula a adaptabilidade `f2`;
4. calcula as proxies estruturais `S`, `R`, `M` e `L`;
5. compõe a explicabilidade estrutural `f3` de acordo com o contexto;
6. normaliza os critérios;
7. aplica o **Weighted Sum Model (WSM)**;
8. gera rankings para três contextos operacionais;
9. executa análise de sensibilidade dos pesos;
10. exporta os resultados para `results/`.

### Observação importante

Os atributos das 12 BTs deste experimento são **dados sintéticos controlados de prova de conceito**. Eles não representam medições coletadas de sistemas reais.

## Rastreabilidade entre texto, código e resultados

A documentação técnica detalhada está em:

- [`docs/experimento_sintetico.md`](docs/experimento_sintetico.md)

Esse documento mostra a correspondência entre cada elemento do modelo (`f1`, `f2`, `S`, `R`, `M`, `L`, `f3`, normalização, WSM e sensibilidade), as funções implementadas no código e os resultados esperados.

## Contextos avaliados

- Tempo Real
- Equipe Iniciante
- Ambiente Dinâmico

## Requisitos

- Python 3.10 ou superior
- Nenhuma biblioteca externa é necessária para o Experimento 1.

## Como executar

A partir da raiz do repositório:

```bash
python src/experimento_sintetico_wsm.py
```

O script gera:

```text
results/relatorio_experimento_sintetico.txt
results/resultados_sinteticos.csv
results/sensibilidade_pesos_sinteticos.csv
```

## Resultados esperados — pesos de referência

| Contexto | BT vencedora | Score |
|---|---|---:|
| Tempo Real | BT Drone Crítico | 0.811 |
| Equipe Iniciante | BT Sistema Médico | 0.877 |
| Ambiente Dinâmico | BT Configurável | 0.838 |

Na análise de sensibilidade são avaliadas **1.615 configurações de pesos por contexto**.

## Status do repositório

- [x] Experimento sintético com WSM
- [x] Análise de sensibilidade dos pesos
- [x] Resultados reproduzíveis do experimento sintético
- [x] Documentação de rastreabilidade do Experimento 1
- [ ] Código do experimento com BTs reais do Nav2
- [ ] XMLs e arquivo de definição de nós utilizados no Nav2
- [ ] Documentação de rastreabilidade do experimento Nav2

## Próximas adições

Os próximos códigos e dados da qualificação serão incorporados mantendo esta organização. A pasta `data/nav2/` está reservada para os artefatos reais usados no experimento com Nav2 e a pasta `src/` receberá o respectivo extrator/analisador.
