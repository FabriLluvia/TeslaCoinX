from flask import Flask, request, jsonify
import json, os, time
from hashlib import sha256

BLOCKCHAIN_FILE = "blockchain.tscoin"
TRANSACTIONS_FILE = "transactions.tscoin"
DIFFICULTY = 4

app = Flask(__name__)

# === Utilidades ===
def cargar_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def guardar_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def calcular_hash(bloque):
    bloque_copia = bloque.copy()
    bloque_copia.pop("hash", None)
    bloque_str = json.dumps(bloque_copia, sort_keys=True).encode()
    return sha256(bloque_str).hexdigest()

def obtener_ultimo_hash(blockchain):
    return "0" * 64 if len(blockchain) == 0 else blockchain[-1]["hash"]

def calcular_reward(index):
    halvings = index // 1_000_000
    return 400 / (2 ** halvings)

# === Endpoints ===
@app.route("/blockchain", methods=["GET"])
def obtener_blockchain():
    blockchain = cargar_json(BLOCKCHAIN_FILE)
    return jsonify(blockchain)

@app.route("/transaccion", methods=["POST"])
def nueva_transaccion():
    tx = request.get_json()
    if not tx or not all(k in tx for k in ["from", "to", "amount"]):
        return jsonify({"error": "Transacción inválida"}), 400
    tx["timestamp"] = int(time.time())
    tx["firma"] = ""
    txs = cargar_json(TRANSACTIONS_FILE)
    txs.append(tx)
    guardar_json(TRANSACTIONS_FILE, txs)
    return jsonify({"status": "Transacción añadida"})

@app.route("/minar", methods=["POST"])
def minar_bloque():
    wallet = request.json.get("wallet")
    if not wallet:
        return jsonify({"error": "Wallet requerida"}), 400

    blockchain = cargar_json(BLOCKCHAIN_FILE)
    txs = cargar_json(TRANSACTIONS_FILE)
    index = len(blockchain)
    reward = calcular_reward(index)

    # Recompensa al minero
    txs.append({
        "from": "NETWORK",
        "to": wallet,
        "amount": reward,
        "timestamp": int(time.time()),
        "firma": ""
    })

    bloque = {
        "index": index,
        "timestamp": int(time.time()),
        "transactions": txs,
        "miner_wallet": wallet,
        "reward": reward,
        "previous_hash": obtener_ultimo_hash(blockchain),
        "nonce": 0,
        "hash": ""
    }

    while True:
        bloque["nonce"] += 1
        h = calcular_hash(bloque)
        if h.startswith("0" * DIFFICULTY):
            bloque["hash"] = h
            break

    blockchain.append(bloque)
    guardar_json(BLOCKCHAIN_FILE, blockchain)
    guardar_json(TRANSACTIONS_FILE, [])

    return jsonify({"status": "Bloque minado", "bloque": bloque})

@app.route("/info", methods=["GET"])
def info():
    blockchain = cargar_json(BLOCKCHAIN_FILE)
    return jsonify({
        "bloques": len(blockchain),
        "ultima_hash": blockchain[-1]["hash"] if blockchain else None
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
