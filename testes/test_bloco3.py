import json
import tempfile
import unittest
from pathlib import Path

from estruturas.grafoMatriz import adicionarAresta, criarGrafo
from processamento.centralidadeGrau import processarBloco3, salvarResultadoBloco3


class TestCentralidadeGrau(unittest.TestCase):
    def testProcessaBloco3SomandoPesosDeCadaLinha(self):
        grafo = criarGrafo(4)
        adicionarAresta(grafo, 0, 1, 0.5)
        adicionarAresta(grafo, 0, 2, 0.25)
        adicionarAresta(grafo, 1, 2, 0.75)

        resultado = processarBloco3(grafo)

        self.assertEqual(resultado.pontuacoes, [0.75, 1.25, 1.0, 0.0])

    def testSalvaPontuacoesCentralidadeEmJson(self):
        grafo = criarGrafo(2)
        adicionarAresta(grafo, 0, 1, 0.5)
        resultado = processarBloco3(grafo)

        with tempfile.TemporaryDirectory() as diretorioTemporario:
            salvarResultadoBloco3(resultado, Path(diretorioTemporario))
            caminhoSaida = Path(diretorioTemporario) / "pontuacoesCentralidade.json"
            pontuacoes = json.loads(caminhoSaida.read_text(encoding="utf-8"))

        self.assertEqual(pontuacoes, [0.5, 0.5])


if __name__ == "__main__":
    unittest.main()
