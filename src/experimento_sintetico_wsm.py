"""
Experimento sintético da pesquisa:
"Seleção Multicritério de Behavior Trees em Diferentes Contextos Operacionais".

Este script:
1. define 12 perfis sintéticos controlados de Behavior Trees;
2. calcula f1, f2 e as proxies estruturais S, R, M e L;
3. calcula f3 de acordo com o contexto operacional;
4. normaliza os critérios;
5. aplica o Weighted Sum Model (WSM);
6. produz rankings para três contextos operacionais;
7. executa uma análise de sensibilidade dos pesos;
8. exporta os resultados em TXT e CSV.

IMPORTANTE:
Os atributos das BTs sintéticas são dados controlados de prova de conceito.
Eles não representam medições obtidas de sistemas reais.
"""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import Iterable


# =============================================================================
# CONFIGURAÇÃO GERAL
# =============================================================================

PASSO_SENSIBILIDADE = 0.05
VARIACAO_MAXIMA = 0.10
TOLERANCIA_SOMA_PESOS = 1e-9

DIRETORIO_SAIDA = Path(__file__).resolve().parents[1] / "results"


# =============================================================================
# MODELO DA BT SINTÉTICA
# =============================================================================

@dataclass(frozen=True)
class BT:
    """Representa um perfil sintético controlado de Behavior Tree."""

    nome: str

    # Atributos estruturais usados nas proxies de explicabilidade.
    profundidade: int
    ramificacao: int
    condicoes_compostas: int
    modulos_reutilizaveis: int
    modulos_totais: int
    caminhos_decisao: int

    # f1: tempo bruto de execução em milissegundos (quanto menor, melhor).
    tempo_execucao_ms: float

    # f2: análogo sintético da definição aplicada posteriormente ao Nav2.
    entradas_dinamicas: int
    entradas_disponiveis: int


# =============================================================================
# DADOS SINTÉTICOS CONTROLADOS
# =============================================================================
#
# A semântica de f2 é mantida compatível com o experimento real:
#
#     f2 = entradas_dinamicas / entradas_disponiveis
#
# Os valores abaixo foram definidos manualmente para representar perfis distintos
# de BTs e permitir a avaliação controlada do modelo multicritério.
# =============================================================================

