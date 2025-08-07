import json, os, time, hashlib, random, struct, math
import requests  # 👈 Necesario para enviar el bloque

TRANSACTIONS_FILE = "transactions.tscoin"
BLOCKCHAIN_FILE = "blockchain.tscoin"
REPLIT_SERVER_URL = "https://97f8658f-c24a-4e9d-9e7c-813890df2937-00-2qyl45og2tx6y.picard.replit.dev/submit_block"
DIFFICULTY = 3

DATASET_SIZE = 256 * 1024 * 1024
CHUNK_SIZE = 64

# --- Dataset y programa dinámico ---
def init_dataset(seed):
    random.seed(seed)
    return bytearray(random.getrandbits(8) for _ in range(DATASET_SIZE))

def generate_program(seed, length=32):
    random.seed(seed)
    instructions = []
    ops = ["ADD", "XOR", "MUL", "ROT", "FADD", "FMUL"]
    for _ in range(length):
        op = random.choice(ops)
        addr = random.randint(0, DATASET_SIZE - CHUNK_SIZE)
        const = random.randint(1, 1000)
        instructions.append((op, addr, const))
    return instructions

def execute_program(dataset, instructions, nonce):
    acc_int = nonce
    acc_float = float(nonce)
    for (op, addr, const) in instructions:
        chunk = dataset[addr:addr+CHUNK_SIZE]
        value = int.from_bytes(chunk, "little")
        if op == "ADD":
            acc_int += value * const
        elif op == "XOR":
            acc_int ^= value
        elif op == "MUL":
            acc_int *= (value | 1)
        elif op == "ROT":
            shift = const % 64
            acc_int = ((acc_int << shift) | (acc_int >> (64 - shift))) & ((1 << 64) - 1)
        elif op == "FADD":
            acc_float += math.sin(value % 360) * const
        elif op == "FMUL":
            acc_float *= math.cos((value % 360) / (const or 1))
    mixed = struct.pack("<Qd", acc_int & ((1 << 64) - 1), acc_float)
    return hashlib.blake2b(mixed).hexdigest()

def prueba_de_trabajo(prev_hash, datos_bloque, dificultad):
    seed = hashlib.sha3_256((prev_hash + datos_bloque).encode()).digest()
    dataset = init_dataset(seed)
    program = generate_program(seed)
    prefix = "0" * dificultad
    nonce = 0
    start = time.time()
    while True:
        resultado = execute_program(dataset, program, nonce)
        if resultado.startswith(prefix):
            return nonce, resultado, time.time() - start
        nonce += 1

# --- Blockchain estándar ---
def calcular_reward(index):
    halvings = index // 1_000_000
    return 400 / (2 ** halvings)

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

def obtener_ultimo_hash(blockchain):
    return "0" * 64 if len(blockchain) == 0 else blockchain[-1]["hash"]

def minar_bloque(bloque):
    datos = json.dumps(bloque["transactions"], sort_keys=True)
    nonce, hash_result, tiempo = prueba_de_trabajo(bloque["previous_hash"], datos, DIFFICULTY)
    bloque["nonce"] = nonce
    bloque["hash"] = hash_result
    print(f"✅ Bloque minado con nonce {nonce} en {tiempo:.2f}s -> {hash_result}")
    return bloque

def enviar_al_servidor(bloque):
    try:
        response = requests.post(REPLIT_SERVER_URL, json=bloque)
        if response.status_code == 201:
            print("🌍 Bloque enviado al servidor Replit con éxito.")
            return True
        else:
            print(f"⚠️ Error al enviar bloque al servidor: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se pudo conectar al servidor Replit: {e}")
        return False

def minar(miner_wallet):
    blockchain = cargar_json(BLOCKCHAIN_FILE)
    transacciones = cargar_json(TRANSACTIONS_FILE)

    index = len(blockchain)
    reward = calcular_reward(index)

    transacciones.append({
        "from": "NETWORK",
        "to": miner_wallet,
        "amount": reward,
        "timestamp": int(time.time()),
        "firma": ""
    })

    previous_hash = obtener_ultimo_hash(blockchain)
    bloque = {
        "index": index,
        "timestamp": int(time.time()),
        "transactions": transacciones,
        "miner_wallet": miner_wallet,
        "reward": reward,
        "previous_hash": previous_hash,
        "nonce": 0,
        "hash": ""
    }

    print(f"🚀 Minando bloque #{index} con recompensa: {reward} TSCOIN ...")
    bloque_mined = minar_bloque(bloque)

    # Enviar primero al servidor
    if enviar_al_servidor(bloque_mined):
        # Si se acepta, guardar localmente
        blockchain.append(bloque_mined)
        guardar_json(BLOCKCHAIN_FILE, blockchain)
        guardar_json(TRANSACTIONS_FILE, [])
        print("🗃️ Bloque guardado localmente y transacciones limpiadas.")
    else:
        print("⚠️ No se guardó localmente el bloque porque no fue aceptado por el servidor.")

if __name__ == "__main__":
    miner_wallet = input("Ingresa la dirección de tu wallet de minero: ").strip()
    minar(miner_wallet)
