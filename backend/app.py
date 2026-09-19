from decimal import Decimal, InvalidOperation
from pathlib import Path
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from auth import borrar_token, crear_token, credenciales_validas, usuario_de_token
from calculator import calcular_cotizacion
from db import guardar, inicializar, listar, obtener
import aranceles

load_dotenv()

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cotiaduana-dev")
CORS(app)

CAMPOS = ("fob", "flete", "seguro", "categoria")


def _a_json(resultado):
    convertido = {}
    for clave, valor in resultado.items():
        convertido[clave] = str(valor) if not isinstance(valor, (str, int, float, bool, type(None))) else valor
    return convertido


def _token_actual():
    header = request.headers.get("Authorization", "")
    return header.removeprefix("Bearer ").strip()


def _exige_login():
    if not usuario_de_token(_token_actual()):
        return jsonify({"error": "No autenticado"}), 401
    return None


@app.get("/")
def inicio():
    return send_from_directory(FRONTEND, "index.html")


@app.get("/app.js")
def frontend_js():
    return send_from_directory(FRONTEND, "app.js")


@app.get("/salud")
def salud():
    return jsonify({"estado": "ok"}), 200


@app.get("/aranceles")
def consultar_aranceles():
    no_logueado = _exige_login()
    if no_logueado:
        return no_logueado

    q = request.args.get("q", "")
    return jsonify(aranceles.buscar(q)), 200


@app.post("/login")
def login():
    datos = request.get_json(silent=True) or {}
    usuario = datos.get("usuario")
    clave = datos.get("clave")
    if not credenciales_validas(usuario, clave):
        return jsonify({"error": "Credenciales invalidas"}), 401

    token = crear_token(usuario)
    return jsonify({"usuario": usuario, "token": token}), 200


@app.post("/logout")
def logout():
    borrar_token(_token_actual())
    return jsonify({"estado": "ok"}), 200


@app.get("/sesion")
def sesion():
    no_logueado = _exige_login()
    if no_logueado:
        return no_logueado
    return jsonify({"usuario": usuario_de_token(_token_actual())}), 200


@app.post("/cotizaciones")
def crear_cotizacion():
    no_logueado = _exige_login()
    if no_logueado:
        return no_logueado

    datos = request.get_json(silent=True) or {}
    faltantes = [campo for campo in CAMPOS if campo not in datos]
    if faltantes:
        return jsonify({"error": "Faltan campos", "campos": faltantes}), 400

    try:
        resultado = calcular_cotizacion(
            fob=datos["fob"],
            flete=datos["flete"],
            seguro=datos["seguro"],
            categoria=datos["categoria"],
        )
    except (ValueError, InvalidOperation, TypeError):
        return jsonify({"error": "Datos invalidos"}), 400

    resultado["usuario"] = usuario_de_token(_token_actual())
    try:
        guardada = guardar(resultado)
    except Exception:
        return jsonify({"error": "No se pudo guardar la cotizacion"}), 500
    return jsonify(_a_json(guardada)), 201


@app.get("/cotizaciones")
def listar_cotizaciones():
    no_logueado = _exige_login()
    if no_logueado:
        return no_logueado

    usuario = usuario_de_token(_token_actual())
    return jsonify([_a_json(item) for item in listar(usuario)]), 200


@app.get("/cotizaciones/<id_cotizacion>")
def consultar_cotizacion(id_cotizacion):
    no_logueado = _exige_login()
    if no_logueado:
        return no_logueado

    encontrada = obtener(id_cotizacion, usuario_de_token(_token_actual()))
    if encontrada is None:
        return jsonify({"error": "Cotizacion no encontrada"}), 404
    return jsonify(_a_json(encontrada)), 200


inicializar()
