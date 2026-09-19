# CotiAduana

Cotizador aduanero digital (Flask + PostgreSQL + HTML/JS).
Cálculo: CIF, DAI (Arancel Centroamericano 2026 / NMF) e IVA 12%.

## Credenciales de revisión QA

- Usuario: `admin`
- Clave: `calidad`

## Pruebas locales

```powershell
py -3 -m pytest -v
cd backend
py -3 -m flask --app app run --port 5001
```

## Despliegue gratuito (Render + Supabase)

### 1) Supabase (base de datos)

1. Crea un proyecto en https://supabase.com
2. En **SQL Editor**, ejecuta el contenido de `backend/schema.sql`
3. En **Project Settings → Database**, copia la **URI** de conexión (modo Session o URI).
4. Debe verse similar a:
   `postgresql://postgres:...@db.xxxxx.supabase.co:5432/postgres`
5. Si Render falla por SSL, agrega al final: `?sslmode=require`

### 2) GitHub

Sube este repositorio a GitHub (público o privado).

### 3) Render (API + frontend)

1. Entra a https://render.com → **New → Blueprint** (usa `render.yaml`)  
   o **New → Web Service** y conecta el repo.
2. Si no usas Blueprint:
   - **Build:** `pip install -r backend/requirements.txt`
   - **Start:** `gunicorn --chdir backend app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
3. Variables de entorno:
   - `SECRET_KEY` = una cadena larga aleatoria
   - `DATABASE_URL` = la URI de Supabase
4. Deploy. La URL quedará como:
   `https://cotiaduana.onrender.com`

### Nota del plan free de Render

La primera visita puede tardar ~30–60 s si el servicio estaba dormido. Eso es normal.

## Estructura

- `backend/` API Flask, cálculo, aranceles, pruebas
- `frontend/` login + cotizador
- `scripts/extraer_arancel.py` regenera `backend/data/aranceles.json` desde el PDF del ACI
- `backend/data/aranceles.json` ~4700 códigos SAC con DAI NMF
