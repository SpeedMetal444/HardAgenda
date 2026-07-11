import psycopg2
import configparser
import os
import sys
import shutil
from contextlib import contextmanager

APP_NAME = "HardAgenda"


def _get_internal_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), '_internal')
    return os.path.dirname(os.path.dirname(__file__))


def _get_user_config_path():
    config_dir = os.path.join(os.path.expandvars('%APPDATA%'), APP_NAME)
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, 'config.ini')


def _ensure_user_config():
    user_path = _get_user_config_path()
    if not os.path.exists(user_path):
        default_path = os.path.join(_get_internal_path(), 'config.ini')
        if os.path.exists(default_path):
            shutil.copy2(default_path, user_path)
    return user_path


def _read_config():
    config = configparser.ConfigParser()
    config_file_path = _ensure_user_config()
    config.read(config_file_path, encoding='utf-8')

    if not config.sections():
        return None

    return {
        "dbname": config.get("database", "database"),
        "user": config.get("database", "user"),
        "password": config.get("database", "password"),
        "host": config.get("database", "host"),
        "port": config.get("database", "port"),
    }


def get_connection():
    params = _read_config()
    if not params:
        return None
    try:
        return psycopg2.connect(**params)
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None


@contextmanager
def connection():
    params = _read_config()
    if not params:
        raise psycopg2.OperationalError("No se pudo leer la configuracion de la base de datos")

    conn = psycopg2.connect(**params)
    try:
        yield conn
    finally:
        conn.close()
