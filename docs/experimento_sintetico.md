# Experimento sintético com WSM

Este documento descreve a correspondência entre o modelo apresentado na qualificação e sua implementação em `src/experimento_sintetico_wsm.py`.

## 1. Objetivo do experimento

O experimento sintético funciona como uma prova de conceito controlada para verificar se o modelo multicritério responde às prioridades definidas em diferentes contextos operacionais.

Foram definidos 12 perfis sintéticos de Behavior Trees (BTs). Seus atributos são controlados manualmente para representar combinações distintas de características estruturais, adaptabilidade e desempenho. Esses valores **não correspondem a medições coletadas de sistemas reais**.

## 2. Fluxo geral

```text
12 perfis sintéticos de BTs
        ↓
cálculo de f1, f2 e das proxies S, R, M e L
        ↓
composição contextual de f3
        ↓
normalização dos critérios
        ↓
agregação pelo Weighted Sum Model (WSM)
        ↓
ranking por contexto operacional
        ↓
análise de sensibilidade dos pesos
        ↓
exportação dos resultados
```

## 3. Correspondência entre modelo e código

| Elemento do modelo | Interpretação | Implementação |
|---|---|---|
| `f1` | tempo de execução, critério de minimização | `desempenho()` |
| `f2` | entradas dinâmicas / entradas disponíveis | `adaptabilidade()` |
| `S` | simplicidade estrutural | `simplicidade()` |
| `R` | rastreabilidade estrutural | `rastreabilidade()` |
| `M` | modularidade | `modularidade()` |
| `L` | clareza lógica | `clareza_logica()` |
| `f3` | explicabilidade estrutural contextual | `explicabilidade()` |
| Normalização de custo | menor valor é melhor | `normalizar_minimizacao()` |
| Normalização de benefício | maior valor é melhor | `normalizar_maximizacao()` |
| WSM | agregação multicritério | `avaliar_contexto()` |
| Sensibilidade | perturbação dos pesos | `gerar_pesos_vizinhos()` e `analisar_sensibilidade()` |

## 4. Métricas utilizadas

### 4.1 Desempenho — `f1`

No conjunto sintético, `f1` é representado pelo tempo de execução em milissegundos:

```text
f1(T) = tempo_execucao_ms
```

Como menor tempo é considerado melhor, o critério é tratado como **minimização** durante a normalização.

### 4.2 Adaptabilidade — `f2`

A adaptabilidade é calculada como:

```text
f2(T) = entradas_dinamicas / entradas_disponiveis
```

No conjunto sintético, esses valores são controlados manualmente, mas a interpretação foi definida para permanecer alinhada à etapa posterior com BTs reais do Nav2.

### 4.3 Explicabilidade estrutural — `f3`

A explicabilidade é uma combinação ponderada das quatro proxies estruturais:

```text
f3(T,C) = wS*S(T) + wR*R(T) + wM*M(T) + wL*L(T)
```

Os pesos internos dependem do contexto operacional.

#### Simplicidade — `S`

```text
S(T) = 1 / (1 + 0.5*profundidade + 0.5*ramificacao)
```

#### Rastreabilidade — `R`

```text
R(T) = 1 / (1 + caminhos_decisao)
```

#### Modularidade — `M`

```text
M(T) = modulos_reutilizaveis / modulos_totais
```

#### Clareza lógica — `L`

```text
L(T) = 1 / (1 + condicoes_compostas)
```

Essas métricas devem ser interpretadas como **proxies estruturais propostas no trabalho**, e não como medidas cognitivas validadas de compreensão humana.

## 5. Contextos operacionais

O script utiliza três contextos de referência.

| Contexto | Desempenho | Adaptabilidade | Explicabilidade |
|---|---:|---:|---:|
| Tempo Real | 0.70 | 0.10 | 0.20 |
| Equipe Iniciante | 0.10 | 0.20 | 0.70 |
| Ambiente Dinâmico | 0.10 | 0.70 | 0.20 |

Os pesos representam hipóteses exploratórias de prioridade, não valores universalmente corretos.

### Pesos internos de explicabilidade

| Contexto | S | R | M | L |
|---|---:|---:|---:|---:|
| Tempo Real | 0.40 | 0.10 | 0.20 | 0.30 |
| Equipe Iniciante | 0.20 | 0.30 | 0.30 | 0.20 |
| Ambiente Dinâmico | 0.20 | 0.20 | 0.40 | 0.20 |

## 6. Normalização e WSM

O desempenho é normalizado como critério de minimização. Adaptabilidade e explicabilidade são normalizadas como critérios de maximização.

Após a normalização, o score global de cada BT é calculado por:

```text
Score(T,C) = w1*f1_norm + w2*f2_norm + w3*f3_norm
```

As BTs são ordenadas de forma decrescente pelo score.

## 7. Resultados esperados com os pesos de referência

### Tempo Real

1. BT Drone Crítico — `0.811`
2. BT Missão Crítica — `0.743`
3. BT Robô Industrial — `0.707`

### Equipe Iniciante

1. BT Sistema Médico — `0.877`
2. BT Modular — `0.782`
3. BT Robô Industrial — `0.693`

### Ambiente Dinâmico

1. BT Configurável — `0.838`
2. BT Monitoramento IoT — `0.707`
3. BT Sistema Médico — `0.663`

A mudança do vencedor entre os contextos é o comportamento central observado neste experimento: o ranking responde às prioridades contextuais definidas pelos pesos.

## 8. Análise de sensibilidade

A análise de sensibilidade varia deterministicamente:

- os três pesos principais do contexto;
- os quatro pesos internos da explicabilidade;
- passo de `0.05`;
- perturbação máxima de `±0.10` em relação aos pesos-base;
- soma dos pesos mantida em `1.0`.

Para cada contexto são obtidas:

- 19 combinações válidas dos pesos principais;
- 85 combinações válidas dos pesos internos de explicabilidade;
- 1.615 configurações avaliadas no total.

### Estabilidade do vencedor-base

| Contexto | Vencedor-base | Vitórias | Estabilidade |
|---|---|---:|---:|
| Tempo Real | BT Drone Crítico | 1475 / 1615 | 91.3% |
| Equipe Iniciante | BT Sistema Médico | 1615 / 1615 | 100.0% |
| Ambiente Dinâmico | BT Configurável | 1615 / 1615 | 100.0% |

A análise não demonstra que os pesos escolhidos sejam universalmente corretos. Ela verifica se os resultados dependem excessivamente de uma única configuração pontual de pesos dentro da vizinhança avaliada.

## 9. Como reproduzir

A partir da raiz do repositório:

```bash
python src/experimento_sintetico_wsm.py
```

O script utiliza apenas a biblioteca padrão do Python.

## 10. Arquivos gerados

```text
results/relatorio_experimento_sintetico.txt
results/resultados_sinteticos.csv
results/sensibilidade_pesos_sinteticos.csv
```

`resultados_sinteticos.csv` contém o ranking completo e as métricas de cada BT em cada contexto.

`sensibilidade_pesos_sinteticos.csv` contém a distribuição das vitórias observadas na análise de sensibilidade.

## 11. Escopo desta etapa

Este experimento avalia o comportamento do mecanismo multicritério em um ambiente controlado. A etapa com Nav2 tem objetivo diferente: verificar se as métricas estruturais e de adaptabilidade podem ser operacionalizadas sobre artefatos reais. A comparação direta de desempenho entre as BTs reais não é realizada nesta etapa porque elas executam tarefas distintas e não foram avaliadas sob cenários equivalentes.