BTS = [
    BT(
        nome="BT Compacta",
        profundidade=6,
        ramificacao=5,
        condicoes_compostas=8,
        modulos_reutilizaveis=1,
        modulos_totais=6,
        caminhos_decisao=7,
        tempo_execucao_ms=1.2,
        entradas_dinamicas=1,
        entradas_disponiveis=8,
    ),
    BT(
        nome="BT Modular",
        profundidade=3,
        ramificacao=2,
        condicoes_compostas=2,
        modulos_reutilizaveis=5,
        modulos_totais=6,
        caminhos_decisao=3,
        tempo_execucao_ms=2.5,
        entradas_dinamicas=3,
        entradas_disponiveis=8,
    ),
    BT(
        nome="BT Configurável",
        profundidade=4,
        ramificacao=3,
        condicoes_compostas=3,
        modulos_reutilizaveis=4,
        modulos_totais=6,
        caminhos_decisao=4,
        tempo_execucao_ms=3.5,
        entradas_dinamicas=8,
        entradas_disponiveis=8,
    ),
    BT(
        nome="BT Híbrida A",
        profundidade=4,
        ramificacao=3,
        condicoes_compostas=4,
        modulos_reutilizaveis=3,
        modulos_totais=6,
        caminhos_decisao=4,
        tempo_execucao_ms=2.0,
        entradas_dinamicas=4,
        entradas_disponiveis=8,
    ),
    BT(
        nome="BT Híbrida B",
        profundidade=5,
        ramificacao=4,
        condicoes_compostas=5,
        modulos_reutilizaveis=4,
        modulos_totais=6,
        caminhos_decisao=5,
        tempo_execucao_ms=1.8,
        entradas_dinamicas=5,
        entradas_disponiveis=8,
    ),
    BT(
        nome="BT Drone Crítico",
        profundidade=3,
        ramificacao=2,
        condicoes_compostas=2,
        modulos_reutilizaveis=1,
        modulos_totais=5,
        caminhos_decisao=2,
        tempo_execucao_ms=0.8,
        entradas_dinamicas=1,
        entradas_disponiveis=8,
    ),
    BT(
        nome="BT NPC Jogo AAA",
        profundidade=7,
        ramificacao=5,
        condicoes_compostas=9,
        modulos_reutilizaveis=4,
        modulos_totais=8,
        caminhos_decisao=8,
        tempo_execucao_ms=2.5,
        entradas_dinamicas=4,
        entradas_disponiveis=10,
    ),
    BT(
        nome="BT Robô Industrial",
        profundidade=4,
        ramificacao=3,
        condicoes_compostas=3,
        modulos_reutilizaveis=6,
        modulos_totais=8,
        caminhos_decisao=4,
        tempo_execucao_ms=1.5,
        entradas_dinamicas=3,
        entradas_disponiveis=6,
    ),
    BT(
        nome="BT Monitoramento IoT",
        profundidade=5,
        ramificacao=3,
        condicoes_compostas=5,
        modulos_reutilizaveis=5,
        modulos_totais=8,
        caminhos_decisao=6,
        tempo_execucao_ms=2.0,
        entradas_dinamicas=8,
        entradas_disponiveis=10,
    ),
    BT(
        nome="BT Veículo Autônomo",
        profundidade=6,
        ramificacao=4,
        condicoes_compostas=8,
        modulos_reutilizaveis=5,
        modulos_totais=9,
        caminhos_decisao=7,
        tempo_execucao_ms=1.3,
        entradas_dinamicas=7,
        entradas_disponiveis=10,
    ),
    BT(
        nome="BT Sistema Médico",
        profundidade=4,
        ramificacao=2,
        condicoes_compostas=2,
        modulos_reutilizaveis=7,
        modulos_totais=8,
        caminhos_decisao=3,
        tempo_execucao_ms=1.8,
        entradas_dinamicas=5,
        entradas_disponiveis=8,
    ),
    BT(
        nome="BT Missão Crítica",
        profundidade=8,
        ramificacao=5,
        condicoes_compostas=10,
        modulos_reutilizaveis=5,
        modulos_totais=10,
        caminhos_decisao=9,
        tempo_execucao_ms=0.9,
        entradas_dinamicas=4,
        entradas_disponiveis=10,
    ),
]


# =============================================================================
# PESOS DO MODELO
# =============================================================================

PESOS_EXPLICABILIDADE = {
    "Tempo Real": {"S": 0.40, "R": 0.10, "M": 0.20, "L": 0.30},
    "Equipe Iniciante": {"S": 0.20, "R": 0.30, "M": 0.30, "L": 0.20},
    "Ambiente Dinâmico": {"S": 0.20, "R": 0.20, "M": 0.40, "L": 0.20},
}

CONTEXTOS = {
    "Tempo Real": {
        "desempenho": 0.70,
        "adaptabilidade": 0.10,
        "explicabilidade": 0.20,
    },
    "Equipe Iniciante": {
        "desempenho": 0.10,
        "adaptabilidade": 0.20,
        "explicabilidade": 0.70,
    },
    "Ambiente Dinâmico": {
        "desempenho": 0.10,
        "adaptabilidade": 0.70,
        "explicabilidade": 0.20,
    },
}


# =============================================================================
# PROXIES E CRITÉRIOS
# =============================================================================

def simplicidade(bt: BT) -> float:
    """S(T) = 1 / (1 + 0.5*d + 0.5*B)."""
    return 1 / (1 + 0.5 * bt.profundidade + 0.5 * bt.ramificacao)


def rastreabilidade(bt: BT) -> float:
    """R(T) = 1 / (1 + caminhos de decisão)."""
    return 1 / (1 + bt.caminhos_decisao)


