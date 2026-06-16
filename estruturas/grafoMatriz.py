from dataclasses import dataclass, field


@dataclass
class GrafoMatriz:
    quantidadeVertices: int
    matrizAdjacencia: list[list[float]] = field(default_factory=list)


def criarGrafo(quantidadeVertices):
    matrizAdjacencia = [
        [0.0 for _ in range(quantidadeVertices)]
        for _ in range(quantidadeVertices)
    ]
    return GrafoMatriz(
        quantidadeVertices=quantidadeVertices,
        matrizAdjacencia=matrizAdjacencia,
    )


def adicionarAresta(grafo, verticeOrigem, verticeDestino, peso):
    if verticeOrigem == verticeDestino:
        return

    grafo.matrizAdjacencia[verticeOrigem][verticeDestino] = float(peso)
    grafo.matrizAdjacencia[verticeDestino][verticeOrigem] = float(peso)


def existeAresta(grafo, verticeOrigem, verticeDestino):
    return grafo.matrizAdjacencia[verticeOrigem][verticeDestino] > 0.0


def grauMatriz(grafo, vertice):
    grau = 0

    for peso in grafo.matrizAdjacencia[vertice]:
        if peso > 0.0:
            grau += 1

    return grau


def liberarGrafo(grafo):
    grafo.quantidadeVertices = 0
    grafo.matrizAdjacencia = []


def imprimirGrafo(grafo):
    for linha in grafo.matrizAdjacencia:
        valores = [f"{peso:.2f}" for peso in linha]
        print(" ".join(valores))
