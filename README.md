# HardAgenda - Sistema de Turnos

Sistema de gestión de turnos basado en Python + PyQt6 + FastAPI, diseñado para conectarse a bases de datos PostgreSQL. Permite administrar turnos de consulta de manera eficiente, con un historial completo de cambios.

## Características

- **Pestaña Hoy**: Lista de turnos del día con el turno actual resaltado
- **Nuevo turno**: Registro rápido con Nombre, Apellido, DNI, Obra Social y Motivo de consulta
- **Todos los turnos**: Búsqueda por DNI, nombre o apellido, con menú contextual para ver detalle o eliminar
- **Historial**: Registro completo de altas, bajas y atención de turnos con usuario y fecha
- **Siguiente turno**: Avance automático con registro en historial
- **Auto-refresh**: La pantalla de hoy se actualiza cada 60 segundos
- **Servidor compartido**: Desktop y Android se conectan al mismo servidor FastAPI

## Requisitos

- Python 3.10+
- PostgreSQL instalado y corriendo
- Servidor FastAPI (HardAgendaServer)

## Instalación

### Desktop (Windows)

1. Descargá la última versión de `HardAgenda_Setup.exe` desde [Releases](https://github.com/SpeedMetal444/HardAgenda/releases)
2. Ejecutá el instalador
3. Ingresá IP y puerto del servidor (ej: `localhost` / `8080`)
4. Marcá "Crear base de datos y tablas" en el primer inicio

### Servidor (requerido)

1. Descargá `HardAgendaServer.exe` desde [Releases](https://github.com/SpeedMetal444/HardAgenda/releases)
2. Ejecutalo
3. El servidor escucha en `http://0.0.0.0:8080`
4. Ambas apps (Desktop y Android) se conectan al mismo servidor

### Desde código fuente

1. Cloná el repositorio:
   ```bash
   git clone https://github.com/SpeedMetal444/HardAgenda.git
   cd HardAgenda
   ```

2. Creá y activá un entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate       # Windows
   source venv/bin/activate    # Linux/Mac
   ```

3. Instalá las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecutá la aplicación:
   ```bash
   python main.py
   ```

5. Para el servidor:
   ```bash
   python server.py
   ```

## Configuración de la base de datos

La aplicación necesita conectarse a un servidor PostgreSQL vía el servidor FastAPI. Al iniciar por primera vez:

1. Completá los campos de conexión en la pantalla de login:
   - **IP del servidor**: dirección del servidor FastAPI (por defecto: `localhost`)
   - **Puerto del servidor**: puerto del servidor FastAPI (por defecto: `8080`)
   - **Nombre de la base de datos**: nombre de la base a crear/usar (por defecto: `hardagenda_db`)
   - **Usuario de PostgreSQL**: usuario de PostgreSQL con permisos sobre la base
   - **Contraseña de PostgreSQL**: contraseña del usuario
2. Si es la primera vez, marcá **Crear base de datos y tablas** para crear todo automáticamente.
3. Opcionalmente, marcá **Guardar datos de inicio de sesión** para no tener que reingresar las credenciales cada vez.

> **Nota**: El archivo `config.ini` con las credenciales guardadas está incluido en `.gitignore` por seguridad. No lo subas al repositorio.

## Uso

1. Ejecutá el servidor (`HardAgendaServer.exe` o `python server.py`)
2. Abrí la app y completá los datos de conexión.
3. Usá las pestañas para realizar acciones:
   - **Hoy**: Visualizá los turnos del día. El primero aparece resaltado (turno actual). Presioná "Siguiente turno" para avanzar.
   - **Nuevo turno**: Cargá los datos de un nuevo turno (Nombre, Apellido, DNI, Obra Social, Motivo de consulta).
   - **Todos los turnos**: Buscá turnos por DNI, nombre o apellido. Hacé doble clic para ver detalle, o clic derecho para menú contextual (copiar, eliminar).
   - **Historial**: Visualizá el registro de todos los cambios realizados en el sistema.

### Atajos de teclado

| Atajo | Acción |
|-------|--------|
| `Enter` | Buscar (en pestaña de búsqueda) |
| `Ctrl+N` | Ir a pestaña "Nuevo turno" |
| `Escape` | Cerrar ventana diálogo |

## Estructura del proyecto

```
HardAgenda/
├── main.py                 # Login + ventana principal con 5 pestañas
├── server.py               # Servidor FastAPI (compartido con Android)
├── create_database.py      # Script para crear la DB en PostgreSQL
├── create_tables.py        # Script para crear las tablas
├── requirements.txt        # Dependencias
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── api_client.py       # Cliente HTTP para FastAPI
│   └── turno_manager.py    # Lógica de turnos + historial
├── config/
│   ├── __init__.py
│   └── db_config.py        # Conexión a PostgreSQL
└── resources/
    ├── HardAgenda.ico       # Icono de la aplicación
    └── logo_default_large.png
```

## Tablas de la base de datos

### turnos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | SERIAL PRIMARY KEY | Identificador único |
| nombre | VARCHAR(100) | Nombre del paciente |
| apellido | VARCHAR(100) | Apellido del paciente |
| dni | VARCHAR(20) | DNI del paciente |
| obra_social | VARCHAR(100) | Obra social |
| motivo_consulta | TEXT | Motivo de la consulta |
| fecha | DATE | Fecha del turno |
| hora | TIMESTAMP | Hora de registro |
| estado | VARCHAR(20) | Estado (pendiente/atendido) |
| usuario | VARCHAR(100) | Usuario que registró el turno |

### historial_cambios
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | SERIAL PRIMARY KEY | Identificador único |
| tabla | VARCHAR(50) | Tabla afectada |
| registro_id | INTEGER | ID del registro |
| accion | VARCHAR(50) | Tipo de acción |
| detalle | TEXT | Detalle del cambio |
| usuario | VARCHAR(100) | Usuario que realizó el cambio |
| fecha | TIMESTAMP | Fecha del cambio |

## Notas

- El sistema incluye validación de licencia para uso en producción. Para desarrollo local, ejecutá `python main.py` directamente desde el código fuente.
- Si necesitás un serial para testing, contactame por email.

## Contribuir

1. Hacé un fork del repositorio.
2. Creá una rama para tu contribución: `git checkout -b mi-contribucion`
3. Hacé los cambios y commit: `git commit -m "Mi contribución"`
4. Enviá un pull request al repositorio principal.

## Licencia

Este proyecto está bajo la licencia MIT.