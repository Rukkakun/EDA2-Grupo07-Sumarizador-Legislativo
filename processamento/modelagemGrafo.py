import json
from dataclasses import dataclass
from pathlib import Path

from estruturas.grafoMatriz import adicionarAresta, criarGrafo


@dataclass
class ResultadoBloco2:
    grafo: object
    discursos: list
    indicesOriginais: list[int]


def calcularIndiceJaccard(bitsetA, bitsetB):
    uniao = bitsetA | bitsetB

    if uniao == 0:
        return 0.0

    intersecao = bitsetA & bitsetB
    return intersecao.bit_count() / uniao.bit_count()


def processarBloco2(discursos):
    discursosValidos = []
    indicesOriginais = []

    for indiceOriginal, discurso in enumerate(discursos):
        if discurso.bitset == 0:
            continue
        discursosValidos.append(discurso)
        indicesOriginais.append(indiceOriginal)

    grafo = criarGrafo(len(discursosValidos))

    for indiceOrigem in range(len(discursosValidos)):
        for indiceDestino in range(indiceOrigem + 1, len(discursosValidos)):
            peso = calcularIndiceJaccard(
                discursosValidos[indiceOrigem].bitset,
                discursosValidos[indiceDestino].bitset,
            )

            if peso > 0.0:
                adicionarAresta(grafo, indiceOrigem, indiceDestino, peso)

    return ResultadoBloco2(
        grafo=grafo,
        discursos=discursosValidos,
        indicesOriginais=indicesOriginais,
    )


def salvarResultadoBloco2(resultado, diretorioSaida):
    diretorioSaida = Path(diretorioSaida)
    diretorioSaida.mkdir(parents=True, exist_ok=True)
    caminhoMatriz = diretorioSaida / "matrizAdjacencia.json"
    caminhoMatriz.write_text(
        _formatarMatrizComoJson(resultado.grafo.matrizAdjacencia),
        encoding="utf-8",
    )


def salvarDiscursosGrafo(resultado, diretorioSaida):
    diretorioSaida = Path(diretorioSaida)
    diretorioSaida.mkdir(parents=True, exist_ok=True)
    caminhoDiscursos = diretorioSaida / "grafoDiscursos.json"
    discursos = []

    for indiceGrafo, discurso in enumerate(resultado.discursos):
        discursos.append(
            {
                "indiceOriginal": resultado.indicesOriginais[indiceGrafo],
                "orador": discurso.orador,
                "frase": discurso.frase,
                "tokens": discurso.tokens,
                "bitset": bin(discurso.bitset),
            }
        )

    caminhoDiscursos.write_text(
        json.dumps(discursos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _formatarMatrizComoJson(matriz):
    linhas = ["["]

    for indice, linha in enumerate(matriz):
        separador = "," if indice < len(matriz) - 1 else ""
        linhas.append(f"  {json.dumps(linha, ensure_ascii=False)}{separador}")

    linhas.append("]")
    return "\n".join(linhas)
