import json
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import fitz

from estruturas.filaPrioridade import FilaPrioridadeMaxima


PERCENTUAL_RESUMO = 0.08
MINIMO_FRASES_RESUMO = 12
MAXIMO_FRASES_RESUMO = 60
LIMIAR_REDUNDANCIA = 0.7


@dataclass
class ResultadoResumo:
    quantidadePlanejada: int
    discursos: list


def calcularQuantidadeResumo(quantidadeDiscursosValidos):
    if quantidadeDiscursosValidos == 0:
        return 0

    quantidadeBase = math.ceil(PERCENTUAL_RESUMO * quantidadeDiscursosValidos)
    quantidadeLimitada = max(MINIMO_FRASES_RESUMO, quantidadeBase)
    quantidadeLimitada = min(MAXIMO_FRASES_RESUMO, quantidadeLimitada)
    return min(quantidadeDiscursosValidos, quantidadeLimitada)


def selecionarDiscursosResumo(discursos):
    quantidadePlanejada = calcularQuantidadeResumo(len(discursos))
    filaPrioridade = FilaPrioridadeMaxima()

    for discurso in discursos:
        filaPrioridade.inserir(discurso)

    bitsetResumo = 0
    discursosSelecionados = []

    while len(discursosSelecionados) < quantidadePlanejada and not filaPrioridade.estaVazia():
        candidato = filaPrioridade.extrairMaximo()

        if _coberturaDoResumo(candidato.bitset, bitsetResumo) >= LIMIAR_REDUNDANCIA:
            continue

        discursosSelecionados.append(candidato)
        bitsetResumo |= candidato.bitset

    discursosSelecionados.sort(key=lambda discurso: discurso.indiceOriginal)
    return ResultadoResumo(
        quantidadePlanejada=quantidadePlanejada,
        discursos=discursosSelecionados,
    )


def salvarResumoJson(resultado, caminhoSaida, nomeDocumento, quantidadeFrasesAnalisadas):
    caminhoSaida = Path(caminhoSaida)
    caminhoSaida.parent.mkdir(parents=True, exist_ok=True)
    dados = {
        "documento": nomeDocumento,
        "frasesAnalisadas": quantidadeFrasesAnalisadas,
        "frasesSelecionadas": len(resultado.discursos),
        "quantidadePlanejada": resultado.quantidadePlanejada,
        "discursos": [
            {
                "indiceOriginal": discurso.indiceOriginal,
                "orador": discurso.orador,
                "frase": discurso.frase,
                "relevancia": discurso.relevancia,
            }
            for discurso in resultado.discursos
        ],
    }
    caminhoSaida.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def gerarResumoPdf(resultado, caminhoSaida, nomeDocumento, quantidadeFrasesAnalisadas):
    caminhoSaida = Path(caminhoSaida)
    caminhoSaida.parent.mkdir(parents=True, exist_ok=True)
    documento = fitz.open()
    pagina, posicaoVertical = _criarPagina(documento)

    posicaoVertical = _inserirCabecalho(
        pagina,
        posicaoVertical,
        nomeDocumento,
        quantidadeFrasesAnalisadas,
        len(resultado.discursos),
    )

    numeroBloco = 1
    for grupo in _agruparDiscursosConsecutivos(resultado.discursos):
        pagina, posicaoVertical = _inserirGrupoDiscurso(
            documento,
            pagina,
            posicaoVertical,
            numeroBloco,
            grupo,
        )
        numeroBloco += 1

    for indicePagina, paginaAtual in enumerate(documento, start=1):
        paginaAtual.insert_text(
            (50, 805),
            f"Pagina {indicePagina}",
            fontname="helv",
            fontsize=8,
            color=(0.35, 0.35, 0.35),
        )

    documento.set_metadata(
        {
            "title": "Resumo Extrativo do Debate Legislativo",
            "author": "Sumarizador Legislativo",
        }
    )
    documento.save(caminhoSaida)
    documento.close()


