import re

from processamento.discurso import Discurso


ABREVIACOES = {
    "Sr.": "Sr<prd>",
    "Sra.": "Sra<prd>",
    "Srs.": "Srs<prd>",
    "Sras.": "Sras<prd>",
    "V.Exa.": "V<prd>Exa<prd>",
    "V.Exas.": "V<prd>Exas<prd>",
}

_PADROES_CABECALHO = [
    re.compile(r"^Sessão de:"),
    re.compile(r"^Notas Taquigráficas$"),
    re.compile(r"^CÂMARA DOS DEPUTADOS$"),
    re.compile(r"^DEPARTAMENTO DE REGISTRO OFICIAL"),
    re.compile(r"^\d+/\d+$"),
]


def limparRuidoEstrutural(texto):
    linhasLimpas = []

    for linha in texto.splitlines():
        linha = re.sub(r"\([^)]*\bPausa\.\)", "", linha)
        linha = linha.strip()

        if not linha:
            continue

        if _ehCabecalhoOuPaginacao(linha):
            continue

        if _ehTituloCaixaAlta(linha):
            continue

        if re.fullmatch(r"\([^)]*\.\)", linha):
            continue

        linhasLimpas.append(linha)

    return "\n".join(linhasLimpas)


def extrairDiscursosDeTexto(texto):
    textoLimpo = limparRuidoEstrutural(texto)
    padraoOrador = re.compile(r"(?m)^(?:O SR\.|A SRA\.)\s+([^\n]*?\([^)]*\)|[^-\n]+)\s+-\s+")
    ocorrencias = list(padraoOrador.finditer(textoLimpo))
    discursos = []

    for indice, ocorrencia in enumerate(ocorrencias):
        inicioFala = ocorrencia.end()
        fimFala = ocorrencias[indice + 1].start() if indice + 1 < len(ocorrencias) else len(textoLimpo)
        orador = _normalizarEspacos(ocorrencia.group(1))
        fala = _normalizarEspacos(textoLimpo[inicioFala:fimFala])

        for frase in dividirFrases(fala):
            discursos.append(Discurso(orador=orador, frase=frase))

    return discursos


def dividirFrases(texto):
    texto = _normalizarEspacos(texto)
    if not texto:
        return []

    protegido = texto
    for abreviacao, substituto in ABREVIACOES.items():
        protegido = protegido.replace(abreviacao, substituto)

    partes = re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9\"“])", protegido)
    frases = []

    for parte in partes:
        frase = parte.replace("<prd>", ".").strip()
        frase = frase.strip(" -")
        if frase:
            frases.append(frase)

    return frases


def _normalizarEspacos(texto):
    return re.sub(r"\s+", " ", texto).strip()


def _ehCabecalhoOuPaginacao(linha):
    return any(padrao.search(linha) for padrao in _PADROES_CABECALHO)


def _ehTituloCaixaAlta(linha):
    if linha.startswith(("O SR.", "A SRA.")):
        return False

    letras = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ]", "", linha)
    if len(letras) < 3:
        return False

    return linha == linha.upper()