def modularidade(bt: BT) -> float:
    """M(T) = módulos reutilizáveis / módulos totais."""
    if bt.modulos_totais == 0:
        return 0.0
    return bt.modulos_reutilizaveis / bt.modulos_totais


def clareza_logica(bt: BT) -> float:
    """L(T) = 1 / (1 + estruturas/condições compostas)."""
    return 1 / (1 + bt.condicoes_compostas)


def adaptabilidade(bt: BT) -> float:
    """f2(T) = entradas dinâmicas / entradas disponíveis."""
    if bt.entradas_disponiveis == 0:
        return 0.0
    return bt.entradas_dinamicas / bt.entradas_disponiveis


def desempenho(bt: BT) -> float:
    """f1(T) = tempo médio de execução em ms; critério de minimização."""
    return bt.tempo_execucao_ms


def explicabilidade(bt: BT, pesos_exp: dict[str, float]) -> tuple[float, float, float, float, float]:
    """Calcula f3(T,C) = ws*S + wr*R + wm*M + wl*L."""
    s = simplicidade(bt)
    r = rastreabilidade(bt)
    m = modularidade(bt)
    l = clareza_logica(bt)

    f3 = (
        pesos_exp["S"] * s
        + pesos_exp["R"] * r
        + pesos_exp["M"] * m
        + pesos_exp["L"] * l
    )

    return f3, s, r, m, l


# =============================================================================
# VALIDAÇÃO DOS DADOS E PESOS
# =============================================================================

def _soma_aproximadamente_um(valores: Iterable[float]) -> bool:
    return abs(sum(valores) - 1.0) <= TOLERANCIA_SOMA_PESOS


def validar_configuracao() -> None:
    """Verifica inconsistências básicas antes da execução do experimento."""
    for bt in BTS:
        if bt.entradas_disponiveis < 0 or bt.entradas_dinamicas < 0:
            raise ValueError(f"Entradas inválidas em {bt.nome}.")
        if bt.entradas_dinamicas > bt.entradas_disponiveis:
            raise ValueError(f"Entradas dinâmicas excedem as disponíveis em {bt.nome}.")
        if bt.modulos_totais < 0 or bt.modulos_reutilizaveis < 0:
            raise ValueError(f"Quantidade de módulos inválida em {bt.nome}.")
        if bt.modulos_reutilizaveis > bt.modulos_totais:
            raise ValueError(f"Módulos reutilizáveis excedem os módulos totais em {bt.nome}.")
        if bt.tempo_execucao_ms <= 0:
            raise ValueError(f"Tempo de execução inválido em {bt.nome}.")

    if set(CONTEXTOS) != set(PESOS_EXPLICABILIDADE):
        raise ValueError("Contextos e pesos internos de explicabilidade não correspondem.")

    for contexto, pesos in CONTEXTOS.items():
        if not _soma_aproximadamente_um(pesos.values()):
            raise ValueError(f"Os pesos principais de '{contexto}' não somam 1.")

    for contexto, pesos in PESOS_EXPLICABILIDADE.items():
        if not _soma_aproximadamente_um(pesos.values()):
            raise ValueError(f"Os pesos internos de '{contexto}' não somam 1.")


# =============================================================================
# NORMALIZAÇÃO
# =============================================================================

def normalizar_maximizacao(valores: list[float]) -> list[float]:
    """Min-max para critérios em que maior valor representa melhor resultado."""
    minimo = min(valores)
    maximo = max(valores)

    if minimo == maximo:
        return [1.0 for _ in valores]

    return [(x - minimo) / (maximo - minimo) for x in valores]


def normalizar_minimizacao(valores: list[float]) -> list[float]:
    """Min-max invertido para critérios em que menor valor representa melhor resultado."""
    minimo = min(valores)
    maximo = max(valores)

    if minimo == maximo:
        return [1.0 for _ in valores]

    return [(maximo - x) / (maximo - minimo) for x in valores]


