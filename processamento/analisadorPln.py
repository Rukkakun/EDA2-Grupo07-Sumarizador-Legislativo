import unicodedata

import spacy


modeloPln = None


def carregarModeloPln():
    global modeloPln

    if modeloPln is None:
        modeloPln = spacy.load("pt_core_news_sm", disable=["ner"])

    return modeloPln


def normalizarFrase(frase, modelo=None):
    modelo = modelo or carregarModeloPln()
    documento = modelo(frase)
    tokens = []

    for token in documento:
        if token.is_space or token.is_punct or token.is_stop or token.like_num:
            continue

        termo = token.lemma_ if token.lemma_ else token.text
        termo = normalizarTermo(termo)

        if termo and termo.isalpha():
            tokens.append(termo)

    return tokens


def normalizarTermo(termo):
    termo = termo.lower().strip()
    termo = unicodedata.normalize("NFKD", termo)
    termo = "".join(caractere for caractere in termo if not unicodedata.combining(caractere))
    return termo
