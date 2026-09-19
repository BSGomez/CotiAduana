import json
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).with_name("data") / "aranceles.json"


@lru_cache(maxsize=1)
def cargar():
    if not DATA.exists():
        return []
    return json.loads(DATA.read_text(encoding="utf-8"))


def indice_por_codigo():
    return {item["codigo"]: item for item in cargar()}


def obtener(codigo):
    codigo = str(codigo or "").strip()
    return indice_por_codigo().get(codigo)


def buscar(texto, limite=30):
    q = str(texto or "").strip().lower()
    if len(q) < 2:
        return []

    resultados = []
    for item in cargar():
        if q in item["codigo"].lower() or q in item["descripcion"].lower():
            resultados.append(item)
            if len(resultados) >= limite:
                break
    return resultados