# =============================================================================
# AVALIAÇÃO WSM DE UM CONTEXTO
# =============================================================================

def avaliar_contexto(
    contexto: str,
    pesos_contexto: dict[str, float] | None = None,
    pesos_exp: dict[str, float] | None = None,
) -> list[dict]:
    """Calcula os critérios, normaliza os valores e produz o ranking WSM."""
    if pesos_contexto is None:
        pesos_contexto = CONTEXTOS[contexto]

    if pesos_exp is None:
        pesos_exp = PESOS_EXPLICABILIDADE[contexto]

    tempos: list[float] = []
    adaps: list[float] = []
    exps: list[float] = []
    detalhes: list[dict] = []

    for bt in BTS:
        f3, s, r, m, l = explicabilidade(bt, pesos_exp)
        f1 = desempenho(bt)
        f2 = adaptabilidade(bt)

        tempos.append(f1)
        adaps.append(f2)
        exps.append(f3)

        detalhes.append(
            {
                "bt": bt,
                "f1": f1,
                "f2": f2,
                "f3": f3,
                "S": s,
                "R": r,
                "M": m,
                "L": l,
            }
        )

    # f1 é critério de minimização; f2 e f3 são critérios de maximização.
    f1_normalizado = normalizar_minimizacao(tempos)
    f2_normalizado = normalizar_maximizacao(adaps)
    f3_normalizado = normalizar_maximizacao(exps)

    ranking: list[dict] = []

    for i, info in enumerate(detalhes):
        score = (
            pesos_contexto["desempenho"] * f1_normalizado[i]
            + pesos_contexto["adaptabilidade"] * f2_normalizado[i]
            + pesos_contexto["explicabilidade"] * f3_normalizado[i]
        )

        ranking.append(
            {
                **info,
                "f1_normalizado": f1_normalizado[i],
                "f2_normalizado": f2_normalizado[i],
                "f3_normalizado": f3_normalizado[i],
                "score": score,
            }
        )

    ranking.sort(key=lambda registro: registro["score"], reverse=True)

    for posicao, registro in enumerate(ranking, start=1):
        registro["posicao"] = posicao

    return ranking


# =============================================================================
# ANÁLISE DE SENSIBILIDADE DOS PESOS
# =============================================================================

def gerar_pesos_vizinhos(
    pesos_base: dict[str, float],
    passo: float = PASSO_SENSIBILIDADE,
    variacao: float = VARIACAO_MAXIMA,
) -> list[dict[str, float]]:
    """Gera combinações próximas aos pesos-base, mantendo soma igual a 1."""
    chaves = list(pesos_base.keys())
    quantidade_passos = round(1 / passo)
    valores = [round(i * passo, 10) for i in range(quantidade_passos + 1)]

    combinacoes: list[dict[str, float]] = []

    for combinacao in product(valores, repeat=len(chaves)):
        if abs(sum(combinacao) - 1.0) > TOLERANCIA_SOMA_PESOS:
            continue

        dentro_da_faixa = all(
            abs(combinacao[i] - pesos_base[chaves[i]]) <= variacao + TOLERANCIA_SOMA_PESOS
            for i in range(len(chaves))
        )

        if dentro_da_faixa:
            combinacoes.append(dict(zip(chaves, combinacao)))

    return combinacoes


