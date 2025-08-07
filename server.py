from flask import Flask, request, jsonify, send_file
import os
import json

app = Flask(__name__)

# Rutas de archivos locales
BLOCKCHAIN_FILE = "blockchain.tscoin"
TRANSACTIONS_FILE = "transactions.tscoin"

# Página principal
@app.route("/")
def index():
    return "🚀 ¡TeslaCoin API está viva!"

# Obtener la blockchain completa
@app.route("/blockchain", methods=["GET"])
def get_blockchain():
    if os.path.exists(BLOCKCHAIN_FILE):
        return send_file(BLOCKCHAIN_FILE, as_attachment=False)
    return jsonify({"error": "Blockchain no encontrada"}), 404

# Obtener transacciones pendientes
@app.route("/transactions", methods=["GET"])
def get_transactions():
    if os.path.exists(TRANSACTIONS_FILE):
        return send_file(TRANSACTIONS_FILE, as_attachment=False)
    return jsonify({"error": "Archivo de transacciones no encontrado"}), 404

# Enviar nueva transacción
@app.route("/submit_transaction", methods=["POST"])
def submit_transaction():
    if not request.is_json:
        return jsonify({"error": "Debe enviar JSON"}), 400
    tx = request.get_json()

    # Cargar transacciones existentes
    txs = []
    if os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, "r") as f:
            try:
                txs = json.load(f)
            except json.JSONDecodeError:
                txs = []

    txs.append(tx)
    with open(TRANSACTIONS_FILE, "w") as f:
        json.dump(txs, f, indent=2)

    return jsonify({"message": "Transacción recibida"}), 201

# Enviar nuevo bloque minado
@app.route("/submit_block", methods=["POST"])
def submit_block():
    if not request.is_json:
        return jsonify({"error": "Debe enviar JSON"}), 400
    block = request.get_json()

    # Cargar blockchain existente
    blockchain = []
    if os.path.exists(BLOCKCHAIN_FILE):
        with open(BLOCKCHAIN_FILE, "r") as f:
            try:
                blockchain = json.load(f)
            except json.JSONDecodeError:
                blockchain = []

    blockchain.append(block)
    with open(BLOCKCHAIN_FILE, "w") as f:
        json.dump(blockchain, f, indent=2)

    return jsonify({"message": "Bloque añadido a la blockchain"}), 201
