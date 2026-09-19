import hmac
import secrets

USUARIOS = {
    "admin": "calidad",
}

_tokens = {}


def credenciales_validas(usuario, clave):
    guardada = USUARIOS.get(str(usuario or ""), "")
    return hmac.compare_digest(guardada, str(clave or "")) and usuario in USUARIOS


def crear_token(usuario):
    token = secrets.token_urlsafe(32)
    _tokens[token] = usuario
    return token


def usuario_de_token(token):
    return _tokens.get(token)


def borrar_token(token):
    _tokens.pop(token, None)


def limpiar_tokens():
    _tokens.clear()
