import json
import os
from transactions import crear_transaccion

WALLET_FILE = "wallet.tscoin"

def crear_billetera():
    direccion = input("Crea una dirección de wallet (nombre o código): ").strip()
    clave_publica = os.urandom(32).hex()  # Simulación
    clave_privada = os.urandom(64).hex()  # Simulación

    wallet = {
        "direccion": direccion,
        "clave_publica": clave_publica,
        "clave_privada": clave_privada
    }

    with open(WALLET_FILE, "w") as f:
        json.dump(wallet, f, indent=2)

    print("\n✅ Billetera creada con éxito.\n")

def ver_billetera():
    try:
        with open(WALLET_FILE, "r") as f:
            wallet = json.load(f)
            print("\n=== Tu billetera ===")
            print("Dirección:", wallet.get("direccion", "Desconocida"))
            print("Clave pública:", wallet.get("clave_publica", "Desconocida"))
            print()
    except FileNotFoundError:
        print("\n⚠️ No se encontró una billetera. Crea una primero.\n")

def ver_clave_privada():
    try:
        with open(WALLET_FILE, "r") as f:
            wallet = json.load(f)
            print("\n🔐 Clave privada:", wallet.get("clave_privada", "No encontrada"), "\n")
    except FileNotFoundError:
        print("\n⚠️ No se encontró una billetera. Crea una primero.\n")

def transferir_dinero():
    try:
        with open(WALLET_FILE, "r") as f:
            wallet = json.load(f)
    except FileNotFoundError:
        print("\n⚠️ No se encontró la billetera. Crea una primero.\n")
        return

    destino = input("Dirección destino: ").strip()
    try:
        monto = float(input("Monto: "))
    except ValueError:
        print("❌ Monto inválido.")
        return

    crear_transaccion(wallet.get("direccion", ""), destino, monto)

def consultar_saldo():
    try:
        with open(WALLET_FILE, "r") as f:
            wallet = json.load(f)
    except FileNotFoundError:
        print("\n⚠️ No se encontró wallet.tscoin. Por favor, crea una billetera primero.\n")
        return

    direccion = wallet.get("direccion")
    if not direccion:
        print("\n⚠️ Dirección no encontrada en la wallet.\n")
        return

    saldo = 0

    if not os.path.exists("blockchain.tscoin"):
        print("\n⚠️ Archivo de blockchain no encontrado.\n")
        return

    try:
        with open("blockchain.tscoin", "r") as archivo:
            for linea in archivo:
                if not linea.strip():
                    continue

                try:
                    bloque = json.loads(linea)
                except json.JSONDecodeError:
                    continue

                transacciones = bloque.get("transacciones", [])
                for tx in transacciones:
                    if not isinstance(tx, dict):
                        continue

                    if tx.get("to") == direccion:
                        saldo += tx.get("amount", 0)
                    elif tx.get("from") == direccion:
                        saldo -= tx.get("amount", 0)

        print(f"\n💰 Saldo actual de {direccion}: {saldo} TSCOIN\n")

    except Exception as e:
        print(f"\n❌ Error al leer blockchain: {e}\n")

# ======= MENÚ =========
while True:
    print("=== Menú Wallet ===")
    print("1. Crear billetera")
    print("2. Ver billetera")
    print("3. Ver clave privada")
    print("4. Transferir dinero")
    print("5. Consultar saldo")
    print("6. Salir")
    opcion = input("Elige opción: ")

    if opcion == "1":
        crear_billetera()
    elif opcion == "2":
        ver_billetera()
    elif opcion == "3":
        ver_clave_privada()
    elif opcion == "4":
        transferir_dinero()
    elif opcion == "5":
        consultar_saldo()
    elif opcion == "6":
        break
    else:
        print("Opción no válida.\n")
