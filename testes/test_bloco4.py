import json
import tempfile
import unittest
from pathlib import Path

import fitz

from estruturas.filaPrioridade import FilaPrioridadeMaxima
from processamento.discurso import DiscursoProcessado
from processamento.geradorResumo import (
    calcularQuantidadeResumo,
    gerarResumoPdf,
    selecionarDiscursosResumo,
    salvarResumoJson,
)


def criarDiscurso(indiceOriginal, relevancia, bitset, orador=None):
    return DiscursoProcessado(
        orador=orador or f"Orador {indiceOriginal}",
        frase=f"Frase {indiceOriginal}",
        bitset=bitset,
        indiceOriginal=indiceOriginal,
        relevancia=relevancia,
    )


class TestFilaPrioridadeMaxima(unittest.TestCase):
    def testExtraiMaiorRelevanciaEDesempataPeloIndiceOriginal(self):
        fila = FilaPrioridadeMaxima()
        fila.inserir(criarDiscurso(4, 2.0, 0b1))
        fila.inserir(criarDiscurso(2, 3.0, 0b10))
        fila.inserir(criarDiscurso(1, 3.0, 0b100))

        self.assertEqual(fila.extrairMaximo().indiceOriginal, 1)
        self.assertEqual(fila.extrairMaximo().indiceOriginal, 2)
        self.assertEqual(fila.extrairMaximo().indiceOriginal, 4)
        self.assertTrue(fila.estaVazia())


class TestGeradorResumo(unittest.TestCase):
    def testCalculaQuantidadeResumoComLimites(self):
        self.assertEqual(calcularQuantidadeResumo(0), 0)
        self.assertEqual(calcularQuantidadeResumo(10), 10)
        self.assertEqual(calcularQuantidadeResumo(200), 16)
        self.assertEqual(calcularQuantidadeResumo(1000), 60)

    def testFiltraRedundanciaEReordenaCronologicamente(self):
        discursos = [
            criarDiscurso(3, 10.0, 0b0011),
            criarDiscurso(0, 9.0, 0b0011),
            criarDiscurso(2, 8.0, 0b1100),
            criarDiscurso(1, 7.0, 0b0100),
        ]

        resultado = selecionarDiscursosResumo(discursos)

        self.assertEqual(resultado.quantidadePlanejada, 4)
        self.assertEqual(
            [discurso.indiceOriginal for discurso in resultado.discursos],
            [2, 3],
        )

    def testSalvaResumoJsonEGeraPdfDeLeitura(self):
        discursos = [
            criarDiscurso(0, 2.0, 0b1, "Orador A"),
            criarDiscurso(1, 1.0, 0b10, "Orador B"),
        ]
        resultado = selecionarDiscursosResumo(discursos)

        with tempfile.TemporaryDirectory() as diretorioTemporario:
            diretorio = Path(diretorioTemporario)
            caminhoJson = diretorio / "resumoExtrativo.json"
            caminhoPdf = diretorio / "resumoExtrativo.pdf"

            salvarResumoJson(resultado, caminhoJson, "entrada.pdf", 5)
            gerarResumoPdf(resultado, caminhoPdf, "entrada.pdf", 5)

            dados = json.loads(caminhoJson.read_text(encoding="utf-8"))
            documento = fitz.open(caminhoPdf)
            textoPdf = "".join(pagina.get_text() for pagina in documento)
            documento.close()

        self.assertEqual(dados["documento"], "entrada.pdf")
        self.assertEqual(dados["frasesAnalisadas"], 5)
        self.assertEqual(dados["frasesSelecionadas"], 2)
        self.assertEqual(dados["discursos"][0]["frase"], "Frase 0")
        self.assertIn("Resumo Extrativo do Debate Legislativo", textoPdf)
        self.assertIn("Documento: entrada.pdf", textoPdf)
        self.assertIn("Frases analisadas: 5", textoPdf)
        self.assertIn("Frases selecionadas: 2", textoPdf)
        self.assertNotIn("Criterio", textoPdf)


if __name__ == "__main__":
    unittest.main()
