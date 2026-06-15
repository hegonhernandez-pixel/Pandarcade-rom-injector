import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- CONFIGURACIÓN COMERCIAL (Tu Backend) ---
class PandoraUniversalManager:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        # 🔒 Límite de la versión de evaluación comercial
        self.LIMITE_VERSION_FREE = 25
        self.es_premium = False # Cambiar a True si el usuario ingresa serial

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
        self.root.geometry("800x600")
        
        # Instanciamos tu manager para validar límites de copia
        self.manager = PandoraUniversalManager(log_callback=self.append_log_roms)
        
        # 🛑 Variables de control para botones STOP independientes
        self.roms_corriendo = False
        self.bios_corriendo = False

        # Configuración estética de las pestañas (Diseño Arcade)
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background="#141419", borderwidth=0)
        style.configure("TNotebook.Tab", background="#252530", foreground="white", font=("Arial", 10), padding=)
        style.map("TNotebook.Tab", background=[("selected", "#00f0ff")], foreground=[("selected", "#000000")])

        # Interfaz Base (Pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_roms = tk.Frame(self.notebook, bg="#141419")
        self.tab_bios = tk.Frame(self.notebook, bg="#141419")

        self.notebook.add(self.tab_roms, text=" 🎮 ROMs ")
        self.notebook.add(self.tab_bios, text=" 🛠️ BIOS ")

        # Montar el contenido de ambas ventanas
        self.setup_roms_tab()
        self.setup_bios_tab()
        self.crear_barra_licencia()

    # =========================================================================
    # 🎮 PESTAÑA ROMS (CONSTRUIDA Y CORREGIDA)
    # =========================================================================
    def setup_roms_tab(self):
        self.roms_origen_path = tk.StringVar()
        self.roms_destino_path = tk.StringVar()

        # Configuración de Rutas de Juegos
        f_origen_r = tk.LabelFrame(self.tab_roms, text=" Carpeta origen de ROMs en PC ", bg="#141419", fg="#00f0ff", font=("Arial", 10, "bold"))
        f_origen_r.pack(fill="x", padx=20, pady=5)
        tk.Entry(f_origen_r, textvariable=self.roms_origen_path, width=50, bg="#1c1c24", fg="#00f0ff", insertbackground="white").pack(side="left", padx=5, expand=True, fill="x")
        tk.Button(f_origen_r, text="...", font=("Arial", 9, "bold"), command=lambda: self.roms_origen_path.set(filedialog.askdirectory())).pack(side="right", padx=5)

        f_destino_r = tk.LabelFrame(self.tab_roms, text=" Carpeta de emulador en Pandora (Ej: games/data/mame78) ", bg="#141419", fg="#00f0ff", font=("Arial", 10, "bold"))
        f_destino_r.pack(fill="x", padx=20, pady=5)
        tk.Entry(f_destino_r, textvariable=self.roms_destino_path, width=50, bg="#1c1c24", fg="#00f0ff", insertbackground="white").pack(side="left", padx=5, expand=True, fill="x")
        tk.Button(f_destino_r, text="...", font=("Arial", 9, "bold"), command=lambda: self.roms_destino_path.set(filedialog.askdirectory())).pack(side="right", padx=5)

        # Consola de texto para ROMs
        self.txt_log_roms = tk.Text(self.tab_roms, height=12, bg="black", fg="#39ff14", font=("Consolas", 9))
        self.txt_log_roms.pack(pady=10, padx=20, fill="both", expand=True)

        # Panel de botones Arcade para ROMs
        f_botones_r = tk.Frame(self.tab_roms, bg="#141419")
        f_botones_r.pack(pady=10)

        self.btn_iniciar_roms = tk.Button(f_botones_r, text="▶️ INYECTAR ROMS", bg="#252530", fg="white", font=("Arial", 10, "bold"), command=self.procesar_roms, relief="groove", cursor="hand2")
        self.btn_iniciar_roms.pack(side="left", padx=10)

        self.btn_stop_roms = tk.Button(f_botones_r, text="🛑 STOP", bg="#ff0055", fg="white", font=("Arial", 10, "bold"), command=self.detener_roms, state="disabled", relief="groove", cursor="hand2")
        self.btn_stop_roms.pack(side="left", padx=10)

    def append_log_roms(self, mensaje):
        self.txt_log_roms.insert(tk.END, mensaje + "\n")
        self.txt_log_roms.see(tk.END)

    def detener_roms(self):
        self.roms_corriendo = False
        self.append_log_roms("\n🛑 [SISTEMA] Transferencia de juegos abortada por el usuario.\n")
        self.btn_stop_roms.config(state="disabled")
        self.btn_iniciar_roms.config(state="normal")

    def procesar_roms(self):
        origen = self.roms_origen_path.get()
        destino = self.roms_destino_path.get()

        if not origen or not destino:
            messagebox.showwarning("Error", "Selecciona las rutas de origen y destino de ROMs.")
            return

        # Escanear archivos en la carpeta de origen
        lista_juegos = [f for f in os.listdir(origen) if os.path.isfile(os.path.join(origen, f))]

        # 🔒 Validación comercial del límite de evaluación (25 juegos)
        if not self.manager.es_premium and len(lista_juegos) > self.manager.LIMITE_VERSION_FREE:
            messagebox.showwarning("Versión Trial", f"Límite excedido.\nSolo se procesarán las primeras {self.manager.LIMITE_VERSION_FREE} ROMs de la carpeta.")
            lista_juegos = lista_juegos[:self.manager.LIMITE_VERSION_FREE]

        self.roms_corriendo = True
        self.btn_iniciar_roms.config(state="disabled")
        self.btn_stop_roms.config(state="normal")
        self.txt_log_roms.delete("1.0", tk.END)
        self.append_log_roms("=== ▶️ Iniciando transferencia de ROMs... ===\n")

        for juego in lista_juegos:
            if not self.roms_corriendo:
                break
            self.root.update()

            # Evitar tocar extensiones de sistema (Tu filtro de exclusión de seguridad)
            if juego.lower() in ['neogeo.zip', 'pgm.zip'] or juego.lower().endswith(('.bin', '.bios')):
                self.append_log_roms(f"[🛡️ FILTRADO] Archivo del sistema ignorado de forma segura: {juego}")
                continue

            try:
                shutil.copy2(os.path.join(origen, juego), os.path.join(destino, juego))
                self.append_log_roms(f"[✅ COPIADO] {juego}")
            except Exception as e:
                self.append_log_roms(f"[❌ ERROR] No se pudo copiar {juego}: {e}")

        if self.roms_corriendo:
            self.append_log_roms("\n=== ✨ Inyección de Juegos Finalizada ===\n")
            messagebox.showinfo("Éxito", "Proceso de ROMs completado.")
            self.btn_iniciar_roms.config(state="normal")
            self.btn_stop_roms.config(state="disabled")
            self.roms_corriendo = False

    # =========================================================================
    # 🛠️ PESTAÑA BIOS (ESTRUCTURA DE TU CÓDIGO)
    # =========================================================================
    def setup_bios_tab(self):
        self.origen_path = tk.StringVar()
        self.destino_path = tk.StringVar()

        # Configuración de Rutas
        f_origen = tk.LabelFrame(self.tab_bios, text=" Origen de BIOS ", bg="#141419", fg="#00f0ff", font=("Arial", 10, "bold"))
        f_origen.pack(fill="x", padx=20, pady=5)
        tk.Entry(f_origen, textvariable=self.origen_path, width=50, bg="#1c1c24", fg="#00f0ff", insertbackground="white").pack(side="left", padx=5, expand=True, fill="x")
        tk.Button(f_origen, text="...", font=("Arial", 9, "bold"), command=lambda: self.origen_path.set(filedialog.askdirectory())).pack(side="right", padx=5)

        f_destino = tk.LabelFrame(self.tab_bios, text=" Carpeta 'data' de Pandora ", bg="#141419", fg="#00f0ff", font=("Arial", 10, "bold"))
        f_destino.pack(fill="x", padx=20, pady=5)
        tk.Entry(f_destino, textvariable=self.destino_path, width=50, bg="#1c1c24", fg="#00f0ff", insertbackground="white").pack(side="left", padx=5, expand=True, fill="x")
        tk.Button(f_destino, text="...", font=("Arial", 9, "bold"), command=lambda: self.destino_path.set(filedialog.askdirectory())).pack(side="right", padx=5)

        # Consola de Texto
        self.txt_log = tk.Text(self.tab_bios, height=12, bg="black", fg="#39ff14", font=("Consolas", 9))
        self.txt_log.pack(pady=10, padx=20, fill="both", expand=True)

        # 🎛️ PANEL DE CONTROL PRINCIPAL BIOS
        f_botones = tk.Frame(self.tab_bios, bg="#141419")
        f_botones.pack(pady=10)

        self.btn_iniciar = tk.Button(f_botones, text="▶️ INICIAR INYECCIÓN", bg="#252530", fg="white", font=("Arial", 10, "bold"), command=self.procesar_bios, relief="groove", cursor="hand2")
        self.btn_iniciar.pack(side="left", padx=10)

        self.btn_stop = tk.Button(f_botones, text="🛑 STOP", bg="#ff0055", fg="white", font=("Arial", 10, "bold"), command=self.detener_proceso, state="disabled", relief="groove", cursor="hand2")
        self.btn_stop.pack(side="left", padx=10)

    def detener_proceso(self):
        self.bios_corriendo = False
        self.txt_log.insert(tk.END, "\n🛑 [SISTEMA] ¡Proceso de BIOS detenido por el usuario!\n")
        self.btn_stop.config(state="disabled")
        self.btn_iniciar.config(state="normal")

    def procesar_bios(self):
        # 🔥 NOTA: Todo este bloque debe llevar 8 espacios de indentación hacia la derecha
        origen = self.origen_path.get()
        destino = self.destino_path.get()
        
        if not origen or not destino:
            messagebox.showwarning("Error", "Selecciona ambas carpetas.")
            return

        self.bios_corriendo = True
        self.btn_iniciar.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.insert(tk.END, "=== Iniciando inyección recursiva de BIOS... ===\n")
        # ... (aquí continúa el resto del bucle for de las BIOS que ya tienes)
        for archivo_bios, (subcarpeta, desc) in PANDORA_BIOS_MAP.items():
            if not self.bios_corriendo:
                break
            self.root.update()

            # Búsqueda automática e inteligente en packs desorganizados
            ruta_origen = None
            for raiz, _, archivos in os.walk(origen):
                if archivo_bios in archivos:
                    ruta_origen = os.path.join(raiz, archivo_bios)
                    break

            if ruta_origen:
                dest_dir = os.path.join(destino, subcarpeta)
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(ruta_origen, os.path.join(dest_dir, archivo_bios))
                self.txt_log.insert(tk.END, f"[✅ REPARADO] {archivo_bios} -> {subcarpeta}/\n")
            else:
                self.txt_log.insert(tk.END, f"[🔍 Faltante] {archivo_bios} ({desc})\n")
                
            self.txt_log.see(tk.END)

        if self.bios_corriendo:
            self.txt_log.insert(tk.END, "\n=== ✨ Inyección Finalizada con Éxito ===\n")
            messagebox.showinfo("Éxito", "Estructura de BIOS completada.")
            self.btn_iniciar.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.bios_corriendo = False

    # Barra informativa de estatus de la licencia de la app
    def crear_barra_licencia(self):
        color_bg = "#ff0055" if not self.manager.es_premium else "#39ff14"
        texto = f"⚠️ MODO EVALUACIÓN: Máximo {self.manager.LIMITE_VERSION_FREE} ROMs por ejecución" if not self.manager.es_premium else "🔓 VERSIÓN PREMIUM - SIN RESTRICCIONES"
        
        lbl_status = tk.Label(self.root, text=texto, font=("Arial", 10, "bold"), bg=color_bg, fg="white" if not self.manager.es_premium else "black", pady=4)
        lbl_status.pack(fill="x", side="bottom")

# 🔥 Disparador principal del script (Va pegado al borde izquierdo de la pantalla)
if __name__ == "__main__":
    root = tk.Tk()
    app = PandarcadeMainWindow(root)
    root.mainloop()