def _coberturaDoResumo(bitsetCandidato, bitsetResumo):
    quantidadeTermosCandidato = bitsetCandidato.bit_count()

    if quantidadeTermosCandidato == 0:
        return 1.0

    return (bitsetCandidato & bitsetResumo).bit_count() / quantidadeTermosCandidato


def _agruparDiscursosConsecutivos(discursos):
    grupos = []

    for discurso in discursos:
        if (
            grupos
            and grupos[-1][-1].orador == discurso.orador
            and grupos[-1][-1].indiceOriginal + 1 == discurso.indiceOriginal
        ):
            grupos[-1].append(discurso)
        else:
            grupos.append([discurso])

    return grupos


def _criarPagina(documento):
    return documento.new_page(width=595, height=842), 55


def _inserirCabecalho(
    pagina,
    posicaoVertical,
    nomeDocumento,
    quantidadeFrasesAnalisadas,
    quantidadeFrasesSelecionadas,
):
    pagina.insert_text(
        (50, posicaoVertical),
        "Resumo Extrativo do Debate Legislativo",
        fontname="hebo",
        fontsize=16,
        color=(0.1, 0.1, 0.1),
    )
    posicaoVertical += 30
    pagina.insert_text((50, posicaoVertical), f"Documento: {nomeDocumento}", fontname="helv", fontsize=10)
    posicaoVertical += 16
    pagina.insert_text(
        (50, posicaoVertical),
        f"Frases analisadas: {quantidadeFrasesAnalisadas}",
        fontname="helv",
        fontsize=10,
    )
    posicaoVertical += 16
    pagina.insert_text(
        (50, posicaoVertical),
        f"Frases selecionadas: {quantidadeFrasesSelecionadas}",
        fontname="helv",
        fontsize=10,
    )
    posicaoVertical += 16
    pagina.insert_text(
        (50, posicaoVertical),
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        fontname="helv",
        fontsize=10,
    )
    posicaoVertical += 22
    pagina.draw_line((50, posicaoVertical), (545, posicaoVertical), color=(0.65, 0.65, 0.65))
    return posicaoVertical + 25


def _inserirGrupoDiscurso(documento, pagina, posicaoVertical, numeroBloco, grupo):
    linhasOrador = _quebrarTexto(f"{numeroBloco}. {grupo[0].orador}", "hebo", 11, 495)
    linhasFrases = []

    for discurso in grupo:
        linhasFrases.extend(_quebrarTexto(f'"{discurso.frase}"', "helv", 10, 480))
        linhasFrases.append("")

    alturaNecessaria = len(linhasOrador) * 15 + len(linhasFrases) * 14 + 10
    if posicaoVertical + alturaNecessaria > 780:
        pagina, posicaoVertical = _criarPagina(documento)

    for linha in linhasOrador:
        pagina.insert_text((50, posicaoVertical), linha, fontname="hebo", fontsize=11)
        posicaoVertical += 15

    posicaoVertical += 3
    for linha in linhasFrases:
        if not linha:
            posicaoVertical += 5
            continue
        pagina.insert_text((62, posicaoVertical), linha, fontname="helv", fontsize=10)
        posicaoVertical += 14

    return pagina, posicaoVertical + 10


def _quebrarTexto(texto, fonte, tamanhoFonte, larguraMaxima):
    palavras = texto.split()
    linhas = []
    linhaAtual = ""

    for palavra in palavras:
        candidata = palavra if not linhaAtual else f"{linhaAtual} {palavra}"

        if fitz.get_text_length(candidata, fontname=fonte, fontsize=tamanhoFonte) <= larguraMaxima:
            linhaAtual = candidata
            continue

        if linhaAtual:
            linhas.append(linhaAtual)
        linhaAtual = palavra

    if linhaAtual:
        linhas.append(linhaAtual)

    return linhas
