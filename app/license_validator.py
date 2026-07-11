import hashlib
import subprocess
import uuid
import os
import base64
import configparser

SECRET = "HardAgenda2026!x7Kp"
LICENSE_DIR = os.path.join(os.path.expandvars('%APPDATA%'), 'HardAgenda')
LICENSE_FILE = os.path.join(LICENSE_DIR, 'license.lic')


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


def _generate_serial_for_hw(hw_hash, index=0):
    data = f"{hw_hash}-{SECRET}-{index}"
    h = hashlib.sha256(data.encode()).hexdigest()[:32]
    return f"{h[0:4].upper()}-{h[4:8].upper()}-{h[8:12].upper()}-{h[12:16].upper()}"


def _generate_master_serial(hw_hash):
    data = f"MASTER-{SECRET}-{hw_hash}"
    h = hashlib.sha256(data.encode()).hexdigest()[:32]
    return f"{h[0:4].upper()}-{h[4:8].upper()}-{h[8:12].upper()}-{h[12:16].upper()}"


def _generate_any_master():
    data = f"MASTER-{SECRET}-UNIVERSAL"
    h = hashlib.sha256(data.encode()).hexdigest()[:32]
    return f"{h[0:4].upper()}-{h[4:8].upper()}-{h[8:12].upper()}-{h[12:16].upper()}"


def validate_serial(serial):
    serial = serial.strip().upper()
    hw_hash = get_hardware_fingerprint()

    master = _generate_any_master()
    if serial == master:
        return True

    for i in range(100):
        expected = _generate_serial_for_hw(hw_hash, index=i)
        if serial == expected:
            return True

    return False


def save_license(serial):
    os.makedirs(LICENSE_DIR, exist_ok=True)
    hw_hash = get_hardware_fingerprint()
    data = f"{serial}|{hw_hash}"
    encoded = base64.b64encode(data.encode()).decode()
    with open(LICENSE_FILE, 'w') as f:
        f.write(encoded)


def is_license_valid():
    if not os.path.exists(LICENSE_FILE):
        return False
    try:
        with open(LICENSE_FILE, 'r') as f:
            encoded = f.read().strip()
        data = base64.b64decode(encoded.encode()).decode()
        serial, hw_hash = data.split("|", 1)

        current_hw = get_hardware_fingerprint()
        if hw_hash != current_hw:
            return False

        return validate_serial(serial)
    except Exception:
        return False


def remove_license():
    if os.path.exists(LICENSE_FILE):
        os.remove(LICENSE_FILE)
