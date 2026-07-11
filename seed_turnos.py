import random
from datetime import date, timedelta, datetime
from app.turno_manager import agregar_turno

NOMBRES = [
    "Juan", "Maria", "Carlos", "Ana", "Pedro", "Laura", "Diego", "Sofia",
    "Martin", "Valentina", "Lucas", "Camila", "Mateo", "Isabella", "Santiago",
    "Mia", "Sebastian", "Emma", "Nicolas", "Olivia", "Tomas", "Martina",
    "Benjamin", "Catalina", "Agustin", "Paula", "Facundo", "Josefina",
    "Tobias", "Julieta", "Santino", "Emilia", "Daniel", "Mora", "Alejandro"
]

APELLIDOS = [
    "Garcia", "Lopez", "Martinez", "Rodriguez", "Fernandez", "Gonzalez",
    "Perez", "Sanchez", "Ramirez", "Torres", "Flores", "Rivera",
    "Gomez", "Diaz", "Cruz", "Morales", "Reyes", "Ortiz", "Gutierrez",
    "Chavez", "Ramos", "Ruiz", "Alvarez", "Mendoza", "Castillo"
]

OBRAS_SOCIALES = [
    "OSDE", "Swiss Medical", "Galeno", "Fleming", "Medicus",
    "IOMA", "PAMI", "Ninguna"
]

MOTIVOS = [
    "Consulta general", "Control", "Dolor de espalda", "Fiebre",
    "Chequeo anual", "Resultado de analisis", "Derivacion",
    "Renovacion receta", "Consulta pediatrica", "Ecografia",
    "Control presion arterial", "Vacunacion"
]


def seed():
    horas_manana = [9, 9, 9, 10, 10, 11, 11, 14, 14, 15, 16]
    horas_tarde = [9, 9, 10, 10, 11, 14, 14, 15, 15, 16]

    turnos = []

    for i in range(8):
        h = horas_manana[i]
        m = random.choice([0, 15, 30, 45])
        turnos.append((date.today(), h, m))

    for i in range(10):
        h = horas_tarde[i]
        m = random.choice([0, 15, 30, 45])
        turnos.append((date.today() + timedelta(days=1), h, m))

    for i in range(6):
        h = horas_manana[i]
        m = random.choice([0, 15, 30, 45])
        turnos.append((date.today() + timedelta(days=2), h, m))

    insertados = 0
    for fecha_turno, hora, minuto in turnos:
        nombre = random.choice(NOMBRES)
        apellido = random.choice(APELLIDOS)
        dni = str(random.randint(10000000, 99999999))
        obra_social = random.choice(OBRAS_SOCIALES)
        motivo = random.choice(MOTIVOS)
        dt = datetime(fecha_turno.year, fecha_turno.month, fecha_turno.day, hora, minuto)

        exito, err = agregar_turno(
            nombre, apellido, dni, obra_social, motivo,
            usuario="seed",
            fecha=fecha_turno,
            hora=dt
        )
        if exito:
            insertados += 1
        else:
            print(f"Error: {err}")

    print(f"Se insertaron {insertados} turnos de prueba.")
    print(f"  Hoy: 8 turnos")
    print(f"  Manana: 10 turnos")
    print(f"  Pasado: 6 turnos")


if __name__ == "__main__":
    seed()
