# main.py
import os
import time
import webbrowser
import threading  # Para evitar que la interfaz se congele al inyectar
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Importamos tu backend corregido desde mcgames_builder.py
from mcgames_builder import PandoraUniversalManager

class PandarcadeMainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Pandarcade - BIOS & ROMs")
        self.root.geometry("700x450")
        self.root.configure(bg="#1e1e2e")  # Fondo oscuro elegante

        # 1. ENLAZAR EL BACKEND (Pasamos el método de log para ver el progreso en vivo)
        self.manager = PandoraUniversalManager(log_callback=self.actualizar_consola_log)

        # Variables de control para las rutas
        self.ruta_origen_var = tk.StringVar()
        self.ruta_destino_var = tk.StringVar()

        # ==========================================
        # 2. DISEÑO DE LA INTERFAZ GRÁFICA (GUI)
        # ==========================================
        
        # --- TÍTULO PRINCIPAL ---
        lbl_titulo = tk.Label(self.root, text="PANDARCADE ROM INJECTOR", font=("Arial", 16, "bold"), bg="#1e1e2e", fg="#39ff14")
        lbl_titulo.pack(pady=15)

        # --- SELECCIÓN DE RUTA DE ORIGEN ---
        f_origen = tk.Frame(self.root, bg="#1e1e2e")
        f_origen.pack(fill="x", padx=20, pady=5)
        tk.Label(f_origen, text="Carpeta de ROMs:", width=15, anchor="w", bg="#1e1e2e", fg="white", font=("Arial", 10)).pack(side="left")
        tk.Entry(f_origen, textvariable=self.ruta_origen_var, font=("Arial", 10), bg="#2d2d3d", fg="white", insertbackground="white").pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(f_origen, text="Buscar...", command=self.seleccionar_origen, bg="#39ff14", fg="black", activebackground="#00f0ff", font=("Arial", 9, "bold")).pack(side="right")

        # --- SELECCIÓN DE RUTA DE DESTINO ---
        f_destino = tk.Frame(self.root, bg="#1e1e2e")
        f_destino.pack(fill="x", padx=20, pady=5)
        tk.Label(f_destino, text="Destino (USB/SD):", width=15, anchor="w", bg="#1e1e2e", fg="white", font=("Arial", 10)).pack(side="left")
        tk.Entry(f_destino, textvariable=self.ruta_destino_var, font=("Arial", 10), bg="#2d2d3d", fg="white", insertbackground="white").pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(f_destino, text="Buscar...", command=self.seleccionar_destino, bg="#39ff14", fg="black", activebackground="#00f0ff", font=("Arial", 9, "bold")).pack(side="right")

        # --- CONSOLA DE TEXTO (LOGS EN VIVO) ---
        tk.Label(self.root, text="Consola de Operaciones:", bg="#1e1e2e", fg="#a5a5b5", font=("Arial", 9, "italic")).pack(anchor="w", padx=20, pady=(15, 2))
        self.txt_log = tk.Text(self.root, height=10, bg="#0f0f17", fg="#39ff14", font=("Consolas", 9.5), wrap="word")
        self.txt_log.pack(fill="both", expand=True, padx=20, pady=5)

        # --- BOTÓN DE INYECCIÓN ACCIÓN CONTRA LÍMITES ---
        self.btn_inyectar = tk.Button(
            self.root, text="🚀 INICIAR INYECCIÓN DE ROMS", font=("Arial", 11, "bold"),
            bg="#00f0ff", fg="black", activebackground="#39ff14", pady=6, command=self.ejecutar_inyeccion_hilo
        )
        self.btn_inyectar.pack(fill="x", padx=20, pady=15)

        # --- BARRA INFERIOR DE LICENCIA DIARIA (Rendermétodo inicial) ---
        self.f_status = tk.Frame(self.root, pady=4)
        self.f_status.pack(fill="x", side="bottom")
        
        self.lbl_status = tk.Label(self.f_status, font=("Arial", 9, "bold"), fg="black")
        self.lbl_status.pack(side="left", padx=10)

        self.btn_donar = tk.Button(
            self.f_status, text="🎁 Apoyar Proyecto (PayPal)", font=("Arial", 8, "bold"),
            bg="black", fg="#39ff14", activebackground="#00f0ff", command=self.abrir_paypal,
            relief="groove", cursor="hand2", padx=5
        )
        self.btn_donar.pack(side="right", padx=10)

        # Pintamos el estado actual por primera vez
        self.actualizar_barra_licencia()

    # ==========================================
    # 3. LÓGICA DE CONTROL Y EVENTOS
    # ==========================================
    def seleccionar_origen(self):
        ruta = filedialog.askdirectory(title="Selecciona la carpeta donde guardas tus ROMs")
        if ruta:
            self.ruta_origen_var.set(ruta)

    def _guardar_txt_pandora(self, ruta_destino, juegos_indexados):
        """Genera el archivo de texto de índices plano requerido por las consolas Pandora Box."""
        try:
            ruta_txt = os.path.join(ruta_destino, "rom_list.txt")
            with open(ruta_txt, "w", encoding="utf-8") as f:
                for emu, nombre_archivo in juegos_indexados:
                    nombre_juego, _ = os.path.splitext(nombre_archivo)
                    f.write(f"{emu}|{nombre_archivo}|{nombre_juego}\n")
            self.log("📝 Base de datos rom_list.txt actualizada con éxito.")
            
            # 🔥 LLAMADA AUTOMÁTICA NATIVA AL INSTALADOR DE PANDORA 3D
            self._guardar_install_txt_3d(ruta_destino, juegos_indexados)
            
        except Exception as e:
            self.log(f"⚠️ No se pudo generar el índice TXT: {e}")

    def _guardar_install_txt_3d(self, ruta_destino, juegos_indexados):
        """Genera de forma automática el archivo install.txt requerido por Pandora 3D / Saga."""
        try:
            ruta_install = os.path.join(ruta_destino, "install.txt")
            with open(ruta_install, "w", encoding="utf-8") as f:
                for emu, nombre_archivo in juegos_indexados:
                    nombre_juego, _ = os.path.splitext(nombre_archivo)
                    
                    # 🎮 DETECCIÓN Y PARÁMETROS ESPECIALES PARA KILLER INSTINCT (.CHD)
                    if "killer" in nombre_juego.lower() and nombre_archivo.lower().endswith('.chd'):
                        self.log(f"🎯 Configurando parámetros avanzados para Killer Instinct (.chd)")
                        f.write(f"{emu},{nombre_archivo},{nombre_juego},1,MAME_HARDWARE_MIPS,LAUNCH_DIRECT_CHD\n")
                    else:
                        f.write(f"{emu},{nombre_archivo},{nombre_juego},0\n")
                        
            self.log("🔥 Archivo 'install.txt' para Pandora 3D generado automáticamente.")
        except Exception as e:
            self.log(f"⚠️ No se pudo generar el archivo install.txt: {e}")

    def _guardar_xml_universal(self, ruta_destino, juegos_indexados):
        """Genera el XML de metadatos utilizando escrituras puras para no requerir librerías complejas."""
        try:
            ruta_xml = os.path.join(ruta_destino, "games_metadata.xml")
            with open(ruta_xml, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                f.write('<gameList>\n')
                for emu, nombre_archivo in juegos_indexados:
                    nombre_juego, _ = os.path.splitext(nombre_archivo)
                    f.write('  <game>\n')
                    f.write(f'    <path>./{emu}/{nombre_archivo}</path>\n')
                    f.write(f'    <name>{nombre_juego}</name>\n')
                    f.write(f'    <system>{emu}</system>\n')
                    f.write('  </game>\n')
                f.write('</gameList>\n')
            self.log("📝 Metadatos estructurados games_metadata.xml actualizados.")
        except Exception as e:
            self.log(f"⚠️ No se pudo generar la base de datos XML: {e}")
