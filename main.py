import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- IMPORTACIONES LOCALES DESDE TU GITHUB ---
from organizer import PandarcadeCore
from detector import SonyFormatDetector
from DBManager import PandarcadeDatabase

class PandarcadeInjectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("💥 Pandarcade ROM Injector PRO v1.0 [100% RAW & OFFLINE]")
        self.root.geometry("680x560")
        self.root.resizable(False, False)
        
        # Configuración de estilo visual básico
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Conectamos los componentes del sistema
        self.core = PandarcadeCore(self.log)
        self.detector = SonyFormatDetector(self.log)
        self.db = PandarcadeDatabase()
        
        # Variables de control de rutas
        self.ruta_origen = tk.StringVar()
        self.ruta_destino = tk.StringVar()
        
        # Creación de los elementos de la ventana
        self.crear_componentes()

    def crear_componentes(self):
        main_frame = ttk.Frame(self.root, padding="15 15 15 15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        lbl_titulo = ttk.Label(
            main_frame, 
            text="PANDARCADE ROM INJECTOR", 
            font=("Arial", 16, "bold"), 
            foreground="#2c3e50"
        )
        lbl_titulo.pack(pady=(0, 15))
        
        # Sección: Selección de Rutas
        frame_rutas = ttk.LabelFrame(main_frame, text=" Configuración de Rutas ", padding="10 10 10 10")
        frame_rutas.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(frame_rutas, text="Carpeta de ROMs (Origen):").grid(row=0, column=0, sticky=tk.W, pady=5)
        entry_origen = ttk.Entry(frame_rutas, textvariable=self.ruta_origen, width=55)
        entry_origen.grid(row=0, column=1, padx=5, pady=5)
        btn_buscar_origen = ttk.Button(frame_rutas, text="Buscar...", command=self.seleccionar_origen)
        btn_buscar_origen.grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(frame_rutas, text="Unidad Pandora (Destino):").grid(row=1, column=0, sticky=tk.W, pady=5)
        entry_destino = ttk.Entry(frame_rutas, textvariable=self.ruta_destino, width=55)
        entry_destino.grid(row=1, column=1, padx=5, pady=5)
        btn_buscar_destino = ttk.Button(frame_rutas, text="Buscar...", command=self.seleccionar_destino)
        btn_buscar_destino.grid(row=1, column=2, padx=5, pady=5)
        
        # Sección: Consola Visual
        frame_consola = ttk.LabelFrame(main_frame, text=" Consola de Operación ", padding="10 10 10 10")
        frame_consola.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.consola_texto = tk.Text(
            frame_consola, 
            height=12, 
            wrap=tk.WORD, 
            background="#1e1e1e", 
            foreground="#ffffff", 
            insertbackground="white",
            font=("Consolas", 10)
        )
        self.consola_texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.consola_texto.config(state=tk.DISABLED)
        
        scroll = ttk.Scrollbar(frame_consola, command=self.consola_texto.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.consola_texto.config(yscrollcommand=scroll.set)
        
        # Botón de Acción
        self.btn_iniciar = ttk.Button(
            main_frame, 
            text="🚀 INICIAR INYECCIÓN MASIVA", 
            command=self.iniciar_inyeccion
        )
        self.btn_iniciar.pack(fill=tk.X, ipady=8)

    def log(self, mensaje):
        if hasattr(self, 'consola_texto') and self.consola_texto:
            self.consola_texto.config(state=tk.NORMAL)
            self.consola_texto.insert(tk.END, f"{mensaje}\n")
            self.consola_texto.see(tk.END)
            self.consola_texto.config(state=tk.DISABLED)
        else:
            print(mensaje)

    def seleccionar_origen(self):
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta de tus juegos")
        if carpeta:
            self.ruta_origen.set(carpeta)
            self.log(f"📂 Origen configurado: {carpeta}")

    def seleccionar_destino(self):
        carpeta = filedialog.askdirectory(title="Selecciona la unidad de tu Pandora Box")
        if carpeta:
            self.ruta_destino.set(carpeta)
            self.log(f"💾 Destino configurado: {carpeta}")

    def iniciar_inyeccion(self):
        origen = self.ruta_origen.get()
        destino = self.ruta_destino.get()

        if not origen or not os.path.exists(origen):
            messagebox.showerror("Error", "⚠️ Selecciona una carpeta de origen válida.")
            return

        if not destino or not os.path.exists(destino):
            messagebox.showerror("Error", "⚠️ Selecciona la ruta de tu tarjeta Pandora Box.")
            return

        self.btn_iniciar.config(state=tk.DISABLED)
        self.log("🚀 Iniciando el proceso de inyección de ROMs...")

        # Hilo secundario para evitar bloqueos de la GUI
        hilo = threading.Thread(target=self._proceso_segundo_plano, args=(origen, destino), daemon=True)
        hilo.start()

    def _proceso_segundo_plano(self, origen, destino):
        try:
            resultado = self.core.clasificar_y_preparar(origen, destino)
            if resultado:
                self.log("🎉 ¡Proceso finalizado con éxito!")
                messagebox.showinfo("Éxito", "¡Juegos inyectados correctamente!")
            else:
                self.log("❌ Hubo un inconveniente durante la clasificación.")
        except Exception as e:
            self.log(f"💥 Error crítico: {str(e)}")
            messagebox.showerror("Error Crítico", str(e))
        finally:
            self.btn_iniciar.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = PandarcadeInjectorGUI(root)
    root.mainloop()
