import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
# Importamos la lógica que acabamos de crear arriba
from bios_logic import ejecutar_inyeccion_bios 

class PandarcadeMainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pandarcade Rom Injector & Tools")
        self.root.geometry("700x500")

        # 1. CREAR EL SISTEMA DE PESTAÑAS (Notebook)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # 2. DEFINIR LAS PESTAÑAS
        self.tab_roms = ttk.Frame(self.notebook)
        self.tab_bios = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_roms, text=" 🎮 Inyector de ROMs ")
        self.notebook.add(self.tab_bios, text=" 🛠️ Gestor de BIOS ")

        # Inicializar contenido de las pestañas
        self.setup_roms_tab()
        self.setup_bios_tab()

    def setup_roms_tab(self):
        """Aquí va tu código actual del inyector de ROMs que tienes en GitHub"""
        lbl = tk.Label(self.tab_roms, text="Tu interfaz actual de ROMs va aquí.", font=("Arial", 12))
        lbl.pack(pady=50)

    def setup_bios_tab(self):
        """Nueva pestaña integrada para solucionar el problema de las BIOS perdidas"""
        self.origen_path = tk.StringVar()
        self.destino_path = tk.StringVar()

        # Marco Origen
        frame_origen = tk.LabelFrame(self.tab_bios, text=" 1. Pack de BIOS (Revueltas o en subcarpetas) ", font=("Arial", 9, "bold"), padx=10, pady=10)
        frame_origen.pack(fill="x", padx=20, pady=10)
        tk.Entry(frame_origen, textvariable=self.origen_path, width=60, state="readonly").pack(side="left", padx=5)
        tk.Button(frame_origen, text="Examinar...", command=self.seleccionar_origen).pack(side="right", padx=5)

        # Marco Destino
        frame_destino = tk.LabelFrame(self.tab_bios, text=" 2. Carpeta Destino (Selecciona la carpeta 'data' de tu Pandora) ", font=("Arial", 9, "bold"), padx=10, pady=10)
        frame_destino.pack(fill="x", padx=20, pady=10)
        tk.Entry(frame_destino, textvariable=self.destino_path, width=60, state="readonly").pack(side="left", padx=5)
        tk.Button(frame_destino, text="Examinar...", command=self.seleccionar_destino).pack(side="right", padx=5)

        # Caja de Registro / Log técnico
        self.txt_log = tk.Text(self.tab_bios, height=12, width=80, font=("Courier", 9))
        self.txt_log.pack(pady=10, padx=20)
        self.txt_log.config(state="disabled")

        # Botón Procesar
        self.btn_procesar = tk.Button(self.tab_bios, text="REPARAR E INYECTAR BIOS", font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", command=self.procesar_bios_ui, state="disabled")
        self.btn_procesar.pack(pady=5)

    def seleccionar_origen(self):
        path = filedialog.askdirectory(title="Selecciona la carpeta de tu Pack de BIOS")
        if path:
            self.origen_path.set(path)
            self.evaluar_activacion_boton()

    def seleccionar_destino(self):
        path = filedialog.askdirectory(title="Selecciona la carpeta 'data' de tu Pandora")
        if path:
            if not os.path.basename(path) == "data" and not os.path.exists(os.path.join(path, "playstation")):
                messagebox.showwarning("Ruta Incorrecta", "Atención: Asegúrate de seleccionar la carpeta raíz llamada 'data' (la de tu captura).")
            self.destino_path.set(path)
            self.evaluar_activacion_boton()

    def evaluar_activacion_boton(self):
        if self.origen_path.get() and self.destino_path.get():
            self.btn_procesar.config(state="normal")

    def append_log(self, mensaje):
        """Función callback que la lógica usará para escribir en la interfaz."""
        self.txt_log.config(state="normal")
        self.txt_log.insert(tk.END, mensaje + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")
        self.root.update_idletasks()

    def procesar_bios_ui(self):
        # Limpiar la consola antes de iniciar
        self.txt_log.config(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.config(state="disabled")

        # Llamamos a la función del módulo lógico pasándole nuestro método de log
        total = ejecutar_inyeccion_bios(self.origen_path.get(), self.destino_path.get(), self.append_log)
        
        messagebox.showinfo("Proceso Terminado", f"¡Éxito! Se han organizado e inyectado {total} archivos de BIOS en sus emuladores correspondientes.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PandarcadeMainApp(root)
    root.mainloop()
