import hashlib
import secrets
import string
import os

SECRET = "HardAgenda2026!x7Kp"
SERIALS_FILE = "SERIALS.txt"


def _serial_from_counter(i):
    raw = f"{SECRET}-{i:06d}"
    h = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return f"{h[0:4].upper()}-{h[4:8].upper()}-{h[8:12].upper()}"


def generate_serial(index):
    return _serial_from_counter(index)


def generate_serials(count=10):
    existing = 0
    if os.path.exists(SERIALS_FILE):
        with open(SERIALS_FILE, 'r') as f:
            existing = len([l for l in f.readlines() if l.strip()])

    serials = []
    for i in range(existing, existing + count):
        serials.append(_serial_from_counter(i))
    return serials


if __name__ == "__main__":
    import sys
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    serials = generate_serials(count)

    print(f"Generando {count} seriales de un solo uso...\n")
    for i, s in enumerate(serials, 1):
        print(f"  {i}. {s}")

    with open(SERIALS_FILE, 'a', encoding='utf-8') as f:
        f.write("\n".join(serials) + "\n")

    print(f"\nSeriales guardados en {SERIALS_FILE}")
