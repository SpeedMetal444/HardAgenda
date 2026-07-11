"""
HardAgenda - Servidor API (FastAPI)
Ejecutar: uvicorn server:app --host 0.0.0.0 --port 8080 --reload
"""
import os
import configparser
import traceback
from datetime import date, datetime
from typing import Optional

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql

from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

CONFIG_PATH = os.path.join(os.path.expandvars('%APPDATA%'), 'HardAgenda', 'config.ini')

app = FastAPI(title="HardAgenda API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def safe_str(e):
    try:
        s = str(e)
        if isinstance(s, bytes):
            return s.decode('utf-8', errors='replace')
        return s
    except Exception:
        try:
            return repr(e)
        except Exception:
            return "Error desconocido"


def get_base_config():
    if os.path.exists(CONFIG_PATH):
        config = configparser.ConfigParser()
        for enc in ('utf-8-sig', 'latin-1', 'cp1252'):
            try:
                config.read(CONFIG_PATH, encoding=enc)
                break
            except UnicodeDecodeError:
                config = configparser.ConfigParser()
        if config.has_section('database'):
            return {
                'user': config.get('database', 'user', fallback=''),
                'password': config.get('database', 'password', fallback=''),
                'host': config.get('database', 'host', fallback='localhost'),
                'port': config.get('database', 'port', fallback='5432'),
            }
    return {}


def get_db_config(x_db_user: str = "", x_db_pass: str = "", x_db_name: str = "hardagenda_db"):
    base = get_base_config()
    return {
        'dbname': x_db_name or base.get('dbname', 'hardagenda_db'),
        'user': x_db_user or base.get('user', 'postgres'),
        'password': x_db_pass if x_db_pass else base.get('password', ''),
        'host': base.get('host', 'localhost'),
        'port': base.get('port', '5432'),
    }


def connect_db(cfg):
    return psycopg2.connect(**cfg)


def row_to_dict(cursor, row):
    if row is None:
        return None
    cols = [d[0] for d in cursor.description]
    d = {}
    for i, col in enumerate(cols):
        val = row[i]
        if isinstance(val, (date, datetime)):
            val = val.isoformat()
        d[col] = val
    return d


def rows_to_list(cursor, rows):
    return [row_to_dict(cursor, r) for r in rows]


def db_headers(x_db_user: str = Header(""), x_db_pass: str = Header(""), x_db_name: str = Header("hardagenda_db")):
    return get_db_config(x_db_user, x_db_pass, x_db_name)


@app.get("/api/ping")
def ping():
    return {"status": "ok"}


@app.get("/api/test")
def test_connection(cfg: dict = Depends(db_headers)):
    try:
        conn = connect_db(cfg)
        conn.close()
        return {"status": "ok", "message": "Conexion exitosa"}
    except Exception as e:
        msg = safe_str(e)
        if "does not exist" in msg or "no existe" in msg:
            raise HTTPException(status_code=400, detail="La base de datos no existe. Crea la base de datos primero.")
        if "fehler" in msg.lower() or "password" in msg.lower() or "auth" in msg.lower():
            raise HTTPException(status_code=400, detail="Usuario o contrasena incorrectos.")
        if "connection refused" in msg.lower() or "connect" in msg.lower():
            raise HTTPException(status_code=400, detail="No se pudo conectar a PostgreSQL. Verifica que este corriendo.")
        raise HTTPException(status_code=400, detail="Verifica los datos de conexion.")


@app.get("/api/crear_db")
def crear_db(cfg: dict = Depends(db_headers)):
    try:
        dbname = cfg['dbname'].strip()
        if not dbname:
            raise HTTPException(status_code=400, detail="Nombre de base de datos vacio")
        conn = psycopg2.connect(
            dbname='postgres', user=cfg['user'], password=cfg['password'],
            host=cfg['host'], port=cfg['port']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname=%s;", (dbname,))
        if not cur.fetchone():
            safe_name = dbname.replace('"', '""')
            cur.execute(f'CREATE DATABASE "{safe_name}"')
        cur.close()
        conn.close()
        return {"status": "ok", "message": "Base de datos creada/verificada"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=safe_str(e))


@app.get("/api/crear_tablas")
def crear_tablas(cfg: dict = Depends(db_headers)):
    try:
        conn = connect_db(cfg)
        cur = conn.cursor()
        cur.execute("""
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
            )
        """)
        cur.execute("""
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
            )
        """)
        for col in ['usuario', 'dni', 'nombre', 'apellido']:
            cur.execute(f"ALTER TABLE historial_cambios ADD COLUMN IF NOT EXISTS {col} VARCHAR(100)")
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "ok", "message": "Tablas creadas/verificadas"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=safe_str(e))


@app.get("/api/turnos/hoy")
def turnos_hoy(cfg: dict = Depends(db_headers)):
    try:
        conn = connect_db(cfg)
        cur = conn.cursor()
        cur.execute("SELECT * FROM turnos WHERE fecha = %s ORDER BY hora ASC", (date.today(),))
        rows = rows_to_list(cur, cur.fetchall())
        cur.close()
        conn.close()
        return {"status": "ok", "data": rows}
    except Exception as e:
        raise HTTPException(status_code=400, detail=safe_str(e))


@app.get("/api/turnos/todos")
def turnos_todos(cfg: dict = Depends(db_headers)):
    try:
        conn = connect_db(cfg)
        cur = conn.cursor()
        cur.execute("SELECT * FROM turnos ORDER BY fecha DESC, hora DESC")
        rows = rows_to_list(cur, cur.fetchall())
        cur.close()
        conn.close()
        return {"status": "ok", "data": rows}
    except Exception as e:
        raise HTTPException(status_code=400, detail=safe_str(e))


@app.get("/api/historial")
def historial(cfg: dict = Depends(db_headers)):
    try:
        conn = connect_db(cfg)
        cur = conn.cursor()
        cur.execute("""
            SELECT h.id, h.tabla, h.registro_id, h.accion, h.detalle, h.usuario,
                   h.dni, h.nombre, h.apellido, h.fecha, t.motivo_consulta
            FROM historial_cambios h
            LEFT JOIN turnos t ON h.tabla = 'turnos' AND h.registro_id = t.id
            ORDER BY h.fecha DESC LIMIT 200
        """)
        rows = []
        cols = [d[0] for d in cur.description]
        for row in cur.fetchall():
            d = {}
            for i, col in enumerate(cols):
                val = row[i]
                if isinstance(val, (date, datetime)):
                    val = val.isoformat()
                d[col] = val
            rows.append(d)
        cur.close()
        conn.close()
        return {"status": "ok", "data": rows}
    except Exception as e:
        raise HTTPException(status_code=400, detail=safe_str(e))


class BuscarRequest(BaseModel):
    dni: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None


@app.post("/api/turnos/buscar")
def buscar_turnos(body: BuscarRequest, cfg: dict = Depends(db_headers)):
    try:
        conditions = []
        params = []
        if body.dni:
            conditions.append("dni ILIKE %s")
            params.append(f"%{body.dni}%")
        if body.nombre:
            conditions.append("nombre ILIKE %s")
            params.append(f"%{body.nombre}%")
        if body.apellido:
            conditions.append("apellido ILIKE %s")
            params.append(f"%{body.apellido}%")
        if not conditions:
            raise HTTPException(status_code=400, detail="Ingrese al menos un criterio")
        where = " AND ".join(conditions)
        conn = connect_db(cfg)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM turnos WHERE {where} ORDER BY fecha DESC, hora DESC", params)
        rows = rows_to_list(cur, cur.fetchall())
        cur.close()
        conn.close()
        return {"status": "ok", "data": rows}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=safe_str(e))


