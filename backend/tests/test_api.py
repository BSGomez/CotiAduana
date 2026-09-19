from auth import limpiar_tokens
from db import limpiar_memoria
from app import app

CREDENCIALES = {"usuario": "admin", "clave": "calidad"}


def cliente():
    limpiar_memoria()
    limpiar_tokens()
    app.config["TESTING"] = True
    return app.test_client()


def cliente_con_auth():
    http = cliente()
    token = http.post("/login", json=CREDENCIALES).get_json()["token"]
    return http, {"Authorization": f"Bearer {token}"}


def test_salud_responde_ok():
    respuesta = cliente().get("/salud")

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {"estado": "ok"}


def test_login_correcto_devuelve_token():
    respuesta = cliente().post("/login", json=CREDENCIALES)
    datos = respuesta.get_json()

    assert respuesta.status_code == 200
    assert datos["usuario"] == "admin"
    assert datos["token"]


def test_login_incorrecto():
    respuesta = cliente().post(
        "/login",
        json={"usuario": "admin", "clave": "mala"},
    )

    assert respuesta.status_code == 401
    assert "error" in respuesta.get_json()


def test_cotizar_sin_login_devuelve_401():
    respuesta = cliente().post(
        "/cotizaciones",
        json={
            "fob": "1000",
            "flete": "100",
            "seguro": "50",
            "categoria": "tecnologia",
        },
    )

    assert respuesta.status_code == 401


def test_cotizar_tecnologia_devuelve_json_esperado():
    http, auth = cliente_con_auth()
    respuesta = http.post(
        "/cotizaciones",
        json={
            "fob": "1000",
            "flete": "100",
            "seguro": "50",
            "categoria": "tecnologia",
        },
        headers=auth,
    )
    datos = respuesta.get_json()

    assert respuesta.status_code == 201
    assert datos["id"]
    assert datos["cif"] == "1150.00"
    assert datos["dai"] == "172.50"
    assert datos["iva"] == "158.70"
    assert datos["total_impuestos"] == "331.20"
    assert datos["total"] == "1481.20"
    assert datos["usuario"] == "admin"


def test_listar_cotizaciones_del_usuario():
    http, auth = cliente_con_auth()
    http.post(
        "/cotizaciones",
        json={"fob": "1000", "flete": "0", "seguro": "0", "categoria": "libros"},
        headers=auth,
    )
    http.post(
        "/cotizaciones",
        json={"fob": "500", "flete": "0", "seguro": "0", "categoria": "ropa"},
        headers=auth,
    )

    respuesta = http.get("/cotizaciones", headers=auth)
    datos = respuesta.get_json()

    assert respuesta.status_code == 200
    assert len(datos) == 2
    assert {item["categoria"] for item in datos} == {"4901.91.00.00", "6109.10.00.00"}


def test_consultar_cotizacion_guardada():
    http, auth = cliente_con_auth()
    creada = http.post(
        "/cotizaciones",
        json={
            "fob": "1000",
            "flete": "0",
            "seguro": "0",
            "categoria": "libros",
        },
        headers=auth,
    )
    id_cotizacion = creada.get_json()["id"]

    respuesta = http.get(f"/cotizaciones/{id_cotizacion}", headers=auth)
    datos = respuesta.get_json()

    assert respuesta.status_code == 200
    assert datos["id"] == id_cotizacion
    assert datos["dai"] == "0.00"
    assert datos["iva"] == "120.00"


def test_consultar_cotizacion_inexistente_devuelve_404():
    http, auth = cliente_con_auth()
    respuesta = http.get("/cotizaciones/no-existe", headers=auth)

    assert respuesta.status_code == 404
    assert "error" in respuesta.get_json()


def test_cotizar_rechaza_categoria_invalida():
    http, auth = cliente_con_auth()
    respuesta = http.post(
        "/cotizaciones",
        json={
            "fob": "100",
            "flete": "0",
            "seguro": "0",
            "categoria": "alimentos",
        },
        headers=auth,
    )

    assert respuesta.status_code == 400
    assert "error" in respuesta.get_json()


def test_cotizar_rechaza_campos_faltantes():
    http, auth = cliente_con_auth()
    respuesta = http.post(
        "/cotizaciones",
        json={"fob": "100"},
        headers=auth,
    )

    assert respuesta.status_code == 400
    assert respuesta.get_json()["error"] == "Faltan campos"


def test_buscar_aranceles():
    http, auth = cliente_con_auth()
    respuesta = http.get("/aranceles?q=8506", headers=auth)
    datos = respuesta.get_json()

    assert respuesta.status_code == 200
    assert len(datos) >= 1
    assert "codigo" in datos[0]
    assert "dai_nmf" in datos[0]


def test_frontend_se_publica_en_la_raiz():
    respuesta = cliente().get("/")
    html = respuesta.get_data(as_text=True)

    assert respuesta.status_code == 200
    assert "CotiAduana" in html
    assert "form-login" in html
    assert "admin" not in html
    assert "calidad" not in html
    assert "Cotizador de impuestos de importación" not in html
    assert "Código UUID" not in html
    assert "buscar-arancel" in html

#Comando para ejecutar los tests: py -3 -m pytest -v