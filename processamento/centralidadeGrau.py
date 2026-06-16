import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ResultadoBloco3:
    pontuacoes: list[float]


def processarBloco3(grafo):
    pontuacoes = []

    for linha in grafo.matrizAdjacencia:
        pontuacoes.append(sum(linha))

    return ResultadoBloco3(pontuacoes=pontuacoes)


def salvarResultadoBloco3(resultado, diretorioSaida):
    diretorioSaida = Path(diretorioSaida)
    diretorioSaida.mkdir(parents=True, exist_ok=True)
    caminhoPontuacoes = diretorioSaida / "pontuacoesCentralidade.json"
    caminhoPontuacoes.write_text(
        json.dumps(resultado.pontuacoes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
