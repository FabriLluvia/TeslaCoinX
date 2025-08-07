import os
import hashlib
import base58
import random
import string
from nacl import signing

# --- Funciones base ---
def generar_clave_privada():
    return os.urandom(32)

def derivar_clave_publica(clave_privada):
    signing_key = signing.SigningKey(clave_privada)
    verify_key = signing_key.verify_key
    return bytes(verify_key)

def keccak256(data):
    return hashlib.new('sha3_256', data).digest()

def base58_monero(data):
    return base58.b58encode(data).decode()

def generar_wallet_base():
    clave_privada = generar_clave_privada()
    clave_publica = derivar_clave_publica(clave_privada)
    datos_direccion = b'\x12' + clave_publica
    checksum = keccak256(datos_direccion)[:4]
    direccion = base58_monero(datos_direccion + checksum)
    return clave_privada.hex(), clave_publica.hex(), direccion

# --- Generador de caracteres aleatorios ---
def random_char():
    return random.choice(string.ascii_letters + string.digits)

# --- Modos de prefijo ---
def generar_wallet_con_prefijo(prefijo_usuario, modo):
    clave_privada, clave_publica, direccion_base = generar_wallet_base()

    if modo == 1:
        # Prefijo de 2 caracteres aleatorios
        prefijo_final = random_char() + random_char()
        direccion = prefijo_final + direccion_base

    elif modo == 2:
        # Prefijo elegido (1 char) + otro aleatorio
        if len(prefijo_usuario) != 1:
            raise ValueError("Modo 2 requiere prefijo de 1 carácter")
        prefijo_final = prefijo_usuario + random_char()
        direccion = prefijo_final + direccion_base

    elif modo == 3:
        # Prefijo exacto de 2 caracteres elegido por el usuario
        if len(prefijo_usuario) != 2:
            raise ValueError("Modo 3 requiere prefijo de 2 caracteres")
        direccion = prefijo_usuario + direccion_base

    else:
        raise ValueError("Modo inválido. Usa 1, 2 o 3.")

    return clave_privada, clave_publica, direccion

# --- Interfaz ---
if __name__ == "__main__":
    print("=== Generador de Wallet con Prefijos (3 modos) ===")
    print("1. Prefijo aleatorio de 2 caracteres")
    print("2. Prefijo de 1 carácter elegido + 1 aleatorio")
    print("3. Prefijo exacto de 2 caracteres elegido\n")

    modo = int(input("Elige modo (1, 2 o 3): ").strip())
    prefijo = ""
    if modo == 2:
        prefijo = input("Ingresa tu prefijo (1 carácter): ").strip()
    elif modo == 3:
        prefijo = input("Ingresa tu prefijo (2 caracteres): ").strip()

    try:
        clave_privada, clave_publica, direccion = generar_wallet_con_prefijo(prefijo, modo)
        print("\n=== Wallet generada ===")
        print("Clave privada:", clave_privada)
        print("Clave pública:", clave_publica)
        print("Dirección:", direccion)
    except ValueError as e:
        print("Error:", e)
