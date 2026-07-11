import psycopg2
import configparser
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from config.db_config import connection

query_turnos = """
CREATE TABLE IF NOT EXISTS turnos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    dni VARCHAR(20) NOT NULL,
    obra_social VARCHAR(100),
    motivo_consulta TEXT,
    fecha DATE DEFAULT CURRENT_DATE,
    hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'pendiente',
    usuario VARCHAR(100)
);
"""

query_historial = """
CREATE TABLE IF NOT EXISTS historial_cambios (
    id SERIAL PRIMARY KEY,
    tabla VARCHAR(50) NOT NULL,
    registro_id INTEGER,
    accion VARCHAR(50) NOT NULL,
    detalle TEXT,
    usuario VARCHAR(100),
    dni VARCHAR(20),
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

migrate_historial = """
ALTER TABLE historial_cambios ADD COLUMN IF NOT EXISTS usuario VARCHAR(100);
ALTER TABLE historial_cambios ADD COLUMN IF NOT EXISTS dni VARCHAR(20);
ALTER TABLE historial_cambios ADD COLUMN IF NOT EXISTS nombre VARCHAR(100);
ALTER TABLE historial_cambios ADD COLUMN IF NOT EXISTS apellido VARCHAR(100);
"""


def crear_tabla_turnos():
    try:
        with connection() as conn:
            cur = conn.cursor()

            cur.execute("SELECT 1 FROM pg_tables WHERE tablename='turnos';")
            if cur.fetchone():
                print("La tabla 'turnos' ya existe.")
            else:
                cur.execute(query_turnos)
                print("Tabla 'turnos' creada correctamente.")

            cur.execute("SELECT 1 FROM pg_tables WHERE tablename='historial_cambios';")
            if cur.fetchone():
                print("La tabla 'historial_cambios' ya existe.")
                cur.execute(migrate_historial)
                print("Migration: columnas agregadas si no existian.")
            else:
                cur.execute(query_historial)
                print("Tabla 'historial_cambios' creada correctamente.")

            conn.commit()
            cur.close()

    except Exception as e:
        print(f"Error al crear las tablas: {e}")


if __name__ == "__main__":
    crear_tabla_turnos()
