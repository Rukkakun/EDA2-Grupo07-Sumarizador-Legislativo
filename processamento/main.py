import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from estruturas.tabelaHash import TabelaHash
from processamento.centralidadeGrau import calcularCentralidadeGrau
from processamento.discurso import DiscursoProcessado
from processamento.extratorPDF import extrairTextoPdf
from processamento.limpezaEstrutural import extrairDiscursosDeTexto
from processamento.modelagemGrafo import construirGrafoSimilaridade, salvarDiscursosGrafo, salvarMatrizAdjacencia
from processamento.processadorPLN import normalizarFrasesEmLote

DIRETORIO_ENTRADA_PADRAO = Path("dados/entrada")
DIRETORIO_SAIDA_PADRAO = Path("dados/saida")


@dataclass
class ResultadoTokenizacao:
    vocabulario: TabelaHash
    discursos: list[DiscursoProcessado]


def _removerDuplicatas(tokens):
    vistos = TabelaHash()
    tokensUnicos = []

    for item in tokens:
        if isinstance(item, tuple):
            chave, original = item
        else:
            chave, original = item, item

        if vistos.buscar(chave) is not None:
            continue
        vistos.inserir(chave, original)
        tokensUnicos.append((chave, original))

    return tokensUnicos


def tokenizarDiscursos(discursos, normalizarFrase=None):
    vocabulario = TabelaHash()
    tokensPorDiscurso = []

    if normalizarFrase is not None:
        for discurso in discursos:
            tokens = _removerDuplicatas(normalizarFrase(discurso.frase))
            tokensPorDiscurso.append(tokens)
    else:
        frases = [discurso.frase for discurso in discursos]
        todosTokens = normalizarFrasesEmLote(frases)
        for tokens in todosTokens:
            tokensPorDiscurso.append(_removerDuplicatas(tokens))

    discursosProcessados = []

    for discurso, tokens in zip(discursos, tokensPorDiscurso):
        idsTokens = [vocabulario.obterId(chave, original) for chave, original in tokens]
        bitset = 0

        for idPalavra in idsTokens:
            bitset |= 1 << idPalavra

        discursosProcessados.append(
            DiscursoProcessado(
                orador=discurso.orador,
                frase=discurso.frase,
                tokens=idsTokens,
                bitset=bitset,
            )
        )

    return ResultadoTokenizacao(vocabulario=vocabulario, discursos=discursosProcessados)


def tokenizarPdf(caminhoPdf, normalizarFrase=None):
    texto = extrairTextoPdf(caminhoPdf)
    discursos = extrairDiscursosDeTexto(texto)
    return tokenizarDiscursos(discursos, normalizarFrase=normalizarFrase)


def salvarResultadoTokenizacao(resultado, diretorioSaida):
    diretorioSaida = Path(diretorioSaida)
    diretorioSaida.mkdir(parents=True, exist_ok=True)

    caminhoVocabulario = diretorioSaida / "vocabulario.json"
    vocabulario = resultado.vocabulario.listarPalavras()
    caminhoVocabulario.write_text(
        json.dumps(vocabulario, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    caminhoDiscursos = diretorioSaida / "discursos.json"
    discursos = [
        {
            "orador": discurso.orador,
            "frase": discurso.frase,
            "tokens": discurso.tokens,
            "bitset": bin(discurso.bitset),
        }
        for discurso in resultado.discursos
    ]
    caminhoDiscursos.write_text(
        json.dumps(discursos, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def salvarVisualizacaoHash(tabela, caminhoArquivo):
    caminhoArquivo = Path(caminhoArquivo)
    caminhoArquivo.parent.mkdir(parents=True, exist_ok=True)
    linhas = []
    linhas.append(f"Tabela Hash — {tabela.quantidade} entradas / {tabela.tamanho} slots")
    linhas.append(f"Fator de carga: {tabela.quantidade / tabela.tamanho:.2%}")
    linhas.append("")
    linhas.append(f"{'Índice':<8} {'Status':<10} {'ID':<6} {'Ocorrências':<12} {'Chave':<20} {'Original'}")
    linhas.append("-" * 80)

    for indice, entrada in enumerate(tabela.vetor):
        if entrada is None:
            linhas.append(f"{indice:<8} {'vazio':<10} {'—':<6} {'—':<12} {'—':<20} {'—'}")
        elif entrada is tabela.lapide:
            linhas.append(f"{indice:<8} {'lápide':<10} {'—':<6} {'—':<12} {'—':<20} {'—'}")
        else:
            linhas.append(f"{indice:<8} {'ocupado':<10} {entrada.idPalavra:<6} {entrada.ocorrencias:<12} {entrada.chave:<20} {entrada.original}")

    caminhoArquivo.write_text("\n".join(linhas), encoding="utf-8")


def processarDocumento(caminhoPdf, diretorioSaida):
    """Executa o pipeline completo para um único documento PDF."""
    # Etapa 1: Tokenização e construção de vocabulário
    resultadoTokenizacao = tokenizarPdf(caminhoPdf)
    salvarResultadoTokenizacao(resultadoTokenizacao, diretorioSaida)
    salvarVisualizacaoHash(resultadoTokenizacao.vocabulario, diretorioSaida / "tabelaHash.txt")

    # Etapa 2: Modelagem do grafo de similaridade (Jaccard)
    resultadoGrafo = construirGrafoSimilaridade(resultadoTokenizacao.discursos)
    salvarMatrizAdjacencia(resultadoGrafo, diretorioSaida)

    # Etapa 3: Centralidade de grau e ranking de relevância
    calcularCentralidadeGrau(resultadoGrafo.grafo, resultadoGrafo.discursos)
    salvarDiscursosGrafo(resultadoGrafo, diretorioSaida)

    return resultadoTokenizacao, resultadoGrafo


def _resolverArquivosEntrada(caminhos):
    """Retorna a lista de PDFs: dos argumentos CLI ou por varredura do diretório padrão."""
    if caminhos:
        return [Path(caminho) for caminho in caminhos]

    if not DIRETORIO_ENTRADA_PADRAO.exists():
        print(f"Diretório '{DIRETORIO_ENTRADA_PADRAO}' não encontrado.")
        return []

    pdfs = sorted(DIRETORIO_ENTRADA_PADRAO.glob("*.pdf"))
    if not pdfs:
        print(f"Nenhum PDF encontrado em '{DIRETORIO_ENTRADA_PADRAO}'.")

    return pdfs


def main():
    parser = argparse.ArgumentParser(
        description="Sumarizador Legislativo — Pipeline de processamento de debates parlamentares."
    )
    parser.add_argument(
        "arquivos",
        nargs="*",
        help="Caminhos dos PDFs a processar. Se omitido, processa todos em dados/entrada/.",
    )
    args = parser.parse_args()

    arquivos = _resolverArquivosEntrada(args.arquivos)

    for caminhoPdf in arquivos:
        diretorioSaida = DIRETORIO_SAIDA_PADRAO / caminhoPdf.stem

        print(f"\n{'-' * 20}")
        print(f"Processando: {caminhoPdf.name}")
        print(f"{'-' * 20}")

        resultadoTokenizacao, resultadoGrafo = processarDocumento(caminhoPdf, diretorioSaida)

        grafo = resultadoGrafo.grafo
        print(f"Discursos processados: {len(resultadoTokenizacao.discursos)}")
        print(f"Matriz de adjacência: {grafo.quantidadeVertices} x {grafo.quantidadeVertices}")
        print(f"Vocabulário: {resultadoTokenizacao.vocabulario.quantidade} termos")
        print(f"Saída: {diretorioSaida}")


if __name__ == "__main__":
    main()

