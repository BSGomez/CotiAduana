CREATE TABLE IF NOT EXISTS cotizaciones (
    id UUID PRIMARY KEY,
    fob NUMERIC(12, 2) NOT NULL,
    flete NUMERIC(12, 2) NOT NULL,
    seguro NUMERIC(12, 2) NOT NULL,
    categoria VARCHAR(20) NOT NULL,
    descripcion TEXT,
    tasa_dai NUMERIC(8, 6) NOT NULL,
    cif NUMERIC(12, 2) NOT NULL,
    dai NUMERIC(12, 2) NOT NULL,
    iva NUMERIC(12, 2) NOT NULL,
    total_impuestos NUMERIC(12, 2) NOT NULL,
    total NUMERIC(12, 2) NOT NULL,
    usuario VARCHAR(50) NOT NULL,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
