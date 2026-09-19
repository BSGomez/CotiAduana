from auth import crear_token, credenciales_validas, usuario_de_token


def test_acepta_admin_con_clave_correcta():
    assert credenciales_validas("admin", "calidad") is True


def test_rechaza_clave_incorrecta():
    assert credenciales_validas("admin", "otra") is False


def test_rechaza_usuario_inexistente():
    assert credenciales_validas("otro", "calidad") is False


def test_token_permite_identificar_usuario():
    token = crear_token("admin")
    assert usuario_de_token(token) == "admin"
    assert usuario_de_token("token-falso") is None
