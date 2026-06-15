import re
import unicodedata
import spacy

from processamento.regras import VERBOS_IRREGULARES, _REGRAS_VERBAIS

modeloPln = None


def carregarModeloPln():
    global modeloPln
    if modeloPln is None:
        modeloPln = spacy.load("pt_core_news_md", disable=["ner"])
    return modeloPln


def normalizarFrase(frase, modelo=None):
    modelo = modelo or carregarModeloPln()
    return _extrairTokens(modelo(frase))


def normalizarFrasesEmLote(frases, modelo=None):
    modelo = modelo or carregarModeloPln()
    return [_extrairTokens(doc) for doc in modelo.pipe(frases)]


def _extrairTokens(documento):
    tokens = []
    for token in documento:
        if token.is_space or token.is_punct or token.is_stop or token.like_num:
            continue
        termo = _normalizarParaFormaCanonica(token)
        if termo and termo.isalpha():
            tokens.append((termo, token.text))
    return tokens


def _normalizarParaFormaCanonica(token):
    lemma = token.lemma_ or token.text
    pos   = token.pos_

    if pos in ("VERB", "AUX"):
        chave = normalizarTermo(token.text)
        if chave in VERBOS_IRREGULARES:
            return VERBOS_IRREGULARES[chave]

        forma = normalizarTermo(lemma)
        if forma != normalizarTermo(token.text) and re.search(r"[aei]r$", forma):
            return forma

        inferido = _inferirInfinitivo(chave)
        if inferido:
            return inferido

        return forma

    return normalizarTermo(lemma)


def _inferirInfinitivo(forma):
    """Tenta converter uma forma conjugada para o infinitivo via sufixos."""
    for padrao, sufixo in _REGRAS_VERBAIS:
        match = re.search(padrao, forma)
        if match:
            radical = forma[: match.start()]
            if len(radical) >= 2:
                return radical + sufixo
    return None


def normalizarTermo(termo):
    termo = termo.lower().strip()
    termo = unicodedata.normalize("NFKD", termo)
    return "".join(c for c in termo if not unicodedata.combining(c))