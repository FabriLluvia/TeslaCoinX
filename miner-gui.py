import tkinter as tk
from tkinter import ttk, messagebox
import threading, time, json, os
from miner import minar_bloque, calcular_reward, cargar_json, guardar_json, obtener_ultimo_hash, BLOCKCHAIN_FILE, TRANSACTIONS_FILE, DIFFICULTY

CONFIG_FILE = "minerconfig.tscoin"

# --- Cargar y guardar config ---
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

# --- GUI principal ---
class MinerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TeslaCoin Miner")
        self.geometry("550x400")
        self.config_data = cargar_config()
        self.mining_thread = None
        self.mining_active = False

        tk.Label(self, text="Wallet del minero:").pack(pady=5)
        self.wallet_entry = tk.Entry(self, width=50)
        self.wallet_entry.pack(pady=5)

        tk.Button(self, text="Iniciar minado", command=self.start_mining).pack(pady=5)
        tk.Button(self, text="Configuración", command=self.open_config_window).pack(pady=5)
        tk.Button(self, text="Detener minado", command=self.stop_mining).pack(pady=5)

        self.status_label = tk.Label(self, text="Estado: Inactivo")
        self.status_label.pack(pady=5)

        self.progress = ttk.Progressbar(self, length=400, mode="determinate")
        self.progress.pack(pady=5)

        self.log_text = tk.Text(self, height=12, wrap="word")
        self.log_text.pack(fill="both", expand=True, pady=5)

    def log(self, msg):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")

    def start_mining(self):
        wallet = self.wallet_entry.get().strip()
        if not wallet:
            messagebox.showwarning("Atención", "Ingresa una dirección de wallet")
            return
        if self.mining_active:
            messagebox.showinfo("Minería", "El minado ya está en ejecución.")
            return
        self.mining_active = True
        self.status_label.config(text="Estado: Minando...")
        self.mining_thread = threading.Thread(target=self.mining_loop, args=(wallet,), daemon=True)
        self.mining_thread.start()

    def stop_mining(self):
        self.mining_active = False
        self.status_label.config(text="Estado: Detenido")
        self.log("Minería detenida por el usuario.")

    def mining_loop(self, wallet):
        blockchain = cargar_json(BLOCKCHAIN_FILE)
        max_blocks = self.config_data.get("max_blocks", 5)

        for _ in range(max_blocks):
            if not self.mining_active:
                break

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
            bloque = {
                "index": index,
                "timestamp": int(time.time()),
                "transactions": transacciones,
                "miner_wallet": wallet,
                "reward": reward,
                "previous_hash": previous_hash,
                "nonce": 0,
                "hash": ""
            }

            self.log(f"Minando bloque #{index} con recompensa {reward} TSCOIN...")
            start_time = time.time()
            bloque_mined = minar_bloque(bloque)
            elapsed = time.time() - start_time
            blockchain.append(bloque_mined)
            guardar_json(BLOCKCHAIN_FILE, blockchain)
            guardar_json(TRANSACTIONS_FILE, [])
            self.log(f"Bloque #{index} minado en {elapsed:.2f}s -> {bloque_mined['hash']}")

        self.mining_active = False
        self.status_label.config(text="Estado: Finalizado")
        self.log("Minería completada.")

    def open_config_window(self):
        config_win = tk.Toplevel(self)
        config_win.title("Configuración del Minero")

        fields = [
            ("Tiempo activo (s)", "active_time"),
            ("Tiempo de reposo (s)", "rest_time"),
            ("% CPU", "cpu_percent"),
            ("Núcleos", "cores"),
            ("Temp máxima (°C)", "max_temp"),
            ("Máx. bloques por sesión", "max_blocks")
        ]

        entries = {}
        for label, key in fields:
            tk.Label(config_win, text=label).pack()
            entry = tk.Entry(config_win)
            entry.insert(0, str(self.config_data[key]))
            entry.pack()
            entries[key] = entry

        def save_and_close():
            try:
                for key, entry in entries.items():
                    self.config_data[key] = int(entry.get())
                guardar_config(self.config_data)
                self.log("Configuración guardada.")
                config_win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Todos los valores deben ser numéricos")

        tk.Button(config_win, text="Guardar", command=save_and_close).pack(pady=5)

if __name__ == "__main__":
    app = MinerGUI()
    app.mainloop()
