import hashlib
import subprocess
import uuid
import os
import base64
import json

SECRET = "HardAgenda2026!x7Kp"
LICENSE_DIR = os.path.join(os.path.expandvars('%APPDATA%'), 'HardAgenda')
LICENSE_FILE = os.path.join(LICENSE_DIR, 'license.lic')
MASTER_SERIAL = "HARD-MAST-ERK2026"


def get_hardware_fingerprint():
    parts = []
    try:
        result = subprocess.run(
            ['wmic', 'cpu', 'get', 'ProcessorId'],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if line and line != 'ProcessorId':
                parts.append(line)
                break
    except Exception:
        pass

    try:
        result = subprocess.run(
            ['wmic', 'diskdrive', 'get', 'SerialNumber'],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if line and line != 'SerialNumber' and line != '':
                parts.append(line)
                break
    except Exception:
        pass

    raw = "-".join(parts) if parts else str(uuid.getnode())
    return hashlib.sha256(raw.encode()).hexdigest()


def validate_serial(serial):
    serial = serial.strip().upper()

    if serial == MASTER_SERIAL:
        return True

    if len(serial) != 14 or serial.count('-') != 2:
        return False
    parts = serial.split('-')
    if len(parts) != 3:
        return False
    for p in parts:
        if len(p) != 4:
            return False

    for i in range(100000):
        raw = f"{SECRET}-{i:06d}"
        h = hashlib.sha256(raw.encode()).hexdigest()[:12]
        expected = f"{h[0:4].upper()}-{h[4:8].upper()}-{h[8:12].upper()}"
        if serial == expected:
            return True

    return False


def save_license(serial):
    os.makedirs(LICENSE_DIR, exist_ok=True)
    hw_hash = get_hardware_fingerprint()
    data = {
        "serial": serial.strip().upper(),
        "hw": hw_hash
    }
    encoded = base64.b64encode(json.dumps(data).encode()).decode()
    with open(LICENSE_FILE, 'w') as f:
        f.write(encoded)


def is_license_valid():
    if not os.path.exists(LICENSE_FILE):
        return False
    try:
        with open(LICENSE_FILE, 'r') as f:
            encoded = f.read().strip()
        data = json.loads(base64.b64decode(encoded.encode()).decode())
        serial = data["serial"]
        hw_hash = data["hw"]

        if serial == MASTER_SERIAL:
            return True

        current_hw = get_hardware_fingerprint()
        if hw_hash != current_hw:
            return False

        return validate_serial(serial)
    except Exception:
        return False


def remove_license():
    if os.path.exists(LICENSE_FILE):
        os.remove(LICENSE_FILE)
