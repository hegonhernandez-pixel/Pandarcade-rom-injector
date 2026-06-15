import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- DICCIONARIO DE BIOS ---
PANDORA_BIOS_MAP = {
    "scph5501.bin": ["playstation", "BIOS PS1"],
    "dc_boot.bin": ["dreamcast", "Boot Dreamcast"],
    "awbios.zip": ["dreamcast", "BIOS Atomiswave"],
    "naomi.zip": ["dreamcast", "BIOS Naomi"],
    "gba_bios.bin": ["gba", "BIOS GBA"],
    "neogeo.zip": ["mame139", "BIOS NeoGeo MAME 139"],
    "neogeo.zip": ["fba42", "BIOS NeoGeo FBA"]
}

class PandarcadeMainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Pandarcade - BIOS & ROMs")
        self.root.geometry("750x500")
        
        # 🛑 Variable de control para el botón STOP
        self.corriendo = False

        # Interfaz Base (Pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_roms = tk.Frame(self.notebook, bg="#141419")
        self.tab_bios = tk.Frame(self.notebook, bg="#141419")

        self.notebook.add(self.tab_roms, text=" 🎮 ROMs ")
        self.notebook.add(self.tab_bios, text=" 🛠️ BIOS ")

        self.setup_bios_tab()

    def setup_bios_tab(self):
        self.origen_path = tk.StringVar()
        self.destino_path = tk.StringVar()

        # Configuración de Rutas
        f_origen = tk.LabelFrame(self.tab_bios, text=" Origen de BIOS ", bg="#141419", fg="#00f0ff")
        f_origen.pack(fill="x", padx=20, pady=5)
        tk.Entry(f_origen, textvariable=self.origen_path, width=50).pack(side="left", padx=5)
        tk.Button(f_origen, text="...", command=lambda: self.origen_path.set(filedialog.askdirectory())).pack(side="right", padx=5)

        f_destino = tk.LabelFrame(self.tab_bios, text=" Carpeta 'data' de Pandora ", bg="#141419", fg="#00f0ff")
        f_destino.pack(fill="x", padx=20, pady=5)
        tk.Entry(f_destino, textvariable=self.destino_path, width=50).pack(side="left", padx=5)
        tk.Button(f_destino, text="...", command=lambda: self.destino_path.set(filedialog.askdirectory())).pack(side="right", padx=5)

        # Consola de Texto
        self.txt_log = tk.Text(self.tab_bios, height=12, bg="black", fg="#39ff14")
        self.txt_log.pack(pady=10, padx=20, fill="both", expand=True)

        # 🎛️ PANEL DE CONTROL PRINCIPAL
        f_botones = tk.Frame(self.tab_bios, bg="#141419")
        f_botones.pack(pady=10)

        self.btn_iniciar = tk.Button(f_botones, text="▶️ INICIAR INYECCIÓN", bg="#252530", fg="white", font=("Arial", 10, "bold"),command=self.procesar_bios)
        self.btn_iniciar.pack(side="left", padx=10)

        # 🛑 EL BOTÓN DE STOP QUE NECESITAS
        self.btn_stop = tk.Button(f_botones, text="🛑 STOP", bg="#ff0055", fg="white", font=("Arial", 10, "bold"), command=self.detener_proceso, state="disabled")
        self.btn_stop.pack(side="left", padx=10)

    def detener_proceso(self):
        """ Cambia el estado para frenar el bucle de copia """
        self.corriendo = False
        self.txt_log.insert(tk.END, "\n🛑 [SISTEMA] ¡Proceso detenido por el usuario!\n")
        self.btn_stop.config(state="disabled")
        self.btn_iniciar.config(state="normal")

    def procesar_bios(self):
        origen = self.origen_path.get()
        destino = self.destino_path.get()
        
        if not origen or not destino:
            messagebox.showwarning("Error", "Selecciona ambas carpetas.")
            return

        self.btn_stop.config(state="normal")
        self.txt_log.delete("1.0", tk.END)self.txt_log.insert(tk.END, "=== ⚙️ Escaneando pack desorganizado recursivamente... ===\n")
        for archivo_bios, (subcarpeta, desc) in PANDORA_BIOS_MAP.items():
            if not self.bios_corriendo:
                break
            self.root.update()
            ruta_origen = None
            for raiz, _, archivos in os.walk(origen)
            :if archivo_bios in archivos:
                ruta_origen = os.path.join(raiz, archivo_bios)
                break
            if ruta_origen:
                dest_dir = os.path.join(destino, subcarpeta)
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(ruta_origen, os.path.join(dest_dir, archivo_bios))
                self.txt_log.insert(tk.END, f"[✅ REPARADO] {archivo_bios} -> {subcarpeta}/\n")
                else:self.txt_log.insert(tk.END, f"[🔍 Faltante] {archivo_bios} ({desc})\n")
                self.txt_log.see(tk.END)if self.bios_corriendo:self.txt_log.insert(tk.END, "\n=== ✨ Gestión de BIOS Finalizada ===\n")
                messagebox.showinfo("Éxito", "Estructura de BIOS reparada correctamente.")
                self.btn_iniciar.config(state="normal")
                self.btn_stop.config(state="disabled")
                self.bios_corriendo = False

# =========================================================================# 💵 BARRA DE MONETIZACIÓN COMERCIAL# =========================================================================
def crear_barra_licencia(self):
   is_free = not self.manager.es_premium
   color_bg = "#ff0055" if is_free else "#39ff14"
texto = f"⚠️ VERSIÓN FREE: Límite de {self.manager.LIMITE_VERSION_FREE} juegos por tanda" if is_free else "🔓 VERSIÓN PREMIUM ACTIVA (Sin Límites)"
lbl_status = tk.Label(self.root, text=texto, font=("Consolas", 10, "bold"), bg=color_bg
                      , fg="black" if not is_free else "white", pady=4)
lbl_status.pack(fill="x", side="bottom")
if name == "main":root = tk.Tk()
app = PandarcadeMainWindow(root)root.mainloop()
