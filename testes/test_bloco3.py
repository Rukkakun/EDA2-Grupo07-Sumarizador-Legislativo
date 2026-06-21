import unittest

from estruturas.grafoMatriz import adicionarAresta, criarGrafo
from processamento.centralidadeGrau import calcularCentralidadeGrau
from processamento.discurso import DiscursoProcessado


class TestCentralidadeGrau(unittest.TestCase):
    def _criarDiscursos(self, quantidade):
        return [
            DiscursoProcessado(orador=f"Orador {i}", frase=f"Frase {i}")
            for i in range(quantidade)
        ]

    def testProcessaBloco3AtribuiRelevanciaAosDiscursos(self):
        grafo = criarGrafo(4)
        adicionarAresta(grafo, 0, 1, 0.5)
        adicionarAresta(grafo, 0, 2, 0.25)
        adicionarAresta(grafo, 1, 2, 0.75)
        discursos = self._criarDiscursos(4)

        calcularCentralidadeGrau(grafo, discursos)

        relevancias = [discurso.relevancia for discurso in discursos]
        self.assertEqual(relevancias, [0.75, 1.25, 1.0, 0.0])


if __name__ == "__main__":
    unittest.main()