class RegistrarTurnoRequest(BaseModel):
    nombre: str
    apellido: str
    dni: str
    obra_social: Optional[str] = None
    motivo: Optional[str] = None
    fecha: Optional[str] = None
    hora: Optional[str] = None
    usuario: Optional[str] = None


@app.post("/api/turnos/registrar")
def registrar_turno(body: RegistrarTurnoRequest, cfg: dict = Depends(db_headers)):
    try:
        conn = connect_db(cfg)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO turnos (nombre, apellido, dni, obra_social, motivo_consulta, fecha, hora, usuario)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            body.nombre, body.apellido, body.dni,
            body.obra_social, body.motivo, body.fecha, body.hora, body.usuario
        ))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "ok", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=safe_str(e))


class IdRequest(BaseModel):
    id: int


@app.post("/api/turnos/avanzar")
def avanzar_turno(body: IdRequest, cfg: dict = Depends(db_headers)):
    try:
        conn = connect_db(cfg)
        cur = conn.cursor()
        cur.execute("UPDATE turnos SET estado='atendido' WHERE id=%s", (body.id,))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=safe_str(e))


class EditarTurnoRequest(BaseModel):
    id: int
    nombre: str
    apellido: str
    dni: str
    obra_social: Optional[str] = None
    motivo: Optional[str] = None
    fecha: Optional[str] = None
    hora: Optional[str] = None


@app.post("/api/turnos/editar")
def editar_turno(body: EditarTurnoRequest, cfg: dict = Depends(db_headers)):
    try:
        conn = connect_db(cfg)
        cur = conn.cursor()
        cur.execute("""
            UPDATE turnos SET nombre=%s, apellido=%s, dni=%s, obra_social=%s,
            motivo_consulta=%s, fecha=%s, hora=%s WHERE id=%s
        """, (
            body.nombre, body.apellido, body.dni,
            body.obra_social, body.motivo, body.fecha, body.hora, body.id
        ))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=safe_str(e))


class ReprogramarRequest(BaseModel):
    id: int
    fecha: str
    hora: str


@app.post("/api/turnos/reprogramar")
def reprogramar_turno(body: ReprogramarRequest, cfg: dict = Depends(db_headers)):
    try:
        conn = connect_db(cfg)
        cur = conn.cursor()
        cur.execute("""
            UPDATE turnos SET fecha=%s, hora=%s, estado='pendiente' WHERE id=%s
        """, (body.fecha, body.hora, body.id))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=safe_str(e))


@app.post("/api/turnos/eliminar")
def eliminar_turno(body: IdRequest, cfg: dict = Depends(db_headers)):
    try:
        conn = connect_db(cfg)
        cur = conn.cursor()
        cur.execute("DELETE FROM turnos WHERE id=%s", (body.id,))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=safe_str(e))


class HistorialRequest(BaseModel):
    tabla: Optional[str] = None
    registro_id: Optional[int] = None
    accion: str
    detalle: Optional[str] = None
    usuario: Optional[str] = None
    dni: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None


@app.post("/api/historial/registrar")
def registrar_historial(body: HistorialRequest, cfg: dict = Depends(db_headers)):
    try:
        conn = connect_db(cfg)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO historial_cambios (tabla, registro_id, accion, detalle, usuario, dni, nombre, apellido)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            body.tabla, body.registro_id, body.accion,
            body.detalle, body.usuario, body.dni, body.nombre, body.apellido
        ))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=safe_str(e))


if __name__ == '__main__':
    import uvicorn
    print("HardAgenda Server corriendo en http://0.0.0.0:8080")
    print("Documentacion API: http://localhost:8080/docs")
    print("Presiona Ctrl+C para detener")
    uvicorn.run(app, host="0.0.0.0", port=8080)
