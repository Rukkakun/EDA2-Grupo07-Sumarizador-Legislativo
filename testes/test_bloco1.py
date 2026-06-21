import tempfile
import unittest
from pathlib import Path

import fitz

from estruturas.tabelaHash import TabelaHash
from processamento.extratorPDF import extrairTextoPdf
from processamento.main import tokenizarDiscursos
from processamento.limpezaEstrutural import extrairDiscursosDeTexto


def normalizarFraseFake(frase):
    termos = {
        "A política pública protege famílias.": ["politica", "publico", "proteger", "familia"],
        "Famílias precisam de proteção pública.": ["familia", "precisar", "protecao", "publico"],
    }
    return termos.get(frase, [])


class TestTabelaHash(unittest.TestCase):
    def testInsereBuscaEReaproveitaLapideComColisao(self):
        tabelaHash = TabelaHash(7)

        idPrimeiro = tabelaHash.obterId("a")
        idSegundo = tabelaHash.obterId("h")

        self.assertNotEqual(idPrimeiro, idSegundo)
        self.assertEqual(tabelaHash.buscar("a"), idPrimeiro)
        self.assertEqual(tabelaHash.buscar("h"), idSegundo)

        self.assertTrue(tabelaHash.remover("a"))
        self.assertIsNone(tabelaHash.buscar("a"))

        idTerceiro = tabelaHash.obterId("o")

        self.assertEqual(idTerceiro, idPrimeiro)
        self.assertEqual(tabelaHash.buscar("o"), idTerceiro)
        self.assertEqual(tabelaHash.quantidade, 2)


class TestLimpezaEstrutural(unittest.TestCase):
    def testExtraiDiscursosSeparandoOradorEFraseSemRuido(self):
        texto = """
Sessão de: 02/02/2026
Notas Taquigráficas
CÂMARA DOS DEPUTADOS
ORDEM DO DIA
O SR. JOÃO SILVA (Partido - UF. Sem revisão do orador.) - Presidente, defendemos a política pública. (Pausa.)
A política pública protege famílias.
2/36
A SRA. MARIA SOUZA (Partido - UF) - Famílias precisam de proteção pública.
"""

        discursos = extrairDiscursosDeTexto(texto)

        self.assertEqual(len(discursos), 3)
        self.assertEqual(discursos[0].orador, "JOÃO SILVA (Partido - UF. Sem revisão do orador.)")
        self.assertEqual(discursos[0].frase, "Presidente, defendemos a política pública.")
        self.assertEqual(discursos[1].orador, "JOÃO SILVA (Partido - UF. Sem revisão do orador.)")
        self.assertEqual(discursos[1].frase, "A política pública protege famílias.")
        self.assertEqual(discursos[2].orador, "MARIA SOUZA (Partido - UF)")
        self.assertEqual(discursos[2].frase, "Famílias precisam de proteção pública.")
        self.assertNotIn("JOÃO", discursos[0].frase)


    def testRemoveRuidoDasNotasDeComissoes(self):
        texto = """
Reunião de: 10/02/2026
Notas Taquigráficas - Comissões
CÂMARA DOS DEPUTADOS
Registro oficial sem redação final.
1 / 15
A SRA. PRESIDENTE (Juliana Cardoso. Bloco/PT - SP) - Este aqui a Deputada fez o registro.
(Não identificado) - (Intervenção fora do microfone. Inaudível.)
Pode ser?
(Não identificado) - Ele vai concorrer...
2 / 15
Reunião de: 10/02/2026
Notas Taquigráficas - Comissões
O SR. AIRTON FALEIRO (Bloco/PT - PA) - A Amazônia precisa ser protegida.
"""

        discursos = extrairDiscursosDeTexto(texto)
        frases = [discurso.frase for discurso in discursos]

        self.assertEqual(frases, [
            "Este aqui a Deputada fez o registro.",
            "Pode ser?",
            "A Amazônia precisa ser protegida.",
        ])
        self.assertFalse(any("Notas Taquigráficas" in frase for frase in frases))
        self.assertFalse(any("Reunião de:" in frase for frase in frases))
        self.assertFalse(any("Não identificado" in frase for frase in frases))


    def testRemoveRubricasTaquigraficasGenericas(self):
        texto = """
O SR. TESTE (PARTIDO - UF) - Começamos a reunião. (Pausa prolongada.)
(Pausa)
Continuamos os trabalhos. (Desligamento do microfone.)
(Intervenção fora do microfone. Inaudível.)
Houve acordo. (Risos.) (Palmas.)
(Manifestação em língua indígena.)
(Procede-se ao descerramento de placa de homenagem.)
Este trecho mantém uma referência comum (art. 5º do Ato da Mesa).
"""

        discursos = extrairDiscursosDeTexto(texto)
        frases = [discurso.frase for discurso in discursos]

        self.assertEqual(frases, [
            "Começamos a reunião.",
            "Continuamos os trabalhos.",
            "Houve acordo.",
            "Este trecho mantém uma referência comum (art. 5º do Ato da Mesa).",
        ])
        self.assertFalse(any("Pausa" in frase for frase in frases))
        self.assertFalse(any("microfone" in frase for frase in frases))
        self.assertFalse(any("Risos" in frase for frase in frases))
        self.assertFalse(any("Palmas" in frase for frase in frases))


class TestBloco1(unittest.TestCase):
    def testProcessaApenasFraseEmTokensEBitsets(self):
        texto = """
O SR. JOÃO SILVA (Partido - UF) - A política pública protege famílias.
A SRA. MARIA SOUZA (Partido - UF) - Famílias precisam de proteção pública.
"""
        discursos = extrairDiscursosDeTexto(texto)

        resultado = tokenizarDiscursos(discursos, normalizarFrase=normalizarFraseFake)

        self.assertEqual(resultado.vocabulario.quantidade, 6)
        self.assertEqual(resultado.discursos[0].orador, "JOÃO SILVA (Partido - UF)")
        self.assertEqual(resultado.discursos[0].tokens, [0, 1, 2, 3])
        self.assertEqual(resultado.discursos[1].tokens, [3, 4, 5, 1])

        indiceJoao = resultado.vocabulario.buscar("joao")
        self.assertIsNone(indiceJoao)

        indiceFamilia = resultado.vocabulario.buscar("familia")
        self.assertIsInstance(resultado.discursos[0].bitset, int)
        self.assertIsInstance(resultado.discursos[1].bitset, int)
        self.assertTrue(resultado.discursos[0].bitset & (1 << indiceFamilia))
        self.assertTrue(resultado.discursos[1].bitset & (1 << indiceFamilia))


class TestExtratorPdf(unittest.TestCase):
    def testExtraiTextoDePdf(self):
        with tempfile.TemporaryDirectory() as diretorioTemporario:
            caminhoPdf = Path(diretorioTemporario) / "entrada.pdf"
            documento = fitz.open()
            pagina = documento.new_page()
            pagina.insert_text((72, 72), "O SR. TESTE - Texto do PDF.")
            documento.save(caminhoPdf)
            documento.close()

            texto = extrairTextoPdf(caminhoPdf)

        self.assertIn("O SR. TESTE - Texto do PDF.", texto)


if __name__ == "__main__":
    unittest.main()
