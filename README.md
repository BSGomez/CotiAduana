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
### Nota del plan free de Render

La primera visita puede tardar ~30–60 s si el servicio estaba dormido. Eso es normal.

## Estructura

- `backend/` API Flask, cálculo, aranceles, pruebas
- `frontend/` login + cotizador
- `scripts/extraer_arancel.py` regenera `backend/data/aranceles.json` desde el PDF del ACI
- `backend/data/aranceles.json` ~4700 códigos SAC con DAI NMF
