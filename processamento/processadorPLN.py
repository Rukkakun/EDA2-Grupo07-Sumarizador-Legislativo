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
    return _extrairTokens(documento)


def normalizarFrasesEmLote(frases, modelo=None):
    modelo = modelo or carregarModeloPln()
    resultados = []

    for documento in modelo.pipe(frases):
        resultados.append(_extrairTokens(documento))

    return resultados


def _extrairTokens(documento):
    tokens = []

    for token in documento:
        # is_space: descarta espaços, tabs e quebras de linha
        # is_punct: descarta pontuação
        # is_stop: descarta stopwords 
        # like_num: descarta tokens numéricos
        if token.is_space or token.is_punct or token.is_stop or token.like_num:
            continue
            
        termo = normalizarTermo(token.lemma_ or token.text)

        if termo and termo.isalpha():
            tokens.append(termo)

    return tokens


def normalizarTermo(termo):
    termo = termo.lower().strip()
    termo = unicodedata.normalize("NFKD", termo)
    termo = "".join(caractere for caractere in termo if not unicodedata.combining(caractere))
    return termo
