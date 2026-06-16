import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from estruturas.grafoMatriz import (
    adicionarAresta,
    criarGrafo,
    existeAresta,
    grauMatriz,
    imprimirGrafo,
    liberarGrafo,
)
from processamento.discurso import DiscursoProcessado
from processamento.modelagemGrafo import (
    calcularIndiceJaccard,
    processarBloco2,
    salvarDiscursosGrafo,
    salvarResultadoBloco2,
)


class TestGrafoMatriz(unittest.TestCase):
    def testAdicionaArestaSimetricaCalculaGrauEImprime(self):
        grafo = criarGrafo(3)

        adicionarAresta(grafo, 0, 1, 0.5)
        adicionarAresta(grafo, 1, 2, 0.25)

        self.assertTrue(existeAresta(grafo, 0, 1))
        self.assertTrue(existeAresta(grafo, 1, 0))
        self.assertFalse(existeAresta(grafo, 0, 2))
        self.assertEqual(grauMatriz(grafo, 1), 2)
        self.assertEqual(grafo.matrizAdjacencia[0][1], 0.5)
        self.assertEqual(grafo.matrizAdjacencia[1][0], 0.5)

        saida = io.StringIO()
        with redirect_stdout(saida):
            imprimirGrafo(grafo)

        self.assertIn("0.50", saida.getvalue())

        liberarGrafo(grafo)

        self.assertEqual(grafo.quantidadeVertices, 0)
        self.assertEqual(grafo.matrizAdjacencia, [])


class TestModelagemGrafo(unittest.TestCase):
    def testCalculaIndiceJaccardComOperacoesBitset(self):
        self.assertEqual(calcularIndiceJaccard(0b1011, 0b0110), 0.25)
        self.assertEqual(calcularIndiceJaccard(0, 0), 0.0)

    def testProcessaBloco2CriandoMatrizDensaSimetrica(self):
        discursos = [
            DiscursoProcessado(orador="A", frase="frase 1", tokens=[0, 1], bitset=0b0011),
            DiscursoProcessado(orador="Ignorado", frase="sim", tokens=[], bitset=0),
            DiscursoProcessado(orador="B", frase="frase 2", tokens=[1, 2], bitset=0b0110),
            DiscursoProcessado(orador="C", frase="frase 3", tokens=[3], bitset=0b1000),
        ]

        resultado = processarBloco2(discursos)

        self.assertEqual(resultado.grafo.quantidadeVertices, 3)
        self.assertEqual([discurso.frase for discurso in resultado.discursos], ["frase 1", "frase 2", "frase 3"])
        self.assertEqual(resultado.grafo.matrizAdjacencia[0][0], 0.0)
        self.assertAlmostEqual(resultado.grafo.matrizAdjacencia[0][1], 1 / 3)
        self.assertAlmostEqual(resultado.grafo.matrizAdjacencia[1][0], 1 / 3)
        self.assertEqual(resultado.grafo.matrizAdjacencia[0][2], 0.0)
        self.assertFalse(existeAresta(resultado.grafo, 0, 2))

    def testSalvaMatrizAdjacenciaComoLinhasDeMatriz(self):
        discursos = [
            DiscursoProcessado(orador="A", frase="frase 1", tokens=[0], bitset=0b01),
            DiscursoProcessado(orador="B", frase="frase 2", tokens=[0, 1], bitset=0b11),
        ]
        resultado = processarBloco2(discursos)

        with tempfile.TemporaryDirectory() as diretorioTemporario:
            salvarResultadoBloco2(resultado, Path(diretorioTemporario))
            conteudo = (Path(diretorioTemporario) / "matrizAdjacencia.json").read_text(encoding="utf-8")

        linhas = conteudo.splitlines()

        self.assertEqual(linhas[0], "[")
        self.assertEqual(linhas[1], "  [0.0, 0.5],")
        self.assertEqual(linhas[2], "  [0.5, 0.0]")
        self.assertEqual(linhas[3], "]")

    def testSalvaDiscursosValidosComIndiceOriginal(self):
        discursos = [
            DiscursoProcessado(orador="A", frase="frase 1", tokens=[0], bitset=0b001),
            DiscursoProcessado(orador="Ignorado", frase="sim", tokens=[], bitset=0),
            DiscursoProcessado(orador="B", frase="frase 2", tokens=[1], bitset=0b010),
        ]
        resultado = processarBloco2(discursos)

        with tempfile.TemporaryDirectory() as diretorioTemporario:
            salvarDiscursosGrafo(resultado, Path(diretorioTemporario))
            caminhoSaida = Path(diretorioTemporario) / "grafoDiscursos.json"
            dados = json.loads(caminhoSaida.read_text(encoding="utf-8"))

        self.assertEqual(len(dados), resultado.grafo.quantidadeVertices)
        self.assertEqual([item["indiceOriginal"] for item in dados], [0, 2])
        self.assertEqual([item["frase"] for item in dados], ["frase 1", "frase 2"])
        self.assertEqual(dados[0]["bitset"], "0b1")


if __name__ == "__main__":
    unittest.main()
