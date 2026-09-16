"""
Extração de métricas estruturais e de adaptabilidade em Behavior Trees reais do Nav2.

Pesquisa:
"Seleção Multicritério de Behavior Trees em Diferentes Contextos Operacionais".

Este script:
1. lê Behavior Trees reais do Nav2 representadas em XML;
2. extrai atributos estruturais das árvores;
3. calcula as proxies de simplicidade (S), rastreabilidade (R), modularidade (M)
   e clareza lógica (L);
4. calcula a explicabilidade estrutural f3 para três contextos operacionais;
5. estima adaptabilidade f2 a partir do uso de portas de entrada dinâmicas;
6. exporta um CSV consolidado e relatórios individuais por BT.

IMPORTANTE:
- o script realiza análise estática dos artefatos XML;
- o critério de desempenho f1 NÃO é medido nesta etapa;
- "caminhos de decisão" é operacionalizado como a quantidade de folhas
  comportamentais da BT, conforme a definição utilizada no texto de qualificação;
- a modularidade é uma proxy baseada na repetição de assinaturas estruturais de
  subárvores enraizadas em nós de controle. Atributos XML não entram na assinatura.

Estrutura esperada do repositório:

    src/extrator_nav2_metricas.py
    data/nav2/*.xml
    results/nav2/

O arquivo data/nav2/nav2_tree_nodes.xml contém as definições de portas dos nós e
não é tratado como uma Behavior Tree do conjunto experimental.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET


# =============================================================================
# CONFIGURAÇÃO DO MODELO
# =============================================================================

TIPOS_CONDICAO_COMPOSTA = {
    "Fallback",
    "ReactiveFallback",
    "ReactiveSequence",
    "RecoveryNode",
    "PipelineSequence",
    "Sequence",
    "RoundRobin",
}

TIPOS_CONTROLE = {
    "Sequence",
    "Fallback",
    "ReactiveSequence",
    "ReactiveFallback",
    "RecoveryNode",
    "PipelineSequence",
    "RoundRobin",
    "RateController",
    "Inverter",
}

TAGS_ESTRUTURA_XML = {"root", "BehaviorTree"}

PESOS_EXPLICABILIDADE = {
    "Tempo Real": {"S": 0.40, "R": 0.10, "M": 0.20, "L": 0.30},
    "Equipe Iniciante": {"S": 0.20, "R": 0.30, "M": 0.30, "L": 0.20},
    "Ambiente Dinamico": {"S": 0.20, "R": 0.20, "M": 0.40, "L": 0.20},
}


# =============================================================================
# VALIDAÇÕES
# =============================================================================

def validar_pesos() -> None:
    """Confirma que os pesos internos de f3 somam 1 em cada contexto."""
    for contexto, pesos in PESOS_EXPLICABILIDADE.items():
        if abs(sum(pesos.values()) - 1.0) > 1e-9:
            raise ValueError(
                f"Os pesos de explicabilidade do contexto '{contexto}' não somam 1."
            )


def validar_arquivo_xml(arquivo: Path) -> None:
    """Gera uma mensagem clara caso um XML esperado não exista."""
    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo XML não encontrado: {arquivo}")


# =============================================================================
# FUNÇÕES ESTRUTURAIS
# =============================================================================

def assinatura_subarvore(no: ET.Element):
    """
    Produz a assinatura estrutural recursiva de uma subárvore.

    A assinatura considera a tag do nó e a estrutura dos descendentes.
    Atributos XML são deliberadamente ignorados nesta proxy estrutural.
    """
    filhos = tuple(assinatura_subarvore(filho) for filho in no)
    return no.tag, filhos


def calcular_modularidade(elemento: ET.Element) -> tuple[int, int, float]:
    """
    Calcula M = módulos reutilizáveis / módulos totais.

    Cada nó pertencente a TIPOS_CONTROLE define um módulo candidato. Um módulo é
    considerado reutilizável quando sua assinatura estrutural ocorre mais de uma vez.
    """
    assinaturas = [
        assinatura_subarvore(no)
        for no in elemento.iter()
        if no.tag in TIPOS_CONTROLE
    ]

    modulos_totais = len(assinaturas)
    frequencias = Counter(assinaturas)
    modulos_reutilizaveis = sum(
        quantidade for quantidade in frequencias.values() if quantidade > 1
    )

    modularidade = (
        modulos_reutilizaveis / modulos_totais if modulos_totais > 0 else 0.0
    )

    return modulos_totais, modulos_reutilizaveis, modularidade


def contar_caminhos_decisao(elemento: ET.Element) -> int:
    """
    Conta as folhas comportamentais da BT.

    No experimento, esse número é utilizado como proxy topológica de caminhos de
    decisão/terminais para o cálculo de R = 1 / (1 + folhas).
    """
    return sum(
        1
        for no in elemento.iter()
        if no.tag not in TAGS_ESTRUTURA_XML and len(no) == 0
    )


def calcular_profundidade(elemento: ET.Element) -> int:
    """Retorna a profundidade de uma árvore XML, contando o elemento atual."""
    if len(elemento) == 0:
        return 1
    return 1 + max(calcular_profundidade(filho) for filho in elemento)


def calcular_profundidade_bt(raiz_xml: ET.Element) -> int:
    """Calcula a profundidade da BT excluindo <root> e <BehaviorTree>."""
    profundidade_total = calcular_profundidade(raiz_xml)
    return max(profundidade_total - 2, 0)


def calcular_ramificacao_maxima(elemento: ET.Element) -> int:
    """Retorna o maior número de filhos diretos observado em um nó."""
    return max((len(no) for no in elemento.iter()), default=0)


def contar_nos_bt(elemento: ET.Element) -> int:
    """Conta somente elementos comportamentais, excluindo wrappers XML."""
    return sum(1 for no in elemento.iter() if no.tag not in TAGS_ESTRUTURA_XML)


def contar_condicoes_compostas(elemento: ET.Element) -> int:
    """Conta ocorrências dos tipos usados na proxy de clareza lógica L."""
    return sum(1 for no in elemento.iter() if no.tag in TIPOS_CONDICAO_COMPOSTA)


def contar_subtrees(elemento: ET.Element) -> int:
    """Conta elementos <SubTree> explicitamente presentes no XML."""
    return sum(1 for no in elemento.iter() if no.tag == "SubTree")


def contar_nos_controle(elemento: ET.Element) -> int:
    """Conta nós pertencentes ao conjunto TIPOS_CONTROLE."""
    return sum(1 for no in elemento.iter() if no.tag in TIPOS_CONTROLE)


# =============================================================================
# EXPLICABILIDADE E ADAPTABILIDADE
# =============================================================================

def calcular_explicabilidade(
    simplicidade: float,
    rastreabilidade: float,
    modularidade: float,
    clareza_logica: float,
) -> dict[str, float]:
    """Calcula f3 para cada contexto operacional."""
    resultados = {}

    for contexto, pesos in PESOS_EXPLICABILIDADE.items():
        f3 = (
            pesos["S"] * simplicidade
            + pesos["R"] * rastreabilidade
            + pesos["M"] * modularidade
            + pesos["L"] * clareza_logica
        )
        resultados[contexto] = f3

    return resultados


def carregar_definicoes_nos(arquivo: Path) -> dict[str, ET.Element]:
    """Carrega do nav2_tree_nodes.xml as definições de nós e suas portas."""
    validar_arquivo_xml(arquivo)

    raiz_nos = ET.parse(arquivo).getroot()
    definicoes: dict[str, ET.Element] = {}

    for modelo in raiz_nos:
        for no in modelo:
            id_no = no.attrib.get("ID")
            if id_no:
                definicoes[id_no] = no

    return definicoes


def calcular_parametrizacao(
    raiz_bt: ET.Element,
    definicoes: dict[str, ET.Element],
) -> dict[str, float | int]:
    """
    Calcula utilização de inputs e a adaptabilidade f2.

    Para cada ocorrência de nó da BT, são consideradas como entradas disponíveis as
    input_port declaradas para aquele tipo em nav2_tree_nodes.xml. Um input utilizado é
    classificado como dinâmico quando seu valor possui a forma exata "{variavel}";
    caso contrário, é classificado como literal.
    """
    total_disponiveis = 0
    total_usados = 0
    total_dinamicos = 0
    total_literais = 0

    for no_bt in raiz_bt.iter():
        definicao = definicoes.get(no_bt.tag)
        if definicao is None:
            continue

        inputs_disponiveis = {
            porta.attrib["name"]
            for porta in definicao
            if porta.tag == "input_port" and "name" in porta.attrib
        }

        if not inputs_disponiveis:
            continue

        inputs_usados = set(no_bt.attrib) & inputs_disponiveis

        for nome_input in inputs_usados:
            valor = no_bt.attrib[nome_input]
            if valor.startswith("{") and valor.endswith("}"):
                total_dinamicos += 1
            else:
                total_literais += 1

        total_disponiveis += len(inputs_disponiveis)
        total_usados += len(inputs_usados)

    if total_disponiveis > 0:
        grau_parametrizacao = total_usados / total_disponiveis
        adaptabilidade = total_dinamicos / total_disponiveis
    else:
        grau_parametrizacao = 0.0
        adaptabilidade = 0.0

    return {
        "inputs_disponiveis": total_disponiveis,
        "inputs_usados": total_usados,
        "inputs_dinamicos": total_dinamicos,
        "inputs_literais": total_literais,
        "grau_parametrizacao": grau_parametrizacao,
        "adaptabilidade": adaptabilidade,
    }


# =============================================================================
# ANÁLISE DE UMA BEHAVIOR TREE
# =============================================================================

def analisar_bt(
    nome: str,
    raiz_bt: ET.Element,
    definicoes: dict[str, ET.Element],
) -> dict[str, float | int | str]:
    """Extrai todos os atributos e métricas usados no experimento Nav2."""
    profundidade = calcular_profundidade_bt(raiz_bt)
    ramificacao = calcular_ramificacao_maxima(raiz_bt)
    total_nos = contar_nos_bt(raiz_bt)
    condicoes_compostas = contar_condicoes_compostas(raiz_bt)
    subtrees = contar_subtrees(raiz_bt)
    nos_controle = contar_nos_controle(raiz_bt)

    modulos_totais, modulos_reutilizaveis, modularidade = calcular_modularidade(raiz_bt)

    caminhos_decisao = contar_caminhos_decisao(raiz_bt)
    rastreabilidade = 1 / (1 + caminhos_decisao)
    simplicidade = 1 / (1 + 0.5 * profundidade + 0.5 * ramificacao)
    clareza_logica = 1 / (1 + condicoes_compostas)

    explicabilidades = calcular_explicabilidade(
        simplicidade,
        rastreabilidade,
        modularidade,
        clareza_logica,
    )

    parametrizacao = calcular_parametrizacao(raiz_bt, definicoes)

    return {
        "nome": nome,
        "profundidade": profundidade,
        "ramificacao": ramificacao,
        "total_nos": total_nos,
        "condicoes_compostas": condicoes_compostas,
        "subtrees": subtrees,
        "nos_controle": nos_controle,
        "caminhos_decisao": caminhos_decisao,
        "rastreabilidade": rastreabilidade,
        "simplicidade": simplicidade,
        "clareza_logica": clareza_logica,
        "explicabilidade_tempo_real": explicabilidades["Tempo Real"],
        "explicabilidade_equipe_iniciante": explicabilidades["Equipe Iniciante"],
        "explicabilidade_ambiente_dinamico": explicabilidades["Ambiente Dinamico"],
        "modulos_totais": modulos_totais,
        "modulos_reutilizaveis": modulos_reutilizaveis,
        "modularidade": modularidade,
        **parametrizacao,
    }


# =============================================================================
# SAÍDA
# =============================================================================

def imprimir_resultado(resultado: dict[str, float | int | str]) -> None:
    """Imprime um resumo legível no terminal."""
    print(f'\nBT: {resultado["nome"]}')
    print(f'Profundidade: {resultado["profundidade"]}')
    print(f'Ramificação máxima: {resultado["ramificacao"]}')
    print(f'Total de nós: {resultado["total_nos"]}')
    print(f'Condições compostas: {resultado["condicoes_compostas"]}')
    print(f'SubTrees: {resultado["subtrees"]}')
    print(f'Nós de controle: {resultado["nos_controle"]}')
    print(f'Caminhos de decisão: {resultado["caminhos_decisao"]}')
    print(f'Rastreabilidade: {resultado["rastreabilidade"]:.3f}')
    print(f'Simplicidade: {resultado["simplicidade"]:.3f}')
    print(f'Clareza lógica: {resultado["clareza_logica"]:.3f}')
    print(f'Explicabilidade - Tempo Real: {resultado["explicabilidade_tempo_real"]:.3f}')
    print(
        'Explicabilidade - Equipe Iniciante: '
        f'{resultado["explicabilidade_equipe_iniciante"]:.3f}'
    )
    print(
        'Explicabilidade - Ambiente Dinâmico: '
        f'{resultado["explicabilidade_ambiente_dinamico"]:.3f}'
    )
    print(f'Módulos totais: {resultado["modulos_totais"]}')
    print(f'Módulos reutilizáveis: {resultado["modulos_reutilizaveis"]}')
    print(f'Modularidade: {resultado["modularidade"]:.3f}')
    print(f'Inputs disponíveis: {resultado["inputs_disponiveis"]}')
    print(f'Inputs explicitamente usados: {resultado["inputs_usados"]}')
    print(f'Inputs dinâmicos: {resultado["inputs_dinamicos"]}')
    print(f'Inputs literais: {resultado["inputs_literais"]}')
    print(f'Grau de parametrização explícita: {resultado["grau_parametrizacao"]:.3f}')
    print(f'Adaptabilidade: {resultado["adaptabilidade"]:.3f}')


def salvar_relatorio_individual(
    resultado: dict[str, float | int | str],
    arquivo_xml: Path,
    pasta_saida: Path,
) -> Path:
    """Salva um TXT com as métricas de uma BT."""
    texto = f"""
