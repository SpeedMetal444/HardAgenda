import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql
import configparser
import os
import sys


def _get_internal_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), '_internal')
    return os.path.dirname(__file__)


def _read_config():
    config = configparser.ConfigParser()
    config_file_path = os.path.join(os.path.expandvars('%APPDATA%'), 'HardAgenda', 'config.ini')
    config.read(config_file_path, encoding='utf-8')
    return config


config = _read_config()
DB_NAME = config.get('database', 'database')
DB_USER = config.get('database', 'user')
DB_PASSWORD = config.get('database', 'password')
DB_HOST = config.get('database', 'host')
DB_PORT = config.get('database', 'port')


def crear_base_de_datos():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s;", (DB_NAME,))
        existe = cursor.fetchone()

        if not existe:
            cursor.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(DB_NAME)))
            print(f"Base de datos '{DB_NAME}' creada exitosamente.")
        else:
            print(f"La base de datos '{DB_NAME}' ya existe.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error creando la base de datos: {e}")


if __name__ == "__main__":
    crear_base_de_datos()
