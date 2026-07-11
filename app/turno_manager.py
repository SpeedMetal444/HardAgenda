import json
from datetime import date, datetime
from app import api_client

MSG_NO_CONEXION = "No se pudo conectar al servidor. Verifique que el servidor FastAPI este corriendo."
MSG_NO_TABLA = "La tabla de turnos no existe. Debe crear la base de datos y tablas desde la pantalla de inicio de sesion."


def _check(resp):
    if resp.get("status") == "error":
        detail = resp.get("detail", "")
        if "does not exist" in detail or "no existe" in detail:
            return None, MSG_NO_TABLA
        return None, detail
    return resp.get("data", resp), None


def crear_base_de_datos():
    resp = api_client.crear_db()
    if resp.get("status") == "error":
        raise Exception(resp.get("detail", "Error al crear base de datos"))


def crear_tablas():
    resp = api_client.crear_tablas()
    if resp.get("status") == "error":
        raise Exception(resp.get("detail", "Error al crear tablas"))


def agregar_turno(nombre, apellido, dni, obra_social, motivo_consulta, usuario=None, fecha=None, hora=None):
    fecha_str = fecha.isoformat() if fecha else None
    hora_str = hora.isoformat() if isinstance(hora, datetime) else (hora.strftime("%H:%M") if hasattr(hora, 'strftime') else None)
    resp = api_client.registrar_turno(
        nombre=nombre, apellido=apellido, dni=dni,
        obra_social=obra_social or None, motivo=motivo_consulta or None,
        fecha=fecha_str, hora=hora_str, usuario=usuario
    )
    if resp.get("status") == "error":
        detail = resp.get("detail", "")
        if "does not exist" in detail or "no existe" in detail:
            return False, MSG_NO_TABLA
        return False, f"Error al registrar turno: {detail}"
    return True, None


def obtener_turnos_del_dia(fecha_date=None):
    data, err = _check(api_client.turnos_hoy())
    if err:
        if "does not exist" in err or "no existe" in err:
            return [], MSG_NO_TABLA
        return [], err
    turnos = []
    for t in data:
        turnos.append({
            "id": t["id"],
            "nombre": t["nombre"],
            "apellido": t["apellido"],
            "dni": t["dni"],
            "obra_social": t.get("obra_social"),
            "motivo_consulta": t.get("motivo_consulta"),
            "fecha": date.fromisoformat(t["fecha"]) if t.get("fecha") else None,
            "hora": datetime.fromisoformat(t["hora"]) if t.get("hora") else None,
            "estado": t.get("estado", "pendiente"),
            "usuario": t.get("usuario"),
        })
    return turnos, None


def obtener_todos_los_turnos():
    data, err = _check(api_client.turnos_todos())
    if err:
        if "does not exist" in err or "no existe" in err:
            return [], MSG_NO_TABLA
        return [], err
    turnos = []
    for t in data:
        turnos.append({
            "id": t["id"],
            "nombre": t["nombre"],
            "apellido": t["apellido"],
            "dni": t["dni"],
            "obra_social": t.get("obra_social"),
            "motivo_consulta": t.get("motivo_consulta"),
            "fecha": date.fromisoformat(t["fecha"]) if t.get("fecha") else None,
            "hora": datetime.fromisoformat(t["hora"]) if t.get("hora") else None,
            "estado": t.get("estado", "pendiente"),
            "usuario": t.get("usuario"),
        })
    return turnos, None


def buscar_turnos(dni=None, nombre=None, apellido=None):
    data, err = _check(api_client.buscar_turnos(dni=dni, nombre=nombre, apellido=apellido))
    if err:
        return [], err
    turnos = []
    for t in data:
        turnos.append({
            "id": t["id"],
            "nombre": t["nombre"],
            "apellido": t["apellido"],
            "dni": t["dni"],
            "obra_social": t.get("obra_social"),
            "motivo_consulta": t.get("motivo_consulta"),
            "fecha": date.fromisoformat(t["fecha"]) if t.get("fecha") else None,
            "hora": datetime.fromisoformat(t["hora"]) if t.get("hora") else None,
            "estado": t.get("estado", "pendiente"),
            "usuario": t.get("usuario"),
        })
    return turnos, None


def eliminar_turno(turno_id):
    resp = api_client.eliminar_turno(turno_id)
    if resp.get("status") == "error":
        return False, f"Error al eliminar turno: {resp.get('detail', '')}"
    return True, None


def editar_turno(turno_id, nombre, apellido, dni, obra_social, motivo_consulta, fecha, hora):
    fecha_str = fecha.isoformat() if fecha else None
    hora_str = hora.isoformat() if isinstance(hora, datetime) else None
    resp = api_client.editar_turno(
        turno_id=turno_id, nombre=nombre, apellido=apellido, dni=dni,
        obra_social=obra_social or None, motivo=motivo_consulta or None,
        fecha=fecha_str, hora=hora_str
    )
    if resp.get("status") == "error":
        return False, f"Error al editar turno: {resp.get('detail', '')}"
    return True, None


def reprogramar_turno(turno_id, nueva_fecha, nueva_hora):
    fecha_str = nueva_fecha.isoformat() if nueva_fecha else None
    hora_str = nueva_hora.isoformat() if isinstance(nueva_hora, datetime) else None
    resp = api_client.reprogramar_turno(turno_id=turno_id, fecha=fecha_str, hora=hora_str)
    if resp.get("status") == "error":
        return False, f"Error al reprogramar turno: {resp.get('detail', '')}"
    return True, None


def avanzar_turno(turno_id):
    resp = api_client.avanzar_turno(turno_id)
    if resp.get("status") == "error":
        return False, f"Error al avanzar turno: {resp.get('detail', '')}"
    return True, None


def registrar_cambio(tabla, registro_id, accion, detalle, usuario=None, dni=None, nombre=None, apellido=None):
    resp = api_client.registrar_historial(
        tabla=tabla, registro_id=registro_id, accion=accion,
        detalle=detalle, usuario=usuario, dni=dni, nombre=nombre, apellido=apellido
    )
    if resp.get("status") == "error":
        return False, f"Error al registrar cambio: {resp.get('detail', '')}"
    return True, None


def obtener_historial():
    data, err = _check(api_client.historial())
    if err:
        if "does not exist" in err or "no existe" in err:
            return [], MSG_NO_TABLA
        return [], err
    registros = []
    for r in data:
        registros.append({
            "id": r["id"],
            "tabla": r.get("tabla"),
            "registro_id": r.get("registro_id"),
            "accion": r["accion"],
            "detalle": r.get("detalle"),
            "usuario": r.get("usuario"),
            "dni": r.get("dni"),
            "nombre": r.get("nombre"),
            "apellido": r.get("apellido"),
            "fecha": datetime.fromisoformat(r["fecha"]) if r.get("fecha") else None,
            "motivo_consulta": r.get("motivo_consulta"),
        })
    return registros, None