BT: {resultado["nome"]}

Fonte: ROS 2 Navigation2 (Nav2)
Repositório: ros-navigation/navigation2
Caminho: nav2_bt_navigator/behavior_trees/{arquivo_xml.name}
Tipo: Behavior Tree real de navegação

Profundidade: {resultado["profundidade"]}
Ramificação máxima: {resultado["ramificacao"]}
Total de nós: {resultado["total_nos"]}
Condições compostas: {resultado["condicoes_compostas"]}
SubTrees: {resultado["subtrees"]}
Nós de controle: {resultado["nos_controle"]}
Caminhos de decisão: {resultado["caminhos_decisao"]}
Rastreabilidade: {resultado["rastreabilidade"]:.3f}
Simplicidade: {resultado["simplicidade"]:.3f}
Clareza lógica: {resultado["clareza_logica"]:.3f}
Explicabilidade - Tempo Real: {resultado["explicabilidade_tempo_real"]:.3f}
Explicabilidade - Equipe Iniciante: {resultado["explicabilidade_equipe_iniciante"]:.3f}
Explicabilidade - Ambiente Dinâmico: {resultado["explicabilidade_ambiente_dinamico"]:.3f}
Módulos totais: {resultado["modulos_totais"]}
Módulos reutilizáveis: {resultado["modulos_reutilizaveis"]}
Modularidade: {resultado["modularidade"]:.3f}

