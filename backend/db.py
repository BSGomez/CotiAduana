import os
import ssl
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse

_memoria = {}

CAMPOS_FILA = (
    "id",
    "fob",
    "flete",
    "seguro",
    "categoria",
    "descripcion",
    "tasa_dai",
    "cif",
    "dai",
    "iva",
    "total_impuestos",
    "total",
    "usuario",
    "creado_en",
)


def generar_id():
    return str(uuid.uuid4())


def limpiar_memoria():
    _memoria.clear()


def usar_postgres():
    if os.getenv("PYTEST_CURRENT_TEST"):
        return False
    return bool(os.getenv("DATABASE_URL"))


def inicializar():
    if not usar_postgres():
        return

    schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    conexion = _conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute(schema)
        conexion.commit()
    finally:
        conexion.close()


def guardar(cotizacion):
    registro = dict(cotizacion)
    registro["id"] = generar_id()
    registro["usuario"] = registro.get("usuario") or ""
    registro["creado_en"] = datetime.now(timezone.utc).isoformat()

    if usar_postgres():
        _guardar_postgres(registro)
    else:
        _memoria[registro["id"]] = registro

    return registro


def obtener(id_cotizacion, usuario=None):
    if usar_postgres():
        encontrada = _obtener_postgres(id_cotizacion)
    else:
        encontrada = _memoria.get(id_cotizacion)

    if encontrada is None:
        return None
    if usuario and encontrada.get("usuario") != usuario:
        return None
    return encontrada


def listar(usuario):
    if usar_postgres():
        filas = _listar_postgres(usuario)
    else:
        filas = [c for c in _memoria.values() if c.get("usuario") == usuario]
    return sorted(filas, key=lambda c: str(c.get("creado_en") or ""), reverse=True)


def _conexion():
    import pg8000.native

    url = os.getenv("DATABASE_URL")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    partes = urlparse(url)
    kwargs = {
        "user": unquote(partes.username or "postgres"),
        "password": unquote(partes.password or ""),
        "host": partes.hostname or "127.0.0.1",
        "port": partes.port or 5432,
        "database": unquote(partes.path.lstrip("/") or "postgres"),
    }
    if kwargs["host"] not in ("localhost", "127.0.0.1"):
        contexto = ssl.create_default_context()
        kwargs["ssl_context"] = contexto
    return pg8000.native.Connection(**kwargs)


def _guardar_postgres(cotizacion):
    conexion = _conexion()
    try:
        conexion.run(
            """
            INSERT INTO cotizaciones (
                id, fob, flete, seguro, categoria, descripcion, tasa_dai,
                cif, dai, iva, total_impuestos, total, usuario
            ) VALUES (
                :id, :fob, :flete, :seguro, :categoria, :descripcion, :tasa_dai,
                :cif, :dai, :iva, :total_impuestos, :total, :usuario
            )
            """,
            id=cotizacion["id"],
            fob=str(cotizacion["fob"]),
            flete=str(cotizacion["flete"]),
            seguro=str(cotizacion["seguro"]),
            categoria=cotizacion["categoria"],
            descripcion=cotizacion.get("descripcion") or "",
            tasa_dai=str(cotizacion["tasa_dai"]),
            cif=str(cotizacion["cif"]),
            dai=str(cotizacion["dai"]),
            iva=str(cotizacion["iva"]),
            total_impuestos=str(cotizacion["total_impuestos"]),
            total=str(cotizacion["total"]),
            usuario=cotizacion["usuario"],
        )
        conexion.commit()
    finally:
        conexion.close()


def _fila(valores):
    return dict(zip(CAMPOS_FILA, valores))


def _obtener_postgres(id_cotizacion):
    conexion = _conexion()
    try:
        filas = conexion.run(
            """
            SELECT id, fob, flete, seguro, categoria, descripcion, tasa_dai,
                   cif, dai, iva, total_impuestos, total, usuario, creado_en
            FROM cotizaciones
            WHERE id = :id
            """,
            id=id_cotizacion,
        )
    finally:
        conexion.close()
    return _fila(filas[0]) if filas else None


def _listar_postgres(usuario):
    conexion = _conexion()
    try:
        filas = conexion.run(
            """
            SELECT id, fob, flete, seguro, categoria, descripcion, tasa_dai,
                   cif, dai, iva, total_impuestos, total, usuario, creado_en
            FROM cotizaciones
            WHERE usuario = :usuario
            ORDER BY creado_en DESC
            """,
            usuario=usuario,
        )
    finally:
        conexion.close()
    return [_fila(fila) for fila in filas]
