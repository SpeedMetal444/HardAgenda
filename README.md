# HardAgenda - Sistema de Turnos

Sistema de gestion de turnos basado en Python + PyQt6 + FastAPI, disenado para conectarse a bases de datos PostgreSQL. Permite administrar turnos de consulta de manera eficiente, con un historial completo de cambios.

Basado en la estetica y estructura de [InsCar](https://github.com/SpeedMetal444/InsCarProject).

## Caracteristicas

- **Pestana Hoy**: Lista de turnos del dia con el turno actual resaltado
- **Nuevo turno**: Registro rapido con Nombre, Apellido, DNI, Obra Social y Motivo de consulta
- **Todos los turnos**: Busqueda por DNI, nombre o apellido, con menu contextual para ver detalle o eliminar
- **Historial**: Registro completo de altas, bajas y atencion de turnos con usuario y fecha
- **Siguiente turno**: Avance automatico con registro en historial
- **Auto-refresh**: La pantalla de hoy se actualiza cada 60 segundos
- **Server compartido**: Desktop y Android se conectan al mismo servidor FastAPI

## Requisitos

- Python 3.10+
- PostgreSQL instalado y corriendo
- Servidor FastAPI (HardAgendaServer)

## Instalacion

### Desktop (Windows)

1. Descarga la ultima version de `HardAgenda_Setup.exe` desde [Releases](https://github.com/SpeedMetal444/HardAgenda/releases)
2. Ejecuta el instalador
3. Al iniciar la app, ingresa el serial de activacion (si no tenes uno, envia un correo a **abelgodoy.1802@gmail.com**)
4. Ingresa IP y puerto del servidor (ej: `localhost` / `8080`)
5. Marca "Crear base de datos y tablas" en el primer inicio

### Servidor (requerido)

1. Descarga `HardAgendaServer.exe` desde [Releases](https://github.com/SpeedMetal444/HardAgenda/releases)
2. Ejecutalo
3. El servidor escucha en `http://0.0.0.0:8080`
4. Ambas apps (Desktop y Android) se conectan al mismo servidor

### Desde codigo fuente

1. Clona el repositorio:
   ```bash
   git clone https://github.com/SpeedMetal444/HardAgenda.git
   cd HardAgenda
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate       # Windows
   source venv/bin/activate    # Linux/Mac
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecuta la aplicacion:
   ```bash
   python main.py
   ```

5. Para el servidor:
   ```bash
   python server.py
   ```

## Configuracion de la base de datos

La aplicacion necesita conectarse a un servidor PostgreSQL via el servidor FastAPI. Al iniciar por primera vez:

1. Completa los campos de conexion en la pantalla de login:
   - **IP del servidor**: direccion del servidor FastAPI (por defecto: `localhost`)
   - **Puerto del servidor**: puerto del servidor FastAPI (por defecto: `8080`)
   - **Nombre de la base de datos**: nombre de la base a crear/usar (por defecto: `hardagenda_db`)
   - **Usuario de PostgreSQL**: usuario de PostgreSQL con permisos sobre la base
   - **Contrasena de PostgreSQL**: contrasena del usuario
2. Si es la primera vez, marca **Crear base de datos y tablas** para crear todo automaticamente.
3. Opcionalmente, marca **Guardar datos de inicio de sesion** para no tener que reingresar las credenciales cada vez.

> **Nota**: El archivo `config.ini` con las credenciales guardadas esta incluido en `.gitignore` por seguridad. No lo subas al repositorio.

## Sistema de Seriales

El sistema de seriales es **experimental** y **sin fines de lucro**. Si necesitas un serial para activar la app, envia un correo a **abelgodoy.1802@gmail.com** y te proporciono uno.

## Uso

1. Ejecuta el servidor (`HardAgendaServer.exe` o `python server.py`)
2. Abri la app, ingresa el serial de activacion y completa los datos de conexion.
3. Usa las pestanas para realizar acciones:
   - **Hoy**: Visualiza los turnos del dia. El primero aparece resaltado (turno actual). Presiona "Siguiente turno" para avanzar.
   - **Nuevo turno**: Carga los datos de un nuevo turno (Nombre, Apellido, DNI, Obra Social, Motivo de consulta).
   - **Todos los turnos**: Busca turnos por DNI, nombre o apellido. Hace doble clic para ver detalle, o clic derecho para menu contextual (copiar, eliminar).
   - **Historial**: Visualiza el registro de todos los cambios realizados en el sistema.

### Atajos de teclado

| Atajo | Accion |
|-------|--------|
| `Enter` | Buscar (en pestana de busqueda) |
| `Ctrl+N` | Ir a pestana "Nuevo turno" |
| `Escape` | Cerrar ventana dialogo |

## Estructura del proyecto

```
HardAgenda/
├── main.py                 # Login + ventana principal con 5 pestanas
├── server.py               # Servidor FastAPI (compartido con Android)
├── serial_generator.py     # Generador de seriales (solo admin)
├── create_database.py      # Script para crear la DB en PostgreSQL
├── create_tables.py        # Script para crear las tablas
├── requirements.txt        # Dependencias
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── api_client.py       # Cliente HTTP para FastAPI
│   ├── license_validator.py# Validacion de seriales
│   └── turno_manager.py    # Logica de turnos + historial
├── config/
│   ├── __init__.py
│   └── db_config.py        # Conexion a PostgreSQL
└── resources/
    ├── HardAgenda.ico       # Icono de la aplicacion
    └── logo_default_large.png
```

## Tablas de la base de datos

### turnos
| Campo | Tipo | Descripcion |
|-------|------|-------------|
| id | SERIAL PRIMARY KEY | Identificador unico |
| nombre | VARCHAR(100) | Nombre del paciente |
| apellido | VARCHAR(100) | Apellido del paciente |
| dni | VARCHAR(20) | DNI del paciente |
| obra_social | VARCHAR(100) | Obra social |
| motivo_consulta | TEXT | Motivo de la consulta |
| fecha | DATE | Fecha del turno |
| hora | TIMESTAMP | Hora de registro |
| estado | VARCHAR(20) | Estado (pendiente/atendido) |
| usuario | VARCHAR(100) | Usuario que registro el turno |

### historial_cambios
| Campo | Tipo | Descripcion |
|-------|------|-------------|
| id | SERIAL PRIMARY KEY | Identificador unico |
| tabla | VARCHAR(50) | Tabla afectada |
| registro_id | INTEGER | ID del registro |
| accion | VARCHAR(50) | Tipo de accion |
| detalle | TEXT | Detalle del cambio |
| usuario | VARCHAR(100) | Usuario que realizo el cambio |
| fecha | TIMESTAMP | Fecha del cambio |

## Contribuir

1. Hace un fork del repositorio.
2. Crea una rama para tu contribucion: `git checkout -b mi-contribucion`
3. Hace los cambios y commit: `git commit -m "Mi contribucion"`
4. Envias un pull request al repositorio principal.

## Licencia

Este proyecto esta bajo la licencia MIT.
