import hashlib
import subprocess
import sys
import uuid
import os
import base64

SECRET = "HardAgenda2026!x7Kp"


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


def generate_serial(hw_hash, index=0, master=False):
    if master:
        data = f"MASTER-{SECRET}-UNIVERSAL"
    else:
        data = f"{hw_hash}-{SECRET}-{index}"
    h = hashlib.sha256(data.encode()).hexdigest()[:32]
    return f"{h[0:4].upper()}-{h[4:8].upper()}-{h[8:12].upper()}-{h[12:16].upper()}"


def validate_serial(serial, hw_hash, master_serial):
    if serial == master_serial:
        return True
    for i in range(100):
        expected = generate_serial(hw_hash, index=i)
        if serial == expected:
            return True
    return False


def save_license(serial, hw_hash, path="license.lic"):
    data = f"{serial}|{hw_hash}"
    encoded = base64.b64encode(data.encode()).decode()
    with open(path, 'w') as f:
        f.write(encoded)


def load_license(path="license.lic"):
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r') as f:
            encoded = f.read().strip()
        data = base64.b64decode(encoded.encode()).decode()
        serial, hw_hash = data.split("|", 1)
        return serial, hw_hash
    except Exception:
        return None


if __name__ == "__main__":
    hw = get_hardware_fingerprint()
    master = generate_serial(hw, master=True)

    print(f"Hardware fingerprint: {hw[:16]}...")
    print(f"\nSerial maestro (funciona en cualquier PC): {master}")
    print(f"\nSeriales para esta PC ({hw[:16]}...):")
    for i in range(5):
        s = generate_serial(hw, index=i)
        print(f"  Serial {i+1}: {s}")

    print(f"\nPara generar seriales para otra PC, ejecuta:")
    print(f"  python serial_generator.py <hardware_hash>")
    if len(sys.argv) > 1:
        other_hw = sys.argv[1]
        other_master = generate_serial(other_hw, master=True)
        print(f"\nSerial maestro para {other_hw[:16]}...: {other_master}")
        for i in range(5):
            s = generate_serial(other_hw, index=i)
            print(f"  Serial {i+1}: {s}")