def analisar_sensibilidade(
    contexto: str,
    passo: float = PASSO_SENSIBILIDADE,
    variacao: float = VARIACAO_MAXIMA,
) -> dict:
    """Avalia a estabilidade do vencedor diante de perturbações dos pesos."""
    pesos_contexto_base = CONTEXTOS[contexto]
    pesos_exp_base = PESOS_EXPLICABILIDADE[contexto]

    ranking_base = avaliar_contexto(
        contexto,
        pesos_contexto=pesos_contexto_base,
        pesos_exp=pesos_exp_base,
    )
    vencedor_base = ranking_base[0]["bt"].nome

    variacoes_contexto = gerar_pesos_vizinhos(
        pesos_contexto_base,
        passo=passo,
        variacao=variacao,
    )
    variacoes_exp = gerar_pesos_vizinhos(
        pesos_exp_base,
        passo=passo,
        variacao=variacao,
    )

    vencedores: Counter[str] = Counter()
    total = 0

    for pesos_ctx in variacoes_contexto:
        for pesos_exp in variacoes_exp:
            ranking = avaliar_contexto(
                contexto,
                pesos_contexto=pesos_ctx,
                pesos_exp=pesos_exp,
            )
            vencedores[ranking[0]["bt"].nome] += 1
            total += 1

    return {
        "contexto": contexto,
        "vencedor_base": vencedor_base,
        "total_cenarios": total,
        "variacoes_contexto": len(variacoes_contexto),
        "variacoes_explicabilidade": len(variacoes_exp),
        "vencedores": vencedores,
        "estabilidade_vencedor_base": vencedores[vencedor_base] / total if total else 0.0,
    }


# =============================================================================
# EXPORTAÇÃO DOS RESULTADOS
# =============================================================================

def salvar_csv(caminho: Path, campos: list[str], linhas: list[dict]) -> None:
    """Salva uma lista de dicionários em CSV UTF-8 com BOM para compatibilidade."""
    with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=campos)
        writer.writeheader()
        writer.writerows(linhas)


def executar_experimento() -> tuple[list[str], list[dict], list[dict]]:
    """Executa rankings e sensibilidade, retornando dados prontos para exportação."""
    relatorio: list[str] = []
    linhas_csv: list[dict] = []
    sensibilidade_csv: list[dict] = []

    relatorio.append(
        "RELATÓRIO DO EXPERIMENTO SINTÉTICO ATUALIZADO\n"
        f"Gerado em: {datetime.now()}\n"
    )
    relatorio.append(
        "\nDEFINIÇÕES CONSOLIDADAS:\n"
        "- f1 = tempo de execução (minimizar; direção invertida na normalização)\n"
        "- f2 = entradas dinâmicas / entradas disponíveis\n"
        "- f3 = combinação ponderada de S, R, M e L\n"
    )

    for contexto in CONTEXTOS:
        ranking = avaliar_contexto(contexto)

        print("\n" + "=" * 78)
        print(contexto)
        print("=" * 78)

        relatorio.append("\n" + "=" * 78 + "\n")
        relatorio.append(contexto + "\n")
        relatorio.append("=" * 78 + "\n")

        for registro in ranking:
            bt = registro["bt"]
            linha = (
                f"{registro['posicao']}º -> {bt.nome} | "
                f"Score={registro['score']:.3f} | "
                f"f1={registro['f1']:.3f}ms (norm={registro['f1_normalizado']:.3f}) | "
                f"f2={registro['f2']:.3f} (norm={registro['f2_normalizado']:.3f}) | "
                f"f3={registro['f3']:.3f} (norm={registro['f3_normalizado']:.3f}) | "
                f"S={registro['S']:.3f} "
                f"R={registro['R']:.3f} "
                f"M={registro['M']:.3f} "
                f"L={registro['L']:.3f}"
            )

            print(linha)
            relatorio.append(linha + "\n")

            linhas_csv.append(
                {
                    "contexto": contexto,
                    "posicao": registro["posicao"],
                    "bt": bt.nome,
                    "tempo_ms_f1": registro["f1"],
                    "f1_normalizado": registro["f1_normalizado"],
                    "adaptabilidade_f2": registro["f2"],
                    "f2_normalizado": registro["f2_normalizado"],
                    "explicabilidade_f3": registro["f3"],
                    "f3_normalizado": registro["f3_normalizado"],
                    "S": registro["S"],
                    "R": registro["R"],
                    "M": registro["M"],
                    "L": registro["L"],
                    "score": registro["score"],
                }
            )

        vencedor = ranking[0]["bt"].nome
        print(f"\nEscolhida: {vencedor}")
        relatorio.append(f"\nEscolhida: {vencedor}\n")

    relatorio.append("\n\n" + "#" * 78 + "\n")
    relatorio.append("ANÁLISE DE SENSIBILIDADE DOS PESOS\n")
    relatorio.append("#" * 78 + "\n")
    relatorio.append(
        f"Perturbação determinística: passo {PASSO_SENSIBILIDADE:.2f} e "
        f"variação máxima +/-{VARIACAO_MAXIMA:.2f} em relação aos pesos-base, "
        "mantendo soma = 1.\n"
    )

    print("\n" + "#" * 78)
    print("ANÁLISE DE SENSIBILIDADE DOS PESOS")
    print("#" * 78)

    for contexto in CONTEXTOS:
        resultado = analisar_sensibilidade(contexto)

        print(f"\n{contexto}")
        print(
            f"Vencedor-base: {resultado['vencedor_base']} | "
            f"estabilidade={resultado['estabilidade_vencedor_base']:.1%} | "
            f"cenários avaliados={resultado['total_cenarios']}"
        )

        relatorio.append(f"\n{contexto}\n")
        relatorio.append(
            f"Vencedor-base: {resultado['vencedor_base']}\n"
            f"Combinações dos pesos principais: {resultado['variacoes_contexto']}\n"
            f"Combinações dos pesos internos de f3: {resultado['variacoes_explicabilidade']}\n"
            f"Total de cenários: {resultado['total_cenarios']}\n"
            f"Estabilidade do vencedor-base: {resultado['estabilidade_vencedor_base']:.3f}\n"
        )

        for nome_bt, quantidade in resultado["vencedores"].most_common():
            percentual = quantidade / resultado["total_cenarios"]
            texto = f"  {nome_bt}: {quantidade} cenários ({percentual:.1%})"

            print(texto)
            relatorio.append(texto + "\n")

            sensibilidade_csv.append(
                {
                    "contexto": contexto,
                    "vencedor_base": resultado["vencedor_base"],
                    "bt_vencedora": nome_bt,
                    "quantidade_vitorias": quantidade,
                    "percentual_vitorias": percentual,
                    "total_cenarios": resultado["total_cenarios"],
                    "estabilidade_vencedor_base": resultado["estabilidade_vencedor_base"],
                }
            )

    return relatorio, linhas_csv, sensibilidade_csv


