"""
Extrae del Arancel Centroamericano 2026:
- codigo SAC (10 digitos)
- descripcion
- DAI NMF (columna Nacion Mas Favorecida)

Uso:
  py -3 scripts/extraer_arancel.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "2026-ARANCEL-CENTROAMERICANO-DE-IMPORTACION-V.-1.2.pdf"
SALIDA = ROOT / "backend" / "data" / "aranceles.json"

CODIGO_RE = re.compile(r"(?<!\d)(\d{4}\.\d{2}\.\d{2}\.\d{2})(?!\d)")
TASA_RE = re.compile(r"^(?:\d+(?:\.\d+)?|E|\d+/\w+)$")
# "84.02", "87.02" son referencias a partidas, no DAI
PARTIDA_RE = re.compile(r"^\d{2}\.\d{2}$")


def es_token_tasa(token: str) -> bool:
    return bool(TASA_RE.match(token))


def limpiar_descripcion(texto: str) -> str:
    texto = re.sub(r"\s+", " ", texto).strip(" -:\t")
    texto = re.sub(
        r"Documento elaborado por.*$",
        "",
        texto,
        flags=re.IGNORECASE,
    ).strip()
    return texto[:280]


def parsear_bloque(bloque: str) -> tuple[str, float] | None:
    bloque = re.sub(r"\s+", " ", bloque).strip()
    if not bloque:
        return None

    tokens = bloque.split(" ")
    # Desde el final: columnas de tasas (NMF + TLC...)
    i = len(tokens) - 1
    tasas: list[str] = []
    while i >= 0 and es_token_tasa(tokens[i]):
        tasas.append(tokens[i])
        i -= 1
    tasas.reverse()

    if len(tasas) < 6:
        return None

    # Si el texto previo es "Capitulo 87" / "partida 84.02", el primer token NO es NMF.
    previo = tokens[i].lower() if i >= 0 else ""
    while tasas and (
        previo in {"capítulo", "capitulo", "capítulos", "capitulos", "partida", "partidas", "y"}
        or PARTIDA_RE.match(tasas[0])
    ):
        tasas.pop(0)
        # no movemos i: esos numeros vinieron despues del texto previo
        if not tasas:
            return None
        # solo quitar una referencia tipica
        if previo not in {"capítulo", "capitulo", "capítulos", "capitulos", "partida", "partidas", "y"}:
            break
        previo = ""

    # Densidades u otras medidas: "inferior a 0.94"
    desc_prev = " ".join(tokens[max(0, i - 2) : i + 1]).lower()
    if tasas and re.search(r"(inferior|superior|igual)\s+a$", desc_prev):
        tasas.pop(0)

    if len(tasas) < 5:
        return None

    nmf_token = tasas[0]
    if nmf_token == "E" or PARTIDA_RE.match(nmf_token):
        return None

    try:
        nmf = float(nmf_token)
    except ValueError:
        return None

    if nmf < 0 or nmf > 100:
        return None

    descripcion = limpiar_descripcion(" ".join(tokens[: i + 1]))
    if len(descripcion) < 2:
        return None

    return descripcion, nmf


def extraer(pdf_path: Path) -> list[dict]:
    reader = PdfReader(str(pdf_path))
    textos = []
    total = len(reader.pages)
    for i, pagina in enumerate(reader.pages, start=1):
        textos.append(pagina.extract_text() or "")
        if i % 50 == 0 or i == total:
            print(f"Leyendo PDF... {i}/{total}", flush=True)

    texto = "\n".join(textos)
    partes = CODIGO_RE.split(texto)
    registros: dict[str, dict] = {}

    for i in range(1, len(partes), 2):
        codigo = partes[i]
        bloque = partes[i + 1] if i + 1 < len(partes) else ""
        bloque = bloque.split("INCISO")[0]
        bloque = bloque.split("ARANCEL CENTROAMERICANO")[0]
        parseado = parsear_bloque(bloque)
        if not parseado:
            continue
        descripcion, nmf = parseado
        registros[codigo] = {
            "codigo": codigo,
            "descripcion": descripcion,
            "dai_nmf": nmf,
        }

    return sorted(registros.values(), key=lambda x: x["codigo"])


def main() -> int:
    if not PDF.exists():
        print(f"No se encontro el PDF: {PDF}")
        return 1

    print(f"PDF: {PDF.name}")
    aranceles = extraer(PDF)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(
        json.dumps(aranceles, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    tasas = sorted({item["dai_nmf"] for item in aranceles})
    print(f"Extraidos: {len(aranceles)} incisos")
    print(f"Tasas NMF distintas: {tasas}")
    print(f"Guardado en: {SALIDA}")
    if aranceles:
        print("Ejemplo:", aranceles[0])
        print("Ejemplo:", aranceles[min(2000, len(aranceles) - 1)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
