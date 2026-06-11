import json
from dataclasses import dataclass
from pathlib import Path

from estruturas.tabelaHash import TabelaHash
from processamento.discurso import DiscursoProcessado
from processamento.extratorPDF import extrairTextoPdf
from processamento.limpezaEstrutural import extrairDiscursosDeTexto
from processamento.processadorPLN import normalizarFrase as normalizarFrasePadrao


@dataclass
class ResultadoBloco1:
    vocabulario: TabelaHash
    discursos: list[DiscursoProcessado]


def processarBloco1(discursos, normalizarFrase=None):
    normalizarFrase = normalizarFrase or normalizarFrasePadrao
    vocabulario = TabelaHash()
    tokensPorDiscurso = []

    for discurso in discursos:
        tokens = _removerDuplicatas(normalizarFrase(discurso.frase))
        idsTokens = []

        for token in tokens:
            idsTokens.append(vocabulario.obterId(token))

        tokensPorDiscurso.append(idsTokens)

    discursosProcessados = []

    for discurso, idsTokens in zip(discursos, tokensPorDiscurso):
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

    return ResultadoBloco1(vocabulario=vocabulario, discursos=discursosProcessados)


def processarPdfBloco1(caminhoPdf, normalizarFrase=None):
    texto = extrairTextoPdf(caminhoPdf)
    discursos = extrairDiscursosDeTexto(texto)
    return processarBloco1(discursos, normalizarFrase=normalizarFrase)


def salvarResultadoBloco1(resultado, caminhoSaida):
    caminhoSaida = Path(caminhoSaida)
    caminhoSaida.parent.mkdir(parents=True, exist_ok=True)
    dados = {
        "vocabulario": resultado.vocabulario.listarPalavras(),
        "discursos": [
            {
                "orador": discurso.orador,
                "frase": discurso.frase,
                "tokens": discurso.tokens,
                "bitset": discurso.bitset,
            }
            for discurso in resultado.discursos
        ],
    }
    caminhoSaida.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def _removerDuplicatas(tokens):
    vistos = []
    tokensUnicos = []

    for token in tokens:
        if token in vistos:
            continue
        vistos.append(token)
        tokensUnicos.append(token)

    return tokensUnicos


def main():
    caminhoEntrada = Path("dados/entrada/entrada1.pdf")
    caminhoSaida = Path("dados/saida/bloco1.json")
    resultado = processarPdfBloco1(caminhoEntrada)
    salvarResultadoBloco1(resultado, caminhoSaida)
    print(f"Discursos processados: {len(resultado.discursos)}")
    print(f"Vocabulário: {resultado.vocabulario.quantidade} termos")
    print(f"Saída: {caminhoSaida}")


if __name__ == "__main__":
    main()
