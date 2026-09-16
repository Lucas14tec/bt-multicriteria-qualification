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
│   ├── experimento_sintetico_wsm.py
│   └── extrator_nav2_metricas.py
├── data/
│   └── nav2/
│       ├── README.md
│       ├── follow_point.xml
│       ├── navigate_to_pose_w_bounds_check.xml
│       ├── navigate_to_pose_w_replanning_and_recovery.xml
│       ├── navigate_through_poses_w_replanning_and_recovery.xml
│       ├── navigate_on_route_graph_w_recovery.xml
│       └── nav2_tree_nodes.xml
├── results/
│   ├── README.md
│   ├── resultados_sinteticos.csv
│   ├── sensibilidade_pesos_sinteticos.csv
│   └── nav2/
│       └── resultados_nav2.csv
└── docs/
    ├── README.md
    ├── experimento_sintetico.md
    └── experimento_nav2.md
```

## Experimento 1 — BTs sintéticas + WSM

Arquivo principal:

```text
src/experimento_sintetico_wsm.py
```

O script define 12 perfis sintéticos controlados, calcula `f1`, `f2`, `S`, `R`, `M`, `L` e `f3`, normaliza os critérios, aplica o **Weighted Sum Model (WSM)**, produz rankings para três contextos e executa uma análise de sensibilidade dos pesos.

### Observação importante

Os atributos das 12 BTs deste experimento são **dados sintéticos controlados de prova de conceito**. Eles não representam medições coletadas de sistemas reais.

### Resultados esperados — pesos de referência

| Contexto | BT vencedora | Score |
|---|---|---:|
| Tempo Real | BT Drone Crítico | 0.811 |
| Equipe Iniciante | BT Sistema Médico | 0.877 |
| Ambiente Dinâmico | BT Configurável | 0.838 |

Na análise de sensibilidade são avaliadas **1.615 configurações de pesos por contexto**.

## Experimento 2 — BTs reais do Nav2

Arquivo principal:

```text
src/extrator_nav2_metricas.py
```

Esta etapa realiza uma **análise estática** de cinco Behavior Trees reais do Nav2. O extrator lê os XMLs em `data/nav2/`, calcula características estruturais, as proxies `S`, `R`, `M` e `L`, a explicabilidade estrutural `f3` para os três contextos e a adaptabilidade `f2` a partir das portas de entrada utilizadas.

O critério de desempenho `f1` **não é medido nesta etapa**, pois as cinco BTs implementam comportamentos distintos e não possuem cenários de execução diretamente comparáveis.

O resultado consolidado está em:

```text
results/nav2/resultados_nav2.csv
```

### Modelo auxiliar de portas

O arquivo `data/nav2/nav2_tree_nodes.xml` deste repositório é um **subconjunto de reprodução** derivado do arquivo oficial do Nav2 usado no experimento. Ele preserva apenas os IDs de nós e nomes das `input_port` necessários às cinco árvores analisadas. A execução com esse subconjunto foi comparada à execução com o arquivo oficial completo e produziu resultados numericamente idênticos.

### Proveniência dos artefatos Nav2

Os XMLs analisados foram obtidos do repositório oficial `ros-navigation/navigation2`, no diretório `nav2_bt_navigator/behavior_trees/`. O commit ou tag exato da coleta original não foi registrado durante o experimento. Por isso, este repositório preserva as cópias exatas dos arquivos efetivamente utilizados e **não atribui retroativamente um SHA de origem**.

## Rastreabilidade entre texto, código e resultados

A documentação técnica está em:

- [`docs/experimento_sintetico.md`](docs/experimento_sintetico.md)
- [`docs/experimento_nav2.md`](docs/experimento_nav2.md)

Esses documentos mostram a correspondência entre as definições apresentadas no texto, as funções do código e os resultados exportados.

## Contextos avaliados

- Tempo Real
- Equipe Iniciante
- Ambiente Dinâmico

## Requisitos

- Python 3.10 ou superior
- Nenhuma biblioteca externa é necessária para os experimentos atualmente incluídos.

## Como executar

### Experimento sintético

```bash
python src/experimento_sintetico_wsm.py
```

### Experimento Nav2

```bash
python src/extrator_nav2_metricas.py
```

## Status do repositório

- [x] Experimento sintético com WSM
- [x] Análise de sensibilidade dos pesos
- [x] Resultados reproduzíveis do experimento sintético
- [x] Documentação de rastreabilidade do Experimento 1
- [x] Código do experimento com BTs reais do Nav2
- [x] Cinco XMLs reais utilizados no experimento Nav2
- [x] Modelo auxiliar de portas necessário para reprodução
- [x] Resultado consolidado do experimento Nav2
- [x] Documentação de rastreabilidade do experimento Nav2

## Escopo atual

Este repositório corresponde ao material experimental apresentado na qualificação. Extensões posteriores, como comparação com outros métodos multicritério ou novos experimentos de desempenho, devem ser adicionadas separadamente para não alterar retrospectivamente a versão utilizada na banca.
