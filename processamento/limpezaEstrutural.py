import re
import unicodedata

from processamento.discurso import Discurso


ABREVIACOES = {
    "Sr.": "Sr<prd>",
    "Sra.": "Sra<prd>",
    "Srs.": "Srs<prd>",
    "Sras.": "Sras<prd>",
    "V.Exa.": "V<prd>Exa<prd>",
    "V.Exas.": "V<prd>Exas<prd>",
    "O.k.": "O<prd>k<prd>",
    "art.": "art<prd>",
}

_PADROES_CABECALHO = [
    re.compile(r"^(Sessão|Reunião) de:"),
    re.compile(r"^Notas Taquigráficas(?: - Comissões)?$"),
    re.compile(r"^CÂMARA DOS DEPUTADOS$"),
    re.compile(r"^DEPARTAMENTO DE REGISTRO OFICIAL"),
    re.compile(r"^Registro oficial sem redação final\.$"),
    re.compile(r"^\d+\s*/\s*\d+$"),
]

_PADROES_CHAMADA_DE_FALA = [
    re.compile(r"\b(?:conced\w*|pass\w*|cham\w*|dar\w*|ter\w*|estar\w*)\b.*\bpalavra\b"),
    re.compile(
        r"\b(?:orador|oradora|deputad[oa])\b.*\b(?:dispoe|tera|falar\w*)\b.*\b(?:tempo|minuto)\b"
    ),
]

_PADROES_CONTROLE_DE_SESSAO = [
    re.compile(r"\b(?:recuper\w*|acrescent\w*|recompor\w*|distribu\w*|ped\w*)\b.*\b(?:tempo|minuto)\b"),
    re.compile(r"\b(?:aguard\w*|complet\w*|organiza\w*|seguir\w*)\b.*\b(?:quorum|lista|inscrit\w*|ordem)\b"),
]

_PADROES_ANUNCIO_OPERACIONAL = [
    re.compile(r"\b(?:pronunciamento|fala)\b.*\b(?:divulg\w*|veicul\w*|registr\w*)\b"),
    re.compile(r"\b(?:divulg\w*|veicul\w*|registr\w*)\b.*\b(?:pronunciamento|fala)\b"),
]

_PADROES_CORTESIA = [
    re.compile(
        r"^\s*(?:(?:eu|nos|quero|queremos|gostaria)\s+)?(?:muito\s+)?(?:obrigad\w*|agradec\w*|cumpriment\w*|saud\w*|parabeniz\w*|felicit\w*)\b"
    ),
    re.compile(r"^\s*(?:seja\w*\s+)?bem[ -]?vind\w*\b"),
]

_PADRAO_RUBRICA_TAQUIGRAFICA = re.compile(
    r"\((?=[^)]*(?:"
    r"pausa|"
    r"intervenção|"
    r"intervencao|"
    r"microfone|"
    r"inaudível|"
    r"inaudivel|"
    r"ininteligível|"
    r"ininteligivel|"
    r"risos|"
    r"palmas|"
    r"manifestação|"
    r"manifestacao|"
    r"procede-se|"
    r"descerramento"
    r"))[^)]*\)",
    re.IGNORECASE,
)


def limparRuidoEstrutural(texto):
    linhasLimpas = []

    for linha in texto.splitlines():
        linha = linha.strip()

        if not linha:
            continue

        if re.match(r"^\(Não identificado\)\s+-\s+", linha):
            continue

        linha = _removerRubricasTaquigraficas(linha).strip()

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


def _removerRubricasTaquigraficas(linha):
    return _PADRAO_RUBRICA_TAQUIGRAFICA.sub("", linha)


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
            if _ehRuidoProcedimental(frase):
                continue
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


def _normalizarParaComparacao(frase):
    frase = unicodedata.normalize("NFKD", frase.lower())
    return "".join(caractere for caractere in frase if not unicodedata.combining(caractere))


def _ehRuidoProcedimental(frase):
    fraseNormalizada = _normalizarParaComparacao(frase)
    padroes = (
        _PADROES_CHAMADA_DE_FALA
        + _PADROES_CONTROLE_DE_SESSAO
        + _PADROES_ANUNCIO_OPERACIONAL
        + _PADROES_CORTESIA
    )
    return any(padrao.search(fraseNormalizada) for padrao in padroes)


def _ehCabecalhoOuPaginacao(linha):
    return any(padrao.search(linha) for padrao in _PADROES_CABECALHO)


def _ehTituloCaixaAlta(linha):
    if linha.startswith(("O SR.", "A SRA.")):
        return False

    letras = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ]", "", linha)
    if len(letras) < 3:
        return False

    return linha == linha.upper()
