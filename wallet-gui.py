import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json, os
from wallet import generar_wallet_con_prefijo
from transactions import crear_transaccion

WALLET_FILE = "wallet.tscoin"
TRANSACTIONS_FILE = "transactions.tscoin"
BLOCKCHAIN_FILE = "blockchain.tscoin"

def cargar_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def guardar_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

class WalletGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TeslaCoin Wallet")
        self.geometry("500x400")

        # Botones principales
        ttk.Button(self, text="Crear billetera", command=self.crear_billetera).pack(pady=5, fill="x")
        ttk.Button(self, text="Ver billetera", command=self.ver_billetera).pack(pady=5, fill="x")
        ttk.Button(self, text="Ver clave privada", command=self.ver_clave_privada).pack(pady=5, fill="x")
        ttk.Button(self, text="Transferir dinero", command=self.transferir_dinero).pack(pady=5, fill="x")
        ttk.Button(self, text="Consultar saldo", command=self.consultar_saldo).pack(pady=5, fill="x")

        # Área de resultados
        self.result_text = tk.Text(self, wrap="word", height=15)
        self.result_text.pack(fill="both", expand=True, pady=5)

    def log(self, msg):
        self.result_text.insert("end", msg + "\n")
        self.result_text.see("end")

    def crear_billetera(self):
        modos = {"1": "Prefijo aleatorio (2 caracteres)",
                 "2": "Prefijo 1 char elegido + 1 aleatorio",
                 "3": "Prefijo exacto (2 caracteres elegido)"}
        modo = simpledialog.askstring("Modo", f"Elige modo:\n1 - {modos['1']}\n2 - {modos['2']}\n3 - {modos['3']}")
        if not modo or modo not in ["1", "2", "3"]:
            messagebox.showerror("Error", "Modo inválido.")
            return
        prefijo = ""
        if modo == "2":
            prefijo = simpledialog.askstring("Prefijo", "Ingresa tu prefijo (1 carácter):")
        elif modo == "3":
            prefijo = simpledialog.askstring("Prefijo", "Ingresa tu prefijo (2 caracteres):")

        clave_privada, clave_publica, direccion = generar_wallet_con_prefijo(prefijo or "", int(modo))
        wallet = {"clave_privada": clave_privada, "clave_publica": clave_publica, "direccion": direccion}
        guardar_json(WALLET_FILE, wallet)
        self.log(f"Billetera creada:\nDirección: {direccion}\nClave pública: {clave_publica}")

    def ver_billetera(self):
        if not os.path.exists(WALLET_FILE):
            messagebox.showinfo("Info", "No existe billetera. Crea una primero.")
            return
        wallet = cargar_json(WALLET_FILE)
        self.log(f"=== Tu billetera ===\nDirección: {wallet['direccion']}\nClave pública: {wallet['clave_publica']}")

    def ver_clave_privada(self):
        if not os.path.exists(WALLET_FILE):
            messagebox.showinfo("Info", "No existe billetera.")
            return
        wallet = cargar_json(WALLET_FILE)
        self.log(f"=== Clave privada ===\nADVERTENCIA: NO COMPARTAS ESTA CLAVE\n{wallet['clave_privada']}")

    def transferir_dinero(self):
        if not os.path.exists(WALLET_FILE):
            messagebox.showinfo("Info", "No existe billetera. Crea una primero.")
            return
        wallet = cargar_json(WALLET_FILE)
        destino = simpledialog.askstring("Transferir", "Dirección destino:")
        monto = simpledialog.askfloat("Transferir", "Monto a enviar:")
        if not destino or not monto:
            return
        tx = crear_transaccion(wallet["clave_privada"], wallet["direccion"], destino, monto)
        transacciones = cargar_json(TRANSACTIONS_FILE)
        transacciones.append(tx)
        guardar_json(TRANSACTIONS_FILE, transacciones)
        self.log(f"Transacción guardada en {TRANSACTIONS_FILE}")

    def consultar_saldo(self):
        if not os.path.exists(WALLET_FILE):
            messagebox.showinfo("Info", "No existe billetera.")
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
        self.log(f"Saldo actual de {direccion}: {saldo}")

if __name__ == "__main__":
    app = WalletGUI()
    app.mainloop()
