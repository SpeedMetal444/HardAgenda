import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql
from config.db_config import connection
from datetime import date, datetime

MSG_NO_CONEXION = "No se pudo conectar a la base de datos. Verifique que exista y las credenciales sean correctas."
MSG_NO_TABLA = "La tabla de turnos no existe. Debe crear la tabla desde la pantalla de inicio de sesion."

_DB_ERRORS = (psycopg2.OperationalError, UnicodeDecodeError, psycopg2.InterfaceError)


def crear_base_de_datos():
    from config.db_config import _read_config
    params = _read_config()
    conn = psycopg2.connect(
        dbname="postgres",
        user=params["user"],
        password=params["password"],
        host=params["host"],
        port=params["port"]
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s;", (params["dbname"],))
    if not cur.fetchone():
        cur.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(params["dbname"])))
    cur.close()
    conn.close()


QUERY_TURNOS = """
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

QUERY_HISTORIAL = """
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

MIGRATE_HISTORIAL = """
ALTER TABLE historial_cambios ADD COLUMN IF NOT EXISTS usuario VARCHAR(100);
ALTER TABLE historial_cambios ADD COLUMN IF NOT EXISTS dni VARCHAR(20);
ALTER TABLE historial_cambios ADD COLUMN IF NOT EXISTS nombre VARCHAR(100);
ALTER TABLE historial_cambios ADD COLUMN IF NOT EXISTS apellido VARCHAR(100);
"""


def crear_tablas():
    with connection() as conn:
        cur = conn.cursor()
        cur.execute(QUERY_TURNOS)
        cur.execute(QUERY_HISTORIAL)
        cur.execute(MIGRATE_HISTORIAL)
        conn.commit()
        cur.close()


def _row_to_dict(row):
    if not row:
        return None
    return {
        "id": row[0],
        "nombre": row[1],
        "apellido": row[2],
        "dni": row[3],
        "obra_social": row[4],
        "motivo_consulta": row[5],
        "fecha": row[6],
        "hora": row[7],
        "estado": row[8],
        "usuario": row[9],
    }


def agregar_turno(nombre, apellido, dni, obra_social, motivo_consulta, usuario=None):
    try:
        with connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO turnos (nombre, apellido, dni, obra_social, motivo_consulta, usuario)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (nombre, apellido, dni, obra_social, motivo_consulta, usuario))
            conn.commit()
            cur.close()
            return True, None

    except _DB_ERRORS:
        return False, MSG_NO_CONEXION
    except psycopg2.errors.UndefinedTable:
        return False, MSG_NO_TABLA
    except Exception as e:
        return False, f"Error al registrar turno: {e}"


