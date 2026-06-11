from pathlib import Path

import fitz


def extrairTextoPdf(caminhoPdf):
    caminhoPdf = Path(caminhoPdf)
    partesTexto = []

    with fitz.open(caminhoPdf) as documento:
        for pagina in documento:
            partesTexto.append(pagina.get_text())

    return "\n".join(partesTexto)