def main() -> None:
    validar_configuracao()
    DIRETORIO_SAIDA.mkdir(parents=True, exist_ok=True)

    relatorio, linhas_csv, sensibilidade_csv = executar_experimento()

    caminho_relatorio = DIRETORIO_SAIDA / "relatorio_experimento_sintetico.txt"
    caminho_resultados = DIRETORIO_SAIDA / "resultados_sinteticos.csv"
    caminho_sensibilidade = DIRETORIO_SAIDA / "sensibilidade_pesos_sinteticos.csv"

    caminho_relatorio.write_text("".join(relatorio), encoding="utf-8")

    salvar_csv(
        caminho_resultados,
        [
            "contexto",
            "posicao",
            "bt",
            "tempo_ms_f1",
            "f1_normalizado",
            "adaptabilidade_f2",
            "f2_normalizado",
            "explicabilidade_f3",
            "f3_normalizado",
            "S",
            "R",
            "M",
            "L",
            "score",
        ],
        linhas_csv,
    )

    salvar_csv(
        caminho_sensibilidade,
        [
            "contexto",
            "vencedor_base",
            "bt_vencedora",
            "quantidade_vitorias",
            "percentual_vitorias",
            "total_cenarios",
            "estabilidade_vencedor_base",
        ],
        sensibilidade_csv,
    )

    print("\nArquivos gerados:")
    print(f"- {caminho_relatorio}")
    print(f"- {caminho_resultados}")
    print(f"- {caminho_sensibilidade}")


if __name__ == "__main__":
    main()
