from dataclasses import dataclass


@dataclass
class EntradaHash:
    chave: str
    idPalavra: int


class TabelaHash:
    def __init__(self, tamanhoInicial=101):
        self.tamanho = self._proximoPrimo(tamanhoInicial)
        self.vetor = [None] * self.tamanho
        self.lapide = object()
        self.quantidade = 0
        self.palavrasPorId = []
        self.idsDisponiveis = []

    def obterId(self, chave):
        posicao = self._encontrarPosicao(chave)
        entrada = self.vetor[posicao]

        if isinstance(entrada, EntradaHash):
            return entrada.idPalavra

        if self.idsDisponiveis:
            idPalavra = self.idsDisponiveis.pop()
            self.palavrasPorId[idPalavra] = chave
        else:
            idPalavra = len(self.palavrasPorId)
            self.palavrasPorId.append(chave)

        self.vetor[posicao] = EntradaHash(chave, idPalavra)
        self.quantidade += 1

        if self.quantidade / self.tamanho > 0.7:
            self._redimensionar()

        return idPalavra

    def inserir(self, chave):
        return self.obterId(chave)

    def buscar(self, chave):
        posicaoInicial = self._hash1(chave)
        salto = self._hash2(chave)

        for tentativa in range(self.tamanho):
            posicao = (posicaoInicial + tentativa * salto) % self.tamanho
            entrada = self.vetor[posicao]

            if entrada is None:
                return None

            if entrada is self.lapide:
                continue

            if entrada.chave == chave:
                return entrada.idPalavra

        return None

    def remover(self, chave):
        posicaoInicial = self._hash1(chave)
        salto = self._hash2(chave)

        for tentativa in range(self.tamanho):
            posicao = (posicaoInicial + tentativa * salto) % self.tamanho
            entrada = self.vetor[posicao]

            if entrada is None:
                return False

            if entrada is self.lapide:
                continue

            if entrada.chave == chave:
                self.vetor[posicao] = self.lapide
                self.palavrasPorId[entrada.idPalavra] = None
                self.idsDisponiveis.append(entrada.idPalavra)
                self.quantidade -= 1
                return True

        return False

    def listarPalavras(self):
        return [palavra for palavra in self.palavrasPorId if palavra is not None]

    def _encontrarPosicao(self, chave):
        posicaoInicial = self._hash1(chave)
        salto = self._hash2(chave)
        primeiraLapide = None

        for tentativa in range(self.tamanho):
            posicao = (posicaoInicial + tentativa * salto) % self.tamanho
            entrada = self.vetor[posicao]

            if entrada is None:
                return primeiraLapide if primeiraLapide is not None else posicao

            if entrada is self.lapide:
                if primeiraLapide is None:
                    primeiraLapide = posicao
                continue

            if entrada.chave == chave:
                return posicao

        self._redimensionar()
        return self._encontrarPosicao(chave)

    def _redimensionar(self):
        entradasAntigas = [
            entrada for entrada in self.vetor if isinstance(entrada, EntradaHash)
        ]
        self.tamanho = self._proximoPrimo(self.tamanho * 2)
        self.vetor = [None] * self.tamanho
        self.quantidade = 0

        for entrada in entradasAntigas:
            posicao = self._encontrarPosicao(entrada.chave)
            self.vetor[posicao] = entrada
            self.quantidade += 1

    def _hash1(self, chave):
        return self._mapearStringParaInteiro(chave, self.tamanho)

    def _hash2(self, chave):
        return 1 + self._mapearStringParaInteiro(chave, self.tamanho - 2)

    @staticmethod
    def _mapearStringParaInteiro(chave, modulo):
        valor = 0
        for caractere in chave:
            valor = (valor * 256 + ord(caractere)) % modulo
        return valor

    @staticmethod
    def _ehPrimo(numero):
        if numero < 2:
            return False
        if numero == 2:
            return True
        if numero % 2 == 0:
            return False

        divisor = 3
        while divisor * divisor <= numero:
            if numero % divisor == 0:
                return False
            divisor += 2

        return True

    @classmethod
    def _proximoPrimo(cls, numero):
        candidato = max(2, numero)
        while not cls._ehPrimo(candidato):
            candidato += 1
        return candidato
