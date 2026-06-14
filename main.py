import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from organizer import PandarcadeCore  # Importamos el motor lógico que acabas de subir

class PandarcadeInjectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("💥 Pandarcade ROM Injector PRO v1.0 [100% RAW & OFFLINE]")
        self.root.geometry("680x540")
        self.root.resizable(False, False)
        
        # Conectamos el motor lógico pasándole nuestra consola visual de logs
        self.core = PandarcadeCore(self.log)
        
        # Variables de control de rutas
        self.ruta_origen = tk.StringVar()
        self.ruta_destino = tk.StringVar()
        
        self.crear_componentes()

    def crear_componentes(self):
        # --- TÍTULO PRINCIPAL ---
        lbl_titulo = tk.Label(self.root, text="PANDARCADE ROM INJECTOR", font=("Arial", 16, "bold"), fg="#1e272e")
        lbl_titulo.pack(pady=10)
        
        lbl_sub = tk.Label(self.root, text="Optimizador de almacenamiento en crudo para sistemas Arcade", font=("Arial", 10, "italic"), fg="#57606f")
        lbl_sub.pack(pady=2)
        
        # --- PANEL DE SELECCIÓN DE RUTAS ---
        frame_rutas = tk.LabelFrame(self.root, text=" 📁 Configuración de Unidades y Directorios ", font=("Arial", 10, "bold"), padx=15, pady=15)
        frame_rutas.pack(fill="x", padx=20, pady=10)
        
        # Origen
        tk.Label(frame_rutas, text="Memoria de Origen (SD/PC):", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(frame_rutas, textvariable=self.ruta_origen, width=52).grid(row=0, column=1, padx=5)
        tk.Button(frame_rutas, text="Examinar...", command=self.buscar_origen, bg="#ced6e0").grid(row=0, column=2, padx=2)
        
        # Destino
        tk.Label(frame_rutas, text="Memoria de Destino (USB):", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(frame_rutas, textvariable=self.ruta_destino, width=52).grid(row=1, column=1, padx=5)
        tk.Button(frame_rutas, text="Examinar...", command=self.buscar_destino, bg="#ced6e0").grid(row=1, column=2, padx=2)

        # --- PANEL DE REGISTRO / LOGS ---
        frame_logs = tk.LabelFrame(self.root, text=" 🖥️ Consola de Proceso local en tiempo real ", font=("Arial", 10, "bold"), padx=10, pady=10)
        frame_logs.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.txt_logs = tk.Text(frame_logs, height=10, width=75, font=("Consolas", 9), bg="#2f3542", fg="#7bed9f")
        self.txt_logs.pack(side="left", fill="both", expand=True)
        
        scroll = tk.Scrollbar(frame_logs, command=self.txt_logs.yview)
        scroll.pack(side="right", fill="y")
        self.txt_logs.config(yscrollcommand=scroll.set)
        
        self.log("Sistema Pandarcade inicializado con éxito.")
        self.log("Core conectado. Listo para purga y optimización en crudo.")

    def buscar_origen(self):
        dir_sel = filedialog.askdirectory(title="Selecciona la carpeta origen de tus juegos")
        if dir_sel:
            self.ruta_origen.set(dir_sel)
            self.log(f"Ruta de origen asignada: {dir_sel}")

    def buscar_destino(self):
        dir_sel = filedialog.askdirectory(title="Selecciona la raíz de tu memoria USB destino")
        if dir_sel:
            self.ruta_destino.set(dir_sel)
            self.log(f"Ruta de destino asignada: {dir_sel}")

    def log(self, mensaje):
        self.txt_logs.insert(tk.END, f">> {mensaje}\n")
        self.txt_logs.see(tk.END)
        self.root.update_idletasks() # Fuerza a la ventana a actualizar el texto en vivo

    def ejecutar_proceso_maestro(self):
        orig = self.ruta_origen.get()
        dest = self.ruta_destino.get()
        
        if not orig or not dest:
            messagebox.showerror("Error de Configuración", "Por favor, asigna ambas rutas antes de iniciar.")
            return
            
        # Desactivamos el botón temporalmente para evitar clics dobles lentos
        btn_ejecutar.config(state="disabled", bg="#747d8c")
        
        self.log("🚀 INICIANDO MODALIDAD EN CRUDO...")
        
        # 1. Llamamos al script purgador de duplicados y basura multimedia
        exito_purga = self.core.purgar_y_extraer_en_crudo(orig)
        
        if exito_purga:
            self.log("⚡ Purga completada. Iniciando inyección automática de listados...")
            # Aquí buscaremos el archivo de historial en el escritorio si existe para clasificar
            ruta_txt_escritorio = os.path.expanduser("~/Desktop/lista_juegos.txt")
            
            if os.path.exists(ruta_txt_escritorio):
                self.core.clasificar_por_historial(ruta_txt_escritorio, orig, dest)
            else:
                self.log("ℹ️ No se encontró 'lista_juegos.txt' en el Escritorio. Se asume organización manual previa.")
            
            messagebox.showinfo("¡Proceso Terminado!", "Tu catálogo ha sido purgado en crudo y estructurado correctamente.")
        else:
            messagebox.showerror("Fallo del Sistema", "Ocurrió un error al intentar acceder a los directorios.")
            
        btn_ejecutar.config(state="normal", bg="#2ed573")
        self.log("🏁 Sistema libre. Listo para una nueva unidad.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PandarcadeInjectorGUI(root)
    
    # Botón de ejecución maestro abajo en la ventana conectado a la función real
    btn_ejecutar = tk.Button(root, text="🔥 INICIAR OPTIMIZACIÓN Y MIGRACIÓN EN CRUDO", 
                             font=("Arial", 11, "bold"), bg="#2ed573", fg="white", 
                             padx=20, pady=8, command=app.ejecutar_proceso_maestro)
    btn_ejecutar.pack(pady=12)
    
    root.mainloop()
