class FilaPrioridadeMaxima:
    def __init__(self):
        self.itens = []

    @property
    def quantidade(self):
        return len(self.itens)

    def estaVazia(self):
        return not self.itens

    def inserir(self, item):
        self.itens.append(item)
        self._subir(len(self.itens) - 1)

    def extrairMaximo(self):
        if self.estaVazia():
            return None

        itemMaximo = self.itens[0]
        ultimoItem = self.itens.pop()

        if self.itens:
            self.itens[0] = ultimoItem
            self._descer(0)

        return itemMaximo

    def _subir(self, indice):
        while indice > 0:
            indicePai = (indice - 1) // 2

            if self._temMaiorPrioridade(self.itens[indicePai], self.itens[indice]):
                return

            self.itens[indicePai], self.itens[indice] = (
                self.itens[indice],
                self.itens[indicePai],
            )
            indice = indicePai

    def _descer(self, indice):
        while True:
            indiceEsquerda = 2 * indice + 1
            indiceDireita = 2 * indice + 2
            indiceMaior = indice

            if (
                indiceEsquerda < self.quantidade
                and self._temMaiorPrioridade(self.itens[indiceEsquerda], self.itens[indiceMaior])
            ):
                indiceMaior = indiceEsquerda

            if (
                indiceDireita < self.quantidade
                and self._temMaiorPrioridade(self.itens[indiceDireita], self.itens[indiceMaior])
            ):
                indiceMaior = indiceDireita

            if indiceMaior == indice:
                return

            self.itens[indice], self.itens[indiceMaior] = (
                self.itens[indiceMaior],
                self.itens[indice],
            )
            indice = indiceMaior

    @staticmethod
    def _temMaiorPrioridade(itemA, itemB):
        if itemA.relevancia != itemB.relevancia:
            return itemA.relevancia > itemB.relevancia

        return itemA.indiceOriginal < itemB.indiceOriginal
