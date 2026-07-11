import json
import urllib.request
import urllib.error
import urllib.parse
import configparser
import os
import sys

APP_NAME = "HardAgenda"


def _get_user_config_path():
    config_dir = os.path.join(os.path.expandvars('%APPDATA%'), APP_NAME)
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, 'config.ini')


def _read_config():
    config = configparser.ConfigParser()
    config.read(_get_user_config_path(), encoding='utf-8')
    if not config.has_section('database'):
        return None
    return {
        "server_url": config.get("database", "server_url", fallback=""),
        "dbname": config.get("database", "database", fallback="hardagenda_db"),
        "user": config.get("database", "user", fallback=""),
        "password": config.get("database", "password", fallback=""),
        "host": config.get("database", "host", fallback="localhost"),
        "port": config.get("database", "port", fallback="5432"),
    }


_server_url = ""
_db_headers = {}


def configure(server_url, dbname, user, password):
    global _server_url, _db_headers
    _server_url = server_url.rstrip('/')
    _db_headers = {
        "X-DB-User": user,
        "X-DB-Pass": password,
        "X-DB-Name": dbname,
    }


def configure_from_config():
    cfg = _read_config()
    if cfg and cfg.get("server_url"):
        configure(cfg["server_url"], cfg["dbname"], cfg["user"], cfg["password"])
        return True
    return False


def _decode_response(resp):
    raw = resp.read()
    try:
        return json.loads(raw.decode('utf-8', errors='replace'))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _decode_error(e):
    raw = e.read()
    try:
        body = raw.decode('utf-8', errors='replace')
        parsed = json.loads(body)
        return parsed.get("detail", str(body))
    except (json.JSONDecodeError, ValueError):
        return f"Error HTTP {e.code}: la base de datos no existe o no esta disponible"


def _get(url):
    req = urllib.request.Request(url)
    for k, v in _db_headers.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = _decode_response(resp)
            if data is None:
                return {"status": "error", "detail": "Respuesta no decodificable del servidor"}
            return data
    except urllib.error.HTTPError as e:
        return {"status": "error", "detail": _decode_error(e)}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _post(url, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    for k, v in _db_headers.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = _decode_response(resp)
            if data is None:
                return {"status": "error", "detail": "Respuesta no decodificable del servidor"}
            return data
    except urllib.error.HTTPError as e:
        return {"status": "error", "detail": _decode_error(e)}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def ping():
    return _get(f"{_server_url}/api/ping")


def test_connection():
    return _get(f"{_server_url}/api/test")


def crear_db():
    return _get(f"{_server_url}/api/crear_db")


def crear_tablas():
    return _get(f"{_server_url}/api/crear_tablas")


def turnos_hoy():
    return _get(f"{_server_url}/api/turnos/hoy")


def turnos_todos():
    return _get(f"{_server_url}/api/turnos/todos")


def historial():
    return _get(f"{_server_url}/api/historial")


def buscar_turnos(dni=None, nombre=None, apellido=None):
    return _post(f"{_server_url}/api/turnos/buscar", {
        "dni": dni, "nombre": nombre, "apellido": apellido
    })


def registrar_turno(nombre, apellido, dni, obra_social=None, motivo=None,
                    fecha=None, hora=None, usuario=None):
    return _post(f"{_server_url}/api/turnos/registrar", {
        "nombre": nombre, "apellido": apellido, "dni": dni,
        "obra_social": obra_social, "motivo": motivo,
        "fecha": fecha, "hora": hora, "usuario": usuario
    })


def avanzar_turno(turno_id):
    return _post(f"{_server_url}/api/turnos/avanzar", {"id": turno_id})


def editar_turno(turno_id, nombre, apellido, dni, obra_social=None,
                 motivo=None, fecha=None, hora=None):
    return _post(f"{_server_url}/api/turnos/editar", {
        "id": turno_id, "nombre": nombre, "apellido": apellido, "dni": dni,
        "obra_social": obra_social, "motivo": motivo,
        "fecha": fecha, "hora": hora
    })


def reprogramar_turno(turno_id, fecha, hora):
    return _post(f"{_server_url}/api/turnos/reprogramar", {
        "id": turno_id, "fecha": fecha, "hora": hora
    })


def eliminar_turno(turno_id):
    return _post(f"{_server_url}/api/turnos/eliminar", {"id": turno_id})


def registrar_historial(tabla=None, registro_id=None, accion="",
                        detalle=None, usuario=None, dni=None,
                        nombre=None, apellido=None):
    return _post(f"{_server_url}/api/historial/registrar", {
        "tabla": tabla, "registro_id": registro_id, "accion": accion,
        "detalle": detalle, "usuario": usuario, "dni": dni,
        "nombre": nombre, "apellido": apellido
    })
