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

    def seleccionar_destino(self):
        ruta = filedialog.askdirectory(title="Selecciona la partición o carpeta de tu Pandora Box")
        if ruta:
            self.ruta_destino_var.set(ruta)

    def actualizar_consola_log(self, mensaje):
        """ Agrega texto en tiempo real a la caja negra de logs """
        self.txt_log.insert(tk.END, f"{mensaje}\n")
        self.txt_log.see(tk.END)  # Autoscroll automático al final

    def actualizar_barra_licencia(self):
        """ Redibuja dinámicamente el color y el texto de la barra según el límite de 24h """
        puede_continuar, mensaje_tiempo = self.manager.verificar_limite_tiempo()
        
        color_bg = "#39ff14" if puede_continuar else "#ff0055"
        self.f_status.config(bg=color_bg)
        self.lbl_status.config(bg=color_bg)
        self.btn_donar.config(fg="#39ff14" if puede_continuar else "#ff0055")

        if puede_continuar:
            # resultado de verificar_limite_tiempo da los juegos ya usados en las últimas 24h
            juegos_usados = mensaje_tiempo
            restantes = self.manager.LIMITE_VERSION_FREE - juegos_usados
            self.lbl_status.config(text=f"📶 MODO FREEMIUM: Disponibles hoy {restantes} de {self.manager.LIMITE_VERSION_FREE} juegos.")
            self.btn_inyectar.config(state="normal", bg="#00f0ff")
        else:
            self.lbl_status.config(text=mensaje_tiempo)
            self.btn_inyectar.config(state="disabled", bg="#555555")

    def ejecutar_inyeccion_hilo(self):
        """ Lanza la inyección en un hilo separado para que la ventana no se congele """
        origen = self.ruta_origen_var.get()
        destino = self.ruta_destino_var.get()

        if not origen or not destino:
            messagebox.showwarning("Rutas vacías", "Por favor, selecciona tanto la carpeta de origen como la de destino.")
            return

        # Desactivamos el botón temporalmente para evitar doble clic
        self.btn_inyectar.config(state="disabled")
        
        # Creamos y arrancamos el hilo secundario de transferencia
        hilo = threading.Thread(target=self._proceso_segundo_plano, args=(origen, destino), daemon=True)
        hilo.start()

    def _proceso_segundo_plano(self, origen, destino):
        """ Corre la lógica pesada de mcgames_builder sin trabar los gráficos """
        self.txt_log.delete("1.0", tk.END)  # Limpiar consola anterior
        
        # Ejecuta la inyección del backend
        resultado = self.manager.purgar_y_extraer_en_crudo(origen, destino)

        # Al terminar, actualizamos la GUI desde el hilo principal de forma segura
        self.root.after(0, self.finalizar_proceso_gui, resultado)

    def finalizar_proceso_gui(self, resultado):
        """ Retorna el control a la pantalla y recarga el contador de bloqueos """
        self.actualizar_barra_licencia()
        
        if resultado == "exito":
            messagebox.showinfo("¡Inyección Completada!", "Tus ROMs se han procesado, purgado y listado con éxito.")
        elif resultado == "limite_demo":
            messagebox.showwarning("Límite alcanzado", "El proceso terminó de forma parcial porque alcanzaste el tope de la versión gratuita.")
        elif resultado == "bloqueado":
            messagebox.showerror("Acción Bloqueada", "No se transfirieron archivos. Por favor, espera a que expire el plazo diario.")
        elif resultado == "vacio":
            messagebox.showinfo("Proceso Terminado", "No se encontraron nuevas ROMs compatibles en el directorio origen.")

    def abrir_paypal(self):
        enlace_paypal = "https://paypal.com"
        webbrowser.open(enlace_paypal)


if __name__ == "__main__":
    root = tk.Tk()
    app = PandarcadeMainWindow(root)
    root.mainloop()
