# Experimento com Behavior Trees reais do Nav2

Este documento descreve a correspondência entre o texto de qualificação, o código e os resultados do experimento realizado com Behavior Trees reais do sistema de navegação Nav2 (ROS 2).

## Objetivo

A etapa com Nav2 verifica se as métricas propostas podem ser operacionalizadas sobre artefatos reais representados em XML. Nesta etapa são extraídas características estruturais e de parametrização; o critério de desempenho `f1` não é medido, pois as cinco BTs analisadas implementam tarefas distintas e não possuem cenários de execução diretamente comparáveis.

## Código principal

```text
src/extrator_nav2_metricas.py
```

## Entradas

As cinco Behavior Trees analisadas estão em `data/nav2/`:

- `follow_point.xml`
- `navigate_to_pose_w_bounds_check.xml`
- `navigate_to_pose_w_replanning_and_recovery.xml`
- `navigate_through_poses_w_replanning_and_recovery.xml`
- `navigate_on_route_graph_w_recovery.xml`

Os XMLs foram obtidos do repositório oficial `ros-navigation/navigation2`, no diretório `nav2_bt_navigator/behavior_trees/`.

### Modelo de portas dos nós

O arquivo `data/nav2/nav2_tree_nodes.xml` incluído neste repositório é um **subconjunto de reprodução** derivado do arquivo oficial `nav2_tree_nodes.xml` usado durante o experimento. Ele mantém os IDs dos nós e os nomes das `input_port` necessários às cinco BTs analisadas. Campos não utilizados pelo extrator, como descrições, tipos, portas de saída e definições de nós que não aparecem no conjunto experimental, foram removidos para manter o repositório compacto.

A equivalência foi verificada executando o extrator com o arquivo oficial completo e com este subconjunto: os valores gerados para todas as cinco BTs foram numericamente idênticos.

## Correspondência entre métricas e código

| Elemento do modelo | Implementação |
|---|---|
| Profundidade | `calcular_profundidade_bt()` |
| Ramificação máxima | `calcular_ramificacao_maxima()` |
| Número de nós | `contar_nos_bt()` |
| Condições/estruturas compostas | `contar_condicoes_compostas()` |
| Folhas comportamentais usadas na proxy de rastreabilidade | `contar_caminhos_decisao()` |
| Simplicidade `S` | calculada em `analisar_bt()` |
| Rastreabilidade `R` | calculada em `analisar_bt()` |
| Modularidade `M` | `calcular_modularidade()` |
| Clareza lógica `L` | calculada em `analisar_bt()` |
| Explicabilidade estrutural `f3` | `calcular_explicabilidade()` |
| Entradas disponíveis/usadas/dinâmicas | `calcular_parametrizacao()` |
| Adaptabilidade `f2` | `calcular_parametrizacao()` |

## Definições operacionais

### Simplicidade

```text
S = 1 / (1 + 0.5 * profundidade + 0.5 * ramificacao)
```

Os wrappers XML `<root>` e `<BehaviorTree>` são excluídos da profundidade e da contagem de nós comportamentais.

### Rastreabilidade

```text
R = 1 / (1 + folhas_comportamentais)
```

No código e no texto de qualificação, o termo `caminhos_decisao` representa operacionalmente a quantidade de folhas comportamentais da BT. Trata-se de uma proxy topológica, não da enumeração exata de todos os traços possíveis em tempo de execução.

### Modularidade

Cada subárvore enraizada em um nó de controle gera uma assinatura estrutural baseada na tag do nó e nas assinaturas de seus descendentes. Atributos XML são ignorados. Assinaturas repetidas são contabilizadas como módulos reutilizáveis:

```text
M = modulos_reutilizaveis / modulos_totais
```

### Clareza lógica

```text
L = 1 / (1 + estruturas_compostas)
```

Os tipos considerados estão definidos em `TIPOS_CONDICAO_COMPOSTA` no código.

### Adaptabilidade

Para cada ocorrência de nó, as `input_port` declaradas no modelo de nós são consideradas entradas disponíveis. Uma entrada usada é classificada como dinâmica quando seu valor XML possui a forma `{variavel}`; os demais valores são tratados como literais.

```text
f2 = inputs_dinamicos / inputs_disponiveis
```

O grau de parametrização explícita também é exportado como informação auxiliar:

```text
grau_parametrizacao = inputs_usados / inputs_disponiveis
```

## Como executar

A partir da raiz do repositório:

```bash
python src/extrator_nav2_metricas.py
```

Por padrão, o script lê `data/nav2/` e grava os resultados em `results/nav2/`.

Também é possível definir diretórios manualmente:

```bash
python src/extrator_nav2_metricas.py --data-dir data/nav2 --output-dir results/nav2
```

## Resultado consolidado

O arquivo reproduzível principal é:

```text
results/nav2/resultados_nav2.csv
```

Alguns valores de referência apresentados na qualificação:

| BT | S | R | M | L | f2 |
|---|---:|---:|---:|---:|---:|
| follow_point | 0.182 | 0.167 | 0.000 | 0.333 | 0.261 |
| navigate_to_pose_w_bounds_check | 0.286 | 0.250 | 0.000 | 0.333 | 0.278 |
| navigate_to_pose_w_replanning_and_recovery | 0.118 | 0.042 | 0.000 | 0.071 | 0.122 |
| navigate_through_poses_w_replanning_and_recovery | 0.118 | 0.040 | 0.000 | 0.067 | 0.174 |
| navigate_on_route_graph_w_recovery | 0.125 | 0.034 | 0.095 | 0.056 | 0.236 |

## Limitação desta etapa

Não é produzido um ranking multicritério final das cinco BTs reais nesta etapa, pois `f1` não foi medido em condições equivalentes. O experimento Nav2 serve para verificar a operacionalização das métricas estruturais e de adaptabilidade sobre artefatos reais, e não para declarar uma BT como melhor de forma geral.