Inputs disponíveis: {resultado["inputs_disponiveis"]}
Inputs explicitamente usados: {resultado["inputs_usados"]}
Inputs dinâmicos: {resultado["inputs_dinamicos"]}
Inputs literais: {resultado["inputs_literais"]}
Grau de parametrização explícita: {resultado["grau_parametrizacao"]:.3f}
Adaptabilidade: {resultado["adaptabilidade"]:.3f}
""".strip()

    pasta_saida.mkdir(parents=True, exist_ok=True)
    arquivo_saida = pasta_saida / f'resultado_{resultado["nome"]}.txt'
    arquivo_saida.write_text(texto + "\n", encoding="utf-8")
    return arquivo_saida


def salvar_csv(
    resultados: list[dict[str, float | int | str]],
    pasta_saida: Path,
) -> Path:
    """Salva todas as métricas em um CSV consolidado."""
    pasta_saida.mkdir(parents=True, exist_ok=True)
    arquivo_csv = pasta_saida / "resultados_nav2.csv"

    campos = [
        "nome",
        "profundidade",
        "ramificacao",
        "total_nos",
        "condicoes_compostas",
        "subtrees",
        "nos_controle",
        "caminhos_decisao",
        "rastreabilidade",
        "simplicidade",
        "clareza_logica",
        "explicabilidade_tempo_real",
        "explicabilidade_equipe_iniciante",
        "explicabilidade_ambiente_dinamico",
        "inputs_disponiveis",
        "inputs_usados",
        "grau_parametrizacao",
        "adaptabilidade",
        "modulos_totais",
        "modulos_reutilizaveis",
        "modularidade",
        "inputs_dinamicos",
        "inputs_literais",
    ]

    with arquivo_csv.open("w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(resultados)

    return arquivo_csv


# =============================================================================
# EXECUÇÃO DO EXPERIMENTO
# =============================================================================

def analisar_conjunto(pasta_dados: Path, pasta_saida: Path) -> list[dict[str, float | int | str]]:
    """Executa o experimento sobre todos os XMLs de BT presentes em pasta_dados."""
    arquivo_modelo_nos = pasta_dados / "nav2_tree_nodes.xml"
    validar_arquivo_xml(arquivo_modelo_nos)

    definicoes = carregar_definicoes_nos(arquivo_modelo_nos)

    arquivos_bt = sorted(
        arquivo
        for arquivo in pasta_dados.glob("*.xml")
        if arquivo.name != arquivo_modelo_nos.name
    )

    if not arquivos_bt:
        raise FileNotFoundError(
            f"Nenhuma Behavior Tree XML encontrada em: {pasta_dados}"
        )

    print(f"{len(arquivos_bt)} Behavior Tree(s) encontrada(s).")

    resultados: list[dict[str, float | int | str]] = []

    for arquivo_bt in arquivos_bt:
        raiz = ET.parse(arquivo_bt).getroot()
        resultado = analisar_bt(arquivo_bt.stem, raiz, definicoes)
        resultados.append(resultado)

        imprimir_resultado(resultado)
        arquivo_saida = salvar_relatorio_individual(
            resultado,
            arquivo_bt,
            pasta_saida,
        )
        print("Resultado salvo em:", arquivo_saida)

    arquivo_csv = salvar_csv(resultados, pasta_saida)
    print("\nCSV geral salvo em:", arquivo_csv)
    print("\n--- RESUMO ---")
    print(f"Total de BTs analisadas: {len(resultados)}")

    return resultados


def criar_parser() -> argparse.ArgumentParser:
    """Cria os argumentos de linha de comando, mantendo defaults do repositório."""
    raiz_repositorio = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser(
        description="Extrai métricas estáticas de Behavior Trees reais do Nav2."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=raiz_repositorio / "data" / "nav2",
        help="Pasta com os XMLs das BTs e nav2_tree_nodes.xml.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=raiz_repositorio / "results" / "nav2",
        help="Pasta onde os resultados serão gravados.",
    )
    return parser


def main() -> None:
    validar_pesos()
    args = criar_parser().parse_args()
    analisar_conjunto(args.data_dir, args.output_dir)


if __name__ == "__main__":
    main()
