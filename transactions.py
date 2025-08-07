import time
import json
from nacl import signing

# === Crear transacción ===
def crear_transaccion(clave_privada_hex, from_address, to_address, amount):
    tx = {
        "from": from_address,
        "to": to_address,
        "amount": amount,
        "timestamp": int(time.time())
    }
    mensaje = json.dumps(tx, sort_keys=True).encode()
    clave_privada = signing.SigningKey(bytes.fromhex(clave_privada_hex))
    firma = clave_privada.sign(mensaje).signature.hex()
    tx["firma"] = firma
    return tx

# === Verificar transacción ===
def verificar_transaccion(transaccion, clave_publica_hex):
    firma_hex = transaccion["firma"]
    tx_sin_firma = transaccion.copy()
    del tx_sin_firma["firma"]
    mensaje = json.dumps(tx_sin_firma, sort_keys=True).encode()
    clave_publica = signing.VerifyKey(bytes.fromhex(clave_publica_hex))
    try:
        clave_publica.verify(mensaje, bytes.fromhex(firma_hex))
        return True
    except Exception:
        return False

# === Interfaz ===
if __name__ == "__main__":
    print("=== Crear y verificar transacción ===")
    clave_privada_hex = input("Clave privada (hex): ").strip()
    clave_publica_hex = input("Clave pública (hex): ").strip()
    from_address = input("Dirección remitente: ").strip()
    to_address = input("Dirección destino: ").strip()
    amount = float(input("Monto a transferir: ").strip())

    tx = crear_transaccion(clave_privada_hex, from_address, to_address, amount)
    print("\n--- Transacción creada ---")
    print(json.dumps(tx, indent=2))

    es_valida = verificar_transaccion(tx, clave_publica_hex)
    print("\n¿Firma válida?:", es_valida)
