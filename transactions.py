import json
import time
import os
import requests

TRANSACTIONS_FILE = "transactions.tscoin"
REPLIT_SERVER_URL = "https://97f8658f-c24a-4e9d-9e7c-813890df2937-00-2qyl45og2tx6y.picard.replit.dev/submit_transaction"

def cargar_json(file):
    if not os.path.exists(file):
        return []
    if os.path.getsize(file) == 0:
        return []
    with open(file, "r") as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

def guardar_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def crear_transaccion(origen, destino, monto):
    transacciones = cargar_json(TRANSACTIONS_FILE)

    nueva_tx = {
        "from": origen,
        "to": destino,
        "amount": monto,
        "timestamp": int(time.time()),
        "firma": ""  # Aquí deberías poner la firma si tienes sistema de firmas
    }

    transacciones.append(nueva_tx)
    guardar_json(TRANSACTIONS_FILE, transacciones)

    print("✅ Transacción guardada localmente.")

    # Enviar al servidor Replit
    try:
        response = requests.post(REPLIT_SERVER_URL, json=nueva_tx)
        if response.status_code == 201:
            print("🌍 Transacción enviada al servidor Replit con éxito.")
        else:
            print(f"⚠️ Error al enviar transacción al servidor: {response.status_code}")
    except Exception as e:
        print(f"❌ No se pudo conectar al servidor Replit: {e}")

if __name__ == "__main__":
    desde = input("Desde (wallet address): ").strip()
    hacia = input("Hacia (wallet address): ").strip()
    monto = float(input("Monto a enviar: "))
    crear_transaccion(desde, hacia, monto)
