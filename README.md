# CotiAduana

Cotizador aduanero digital para estimar impuestos de importación (CIF, DAI e IVA) usando tasas reales del **Arancel Centroamericano de Importación 2026** (columna NMF).

- **App publicada:** https://cotiaduana.onrender.com
- **Repositorio:** https://github.com/BSGomez/CotiAduana
- **Desarrollador:** Bryan S. Gómez
- **Curso:** Aseguramiento de la Calidad de Software (QA)
- **Metodología:** Extreme Programming (XP)
- **Estándar de calidad:** ISO 9001:2015 (ciclo PHVA)

## Acceso para revisión QA

| Campo | Valor |
|---|---|
| URL | https://cotiaduana.onrender.com |
| Usuario | `admin` |
| Contraseña | `calidad` |

En el plan gratuito de Render el servidor se duerme por inactividad. La **primera visita** puede tardar 30–60 segundos; después responde normal. No hay que encender nada: al abrir el link el servicio se despierta solo.

---

## Manual de uso

### 1. Iniciar sesión

1. Abre la URL del sistema.
2. Ingresa usuario `admin` y contraseña `calidad`.
3. Pulsa **Entrar**.

Si las credenciales son incorrectas, el sistema muestra error y no deja cotizar.

### 2. Crear una cotización

1. Completa:
   - **Valor FOB:** precio de la mercancía.
   - **Flete:** costo de transporte.
   - **Seguro:** costo del seguro.
2. En **Código SAC / mercancía** escribe al menos 2 caracteres (código o descripción), por ejemplo `0101` o `maíz`.
3. Elige una sugerencia de la lista. Debes ver algo como:  
   `0101.21.00.00 · DAI 0% · Reproductores de raza pura`
4. Pulsa **Calcular y guardar**.

El sistema muestra:

- Referencia UUID
- Código SAC y descripción
- DAI NMF aplicado
- CIF, DAI, IVA, total de impuestos y total

### 3. Consultar cotizaciones guardadas

En **Mis cotizaciones** aparece el historial del usuario.

1. Haz clic en una fila para ver el detalle.
2. No necesitas copiar el UUID: la lista es el medio de consulta.

### 4. Cerrar sesión

Pulsa **Cerrar sesión** (arriba a la derecha). El token se elimina y vuelves al login.

### Códigos SAC de prueba

| Código SAC | DAI NMF | Descripción |
|---|---|---|
| `0101.21.00.00` | 0% | Reproductores de raza pura |
| `0207.26.10.00` | 5% | En pasta, deshuesados mecánicamente |
| `0101.29.00.00` | 10% | Los demás |
| `0201.10.00.00` | 15% | En canales o medias canales |
| `1005.90.30.00` | 20% | Maíz blanco |

Ejemplo con FOB `1000`, flete `0` y seguro `0` para `0201.10.00.00` (15%):

- CIF = 1000
- DAI = 150
- IVA = 138
- Total = 1288

---

## Cómo calcula el sistema

- **CIF** = FOB + Flete + Seguro
- **DAI** = CIF × (tasa NMF / 100)
- **IVA** = (CIF + DAI) × 0.12
- **Total impuestos** = DAI + IVA
- **Total** = CIF + Total impuestos

Los montos se calculan con `Decimal` y se redondean a 2 decimales (dinero real).  
La tasa DAI sale del código SAC elegido, no de categorías inventadas.

---

## Ejecutar en local

Desde la carpeta del proyecto:

```powershell
py -3 -m pytest -v
```

Levantar la página:

```powershell
cd backend
py -3 -m flask --app app run --port 5001
```

Abre http://127.0.0.1:5001

Sin `DATABASE_URL`, las cotizaciones se guardan en memoria: al reiniciar Flask la lista se vacía. En producción (Render + Supabase) sí persisten.

---

## Pruebas

Hay **30 pruebas** automatizadas con PyTest:

- Cálculo CIF / DAI / IVA
- Login correcto e incorrecto
- Cotizar sin token (401)
- Campos faltantes o código inválido (400)
- Guardar, listar y consultar cotizaciones
- Búsqueda de aranceles

Comando: `py -3 -m pytest -v`

---

## API (resumen)

| Método | Ruta | Acceso | Qué hace |
|---|---|---|---|
| GET | `/salud` | Público | Healthcheck |
| POST | `/login` | Público | Devuelve token |
| POST | `/logout` | Token | Cierra sesión |
| GET | `/aranceles?q=` | Token | Busca códigos SAC |
| POST | `/cotizaciones` | Token | Calcula y guarda |
| GET | `/cotizaciones` | Token | Lista del usuario |
| GET | `/cotizaciones/<id>` | Token | Consulta por UUID |

---

## Estructura del proyecto

| Carpeta / archivo | Contenido |
|---|---|
| `backend/` | API Flask, cálculo, base de datos, pruebas |
| `backend/data/aranceles.json` | ~4700 códigos SAC con DAI NMF |
| `frontend/` | Login, cotizador y listado |
| `scripts/extraer_arancel.py` | Extrae el arancel desde el PDF del ACI 2026 |
| `backend/schema.sql` | Tabla `cotizaciones` en PostgreSQL |

---

## Despliegue

- **Frontend + API:** [Render](https://render.com) (Free)
- **Base de datos:** [Supabase](https://supabase.com) (PostgreSQL)
- **Código:** GitHub

Variables de entorno en Render:

- `SECRET_KEY`
- `DATABASE_URL` (URI de PostgreSQL de Supabase, puerto 5432)

Build: `pip install -r backend/requirements.txt`  
Start: `gunicorn --chdir backend app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
