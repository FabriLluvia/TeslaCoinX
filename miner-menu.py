import json, os, time, random, secrets
import psutil  # Para CPU y temperatura
from miner import minar_bloque, calcular_reward, cargar_json, guardar_json, obtener_ultimo_hash, BLOCKCHAIN_FILE, TRANSACTIONS_FILE

CONFIG_FILE = "minerconfig.tscoin"

# --- Configuración ---
def cargar_config():
    if not os.path.exists(CONFIG_FILE):
        return {
            "active_time": 60,
            "rest_time": 10,
            "cpu_percent": 80,
            "cores": 1,
            "max_temp": 75,
            "max_blocks": 5
        }
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def guardar_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# --- Temperatura ---
def leer_temperatura():
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return random.uniform(40, 70)
        for name, entries in temps.items():
            if entries:
                return entries[0].current
    except Exception:
        return random.uniform(40, 70)
    return 50.0

# --- Configuración interactiva ---
def configurar():
    config = cargar_config()
    print("\n=== Configuración del minero ===")
    config["active_time"] = int(input(f"Tiempo de minado activo (s) [{config['active_time']}]: ") or config["active_time"])
    config["rest_time"] = int(input(f"Tiempo de reposo (s) [{config['rest_time']}]: ") or config["rest_time"])
    config["cpu_percent"] = int(input(f"% uso de CPU (0-100) [{config['cpu_percent']}]: ") or config["cpu_percent"])
    config["cores"] = int(input(f"Núcleos de CPU a usar [{config['cores']}]: ") or config["cores"])
    config["max_temp"] = int(input(f"Temperatura máxima (°C) [{config['max_temp']}]: ") or config["max_temp"])
    config["max_blocks"] = int(input(f"Máximo de bloques por sesión [{config.get('max_blocks', 5)}]: ") or config.get("max_blocks", 5))
    guardar_config(config)
    print("✅ Configuración guardada.")

# --- Minado principal ---
def iniciar():
    config = cargar_config()
    wallet = input("Ingresa tu dirección de wallet de minero: ").strip()
    if not wallet:
        print("⚠️ Wallet vacía.")
        return

    blockchain = cargar_json(BLOCKCHAIN_FILE)
    max_blocks = config.get("max_blocks", 5)

    print(f"\n🚀 Iniciando minado con config: {config}")
    bloques_minados = 0

    while bloques_minados < max_blocks:
        temp = leer_temperatura()
        if temp >= config["max_temp"]:
            print(f"🌡️ Temperatura alta ({temp:.1f}°C) ≥ {config['max_temp']}°C. Pausando...")
            time.sleep(config["rest_time"])
            continue

        index = len(blockchain)
        reward = calcular_reward(index)
        transacciones = cargar_json(TRANSACTIONS_FILE)
        transacciones.append({
            "from": "NETWORK",
            "to": wallet,
            "amount": reward,
            "timestamp": int(time.time()),
            "firma": ""
        })

        previous_hash = obtener_ultimo_hash(blockchain)
        salt = secrets.token_hex(8)

        bloque = {
            "index": index,
            "timestamp": int(time.time()),
            "transactions": transacciones,
            "miner_wallet": wallet,
            "reward": reward,
            "previous_hash": previous_hash,
            "salt": salt,
            "nonce": 0,
            "hash": ""
        }

        print(f"\n⛏️ Minando bloque #{index} con recompensa {reward} TSCOIN...")
        t_inicio = time.time()
        bloque_mined = minar_bloque(bloque)
        t_fin = time.time()

        blockchain.append(bloque_mined)
        guardar_json(BLOCKCHAIN_FILE, blockchain)
        guardar_json(TRANSACTIONS_FILE, [])
        print(f"✅ Bloque #{index} minado en {t_fin - t_inicio:.2f}s → {bloque_mined['hash']}")
        bloques_minados += 1

        print(f"🛌 Descansando {config['rest_time']} segundos...")
        time.sleep(config["rest_time"])

    print("✅ Sesión de minería finalizada.")

# --- Menú CLI ---
if __name__ == "__main__":
    while True:
        print("\n=== Menú del Minero TeslaCoin ===")
        print("1. Iniciar minado")
        print("2. Configuración")
        print("3. Salir")
        op = input("Elige opción: ").strip()

        if op == "1":
            iniciar()
        elif op == "2":
            configurar()
        elif op == "3":
            break
        else:
            print("❌ Opción inválida.")