def obtener_turnos_del_dia(fecha_date=None):
    try:
        if fecha_date is None:
            fecha_date = date.today()
        with connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM turnos
                WHERE fecha = %s
                ORDER BY hora ASC
            """, (fecha_date,))
            rows = cur.fetchall()
            cur.close()
            return [_row_to_dict(r) for r in rows], None

    except _DB_ERRORS:
        return [], MSG_NO_CONEXION
    except psycopg2.errors.UndefinedTable:
        return [], MSG_NO_TABLA
    except Exception as e:
        return [], f"Error al obtener turnos: {e}"


def obtener_todos_los_turnos():
    try:
        with connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM turnos ORDER BY fecha DESC, hora DESC")
            rows = cur.fetchall()
            cur.close()
            return [_row_to_dict(r) for r in rows], None

    except _DB_ERRORS:
        return [], MSG_NO_CONEXION
    except psycopg2.errors.UndefinedTable:
        return [], MSG_NO_TABLA
    except Exception as e:
        return [], f"Error al obtener turnos: {e}"


def buscar_turnos(dni=None, nombre=None, apellido=None):
    try:
        with connection() as conn:
            cur = conn.cursor()
            condiciones = []
            parametros = []

            if dni:
                condiciones.append("dni ILIKE %s")
                parametros.append(f"%{dni}%")
            if nombre:
                condiciones.append("nombre ILIKE %s")
                parametros.append(f"%{nombre}%")
            if apellido:
                condiciones.append("apellido ILIKE %s")
                parametros.append(f"%{apellido}%")

            if not condiciones:
                return [], "Debe ingresar al menos un criterio de busqueda"

            where = " AND ".join(condiciones)
            cur.execute(f"SELECT * FROM turnos WHERE {where} ORDER BY fecha DESC, hora DESC", parametros)
            rows = cur.fetchall()
            cur.close()
            return [_row_to_dict(r) for r in rows], None

    except _DB_ERRORS:
        return [], MSG_NO_CONEXION
    except psycopg2.errors.UndefinedTable:
        return [], MSG_NO_TABLA
    except Exception as e:
        return [], f"Error al buscar turnos: {e}"


def eliminar_turno(turno_id):
    try:
        with connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM turnos WHERE id = %s", (turno_id,))
            conn.commit()
            cur.close()
            return True, None

    except _DB_ERRORS:
        return False, MSG_NO_CONEXION
    except psycopg2.errors.UndefinedTable:
        return False, MSG_NO_TABLA
    except Exception as e:
        return False, f"Error al eliminar turno: {e}"


def avanzar_turno(turno_id):
    try:
        with connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE turnos SET estado = 'atendido'
                WHERE id = %s
            """, (turno_id,))
            conn.commit()
            cur.close()
            return True, None

    except _DB_ERRORS:
        return False, MSG_NO_CONEXION
    except psycopg2.errors.UndefinedTable:
        return False, MSG_NO_TABLA
    except Exception as e:
        return False, f"Error al avanzar turno: {e}"


def registrar_cambio(tabla, registro_id, accion, detalle, usuario=None, dni=None, nombre=None, apellido=None):
    try:
        with connection() as conn:
            cur = conn.cursor()
            try:
                cur.execute("""
                    INSERT INTO historial_cambios (tabla, registro_id, accion, detalle, usuario, dni, nombre, apellido)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (tabla, registro_id, accion, detalle, usuario, dni, nombre, apellido))
            except psycopg2.errors.UndefinedColumn:
                conn.rollback()
                cur.execute("""
                    INSERT INTO historial_cambios (tabla, registro_id, accion, detalle, usuario)
                    VALUES (%s, %s, %s, %s, %s)
                """, (tabla, registro_id, accion, detalle, usuario))
            conn.commit()
            cur.close()
            return True, None
    except _DB_ERRORS:
        return False, MSG_NO_CONEXION
    except Exception as e:
        return False, f"Error al registrar cambio: {e}"


def obtener_historial():
    try:
        with connection() as conn:
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT id, tabla, registro_id, accion, detalle, usuario, dni, nombre, apellido, fecha
                    FROM historial_cambios
                    ORDER BY fecha DESC
                    LIMIT 200
                """)
            except psycopg2.errors.UndefinedColumn:
                conn.rollback()
                cur.execute("""
                    SELECT id, tabla, registro_id, accion, detalle,
                           NULL as usuario, NULL as dni, NULL as nombre, NULL as apellido, fecha
                    FROM historial_cambios
                    ORDER BY fecha DESC
                    LIMIT 200
                """)
            registros = cur.fetchall()
            cur.close()
            return [_row_to_dict_historial(r) for r in registros], None
    except _DB_ERRORS:
        return [], MSG_NO_CONEXION
    except psycopg2.errors.UndefinedTable:
        return [], MSG_NO_TABLA
    except Exception as e:
        return [], f"Error al obtener historial: {e}"


def _row_to_dict_historial(row):
    if not row:
        return None
    return {
        "id": row[0],
        "tabla": row[1],
        "registro_id": row[2],
        "accion": row[3],
        "detalle": row[4],
        "usuario": row[5],
        "dni": row[6],
        "nombre": row[7],
        "apellido": row[8],
        "fecha": row[9],
    }
