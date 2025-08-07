import json, os
from wallet import generar_wallet_con_prefijo
from transactions import crear_transaccion

WALLET_FILE = "wallet.tscoin"
TRANSACTIONS_FILE = "transactions.tscoin"
BLOCKCHAIN_FILE = "blockchain.tscoin"

# === Auxiliares ===
def cargar_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def guardar_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# === Crear billetera ===
def crear_billetera():
    print("\n=== Generación de Wallet ===")
    print("1. Prefijo aleatorio de 2 caracteres")
    print("2. Prefijo de 1 carácter elegido + 1 aleatorio")
    print("3. Prefijo exacto de 2 caracteres elegido")

    modo = int(input("Elige modo (1, 2 o 3): ").strip())
    prefijo = ""
    if modo == 2:
        prefijo = input("Ingresa tu prefijo (1 carácter): ").strip()
    elif modo == 3:
        prefijo = input("Ingresa tu prefijo (2 caracteres): ").strip()

    clave_privada, clave_publica, direccion = generar_wallet_con_prefijo(prefijo, modo)
    wallet = {
        "clave_privada": clave_privada,
        "clave_publica": clave_publica,
        "direccion": direccion
    }
    guardar_json(WALLET_FILE, wallet)
    print("\n=== Billetera creada ===")
    print("Dirección:", direccion)
    print("Clave pública:", clave_publica)

# === Ver billetera ===
def ver_billetera():
    if not os.path.exists(WALLET_FILE):
        print("No existe billetera. Crea una primero.")
        return
    wallet = cargar_json(WALLET_FILE)
    print("\n=== Tu billetera ===")
    print("Dirección:", wallet["direccion"])
    print("Clave pública:", wallet["clave_publica"])

# === Ver clave privada ===
def ver_clave_privada():
    if not os.path.exists(WALLET_FILE):
        print("No existe billetera.")
        return
    wallet = cargar_json(WALLET_FILE)
    print("\n=== Clave privada ===")
    print("ADVERTENCIA: NO COMPARTAS ESTA CLAVE")
    print(wallet["clave_privada"])

# === Transferir dinero ===
def transferir_dinero():
    if not os.path.exists(WALLET_FILE):
        print("No existe billetera. Crea una primero.")
        return
    wallet = cargar_json(WALLET_FILE)
    destino = input("Dirección destino: ").strip()
    monto = float(input("Monto: "))
    tx = crear_transaccion(wallet["clave_privada"], wallet["direccion"], destino, monto)
    transacciones = cargar_json(TRANSACTIONS_FILE)
    transacciones.append(tx)
    guardar_json(TRANSACTIONS_FILE, transacciones)
    print("\nTransacción guardada en transactions.tscoin")

# === Consultar saldo ===
def consultar_saldo():
    if not os.path.exists(WALLET_FILE):
        print("No existe billetera.")
        return
    wallet = cargar_json(WALLET_FILE)
    direccion = wallet["direccion"]
    blockchain = cargar_json(BLOCKCHAIN_FILE)

    saldo = 0.0
    for bloque in blockchain:
        for tx in bloque.get("transactions", []):
            if tx["to"] == direccion:
                saldo += tx["amount"]
            if tx["from"] == direccion:
                saldo -= tx["amount"]
    print(f"\nSaldo actual de {direccion}: {saldo}")

# === Menú principal ===
if __name__ == "__main__":
    while True:
        print("\n=== Menú Wallet ===")
        print("1. Crear billetera")
        print("2. Ver billetera")
        print("3. Ver clave privada")
        print("4. Transferir dinero")
        print("5. Consultar saldo")
        print("6. Salir")
        opcion = input("Elige opción: ").strip()

        if opcion == "1": crear_billetera()
        elif opcion == "2": ver_billetera()
        elif opcion == "3": ver_clave_privada()
        elif opcion == "4": transferir_dinero()
        elif opcion == "5": consultar_saldo()
        elif opcion == "6": break
        else: print("Opción inválida")
