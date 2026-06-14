# main.py
import os
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from mcgames_builder import PandoraUniversalManager

class PandarcadeMainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Universal ROM Injector PRO - Suite de Evaluacion")
        self.root.geometry("620x510")
        self.root.configure(bg="#111111")
        
        self.procesando = False
        self.ruta_origen = tk.StringVar()
        self.ruta_destino = tk.StringVar()
        self.estado_texto = tk.StringVar(value="Estado: Modo Evaluacion Activo (Limite: 25 juegos por ejecucion)")
        
        self.manager_backend = PandoraUniversalManager(log_callback=self.ag)
        self.construir_interfaz_principal()

    def construir_interfaz_principal(self):
        tk.Label(
            self.root, text="UNIVERSAL ROM INJECTOR PRO", 
            font=("Arial", 14, "bold"), fg="#2ecc71", bg="#111111"
        ).pack(pady=15)

        # Botón 1: Origen
        frame_orig = tk.Frame(self.root, bg="#111111")
        frame_orig.pack(pady=6, fill='x', padx=35)
        tk.Entry(frame_orig, textvariable=self.ruta_origen, width=48, bg="#222222", fg="white", insertbackground="white").pack(side=tk.LEFT, padx=5)
        tk.Button(frame_orig, text="Carpeta Origen...", command=self._buscar_origen, bg="#333333", fg="white", width=15).pack(side=tk.LEFT)

        # Botón 2: Destino
        frame_dest = tk.Frame(self.root, bg="#111111")
        frame_dest.pack(pady=6, fill='x', padx=35)
        tk.Entry(frame_dest, textvariable=self.ruta_destino, width=48, bg="#222222", fg="white", insertbackground="white").pack(side=tk.LEFT, padx=5)
        tk.Button(frame_dest, text="Unidad SD/USB...", command=self._buscar_destino, bg="#333333", fg="white", width=15).pack(side=tk.LEFT)

        # Estado en pantalla
        tk.Label(self.root, textvariable=self.estado_texto, fg="#f1c40f", bg="#111111", font=("Arial", 9, "bold")).pack(pady=8)

        # Barra de progreso
        self.progreso = ttk.Progressbar(self.root, orient="horizontal", length=480, mode="indeterminate")
        self.progreso.pack(pady=5)

        # Monitor de actividad sanitizado
        tk.Label(self.root, text="Monitor de Inyeccion Activo:", fg="#888888", bg="#111111", font=("Arial", 8)).pack(anchor="w", padx=45)
        self.txt_consola = tk.Text(self.root, height=7, width=68, bg="#000000", fg="#39ff14", font=("CourierNew", 9))
        self.txt_consola.pack(pady=5)
        self.txt_consola.config(state="disabled")

        # Link Comercial Seguro (Sin marcas comerciales)
        self.lbl_comprar = tk.Label(
            self.root, 
            text="🔒 Desbloquea inyecciones ilimitadas para tus consolas arcade de forma inmediata", 
            fg="#3498db", bg="#111111", font=("Arial", 8, "underline", "bold"), cursor="hand2"
        )
        self.lbl_comprar.pack(pady=5)
        self.lbl_comprar.bind("<Button-1>", lambda e: webbrowser.open("https://tu-sitio-web-o-tienda.com"))

        # Botón Ejecutar
        self.btn_ejecutar = tk.Button(
            self.root, text="PROCESAR, OPTIMIZAR E INDEXAR SISTEMAS", 
            command=self.lanzar_backend_hilo, bg="#2ecc71", fg="white", 
            font=("Arial", 11, "bold"), activebackground="#27ae60", height=2
        )
        self.btn_ejecutar.pack(pady=10)

    def ag(self, mensaje_crudo):
        """[AGENTE DE LOGS ANTI-COPYRIGHT]"""
        # Filtro estricto de strings comerciales por si vienen en el nombre del archivo
        mensaje_limpio = mensaje_crudo.replace("playstation", "PSX").replace("sony", "SYS").replace("PlayStation", "PSX")
        
        if "Inyectando:" in mensaje_limpio:
            archivo = mensaje_limpio.split(":")[-1].strip()
            mensaje_salida = f"✨ Optimizando e Inyectando juego: {archivo}"
        elif "Límite" in mensaje_limpio or "Demo" in mensaje_limpio:
            mensaje_salida = "❌ [LOCK] Cantidad maxima de evaluacion superada."
        else:
            mensaje_salida = mensaje_limpio
            
        self.txt_consola.config(state="normal")
        self.txt_consola.insert(tk.END, f"> {mensaje_salida}\n")
        self.txt_consola.see(tk.END)
        self.txt_consola.config(state="disabled")

    def _buscar_origen(self):
        if self.procesando: return
        ruta = filedialog.askdirectory(title="Selecciona la carpeta origen con tus ROMs")
        if ruta: self.ruta_origen.set(ruta)

    def _buscar_destino(self):
        if self.procesando: return
        ruta = filedialog.askdirectory(title="Selecciona la unidad destino (SD/USB)")
        if ruta: self.ruta_destino.set(ruta)

    def lanzar_backend_hilo(self):
        orig = self.ruta_origen.get()
        dest = self.ruta_destino.get()
        
        if not orig or not dest:
            messagebox.showwarning("Datos Incompletos", "Por favor, configure las rutas de Origen y Destino primero.")
            return

        self.procesando = True
        self.btn_ejecutar.config(state="disabled", bg="#7f8c8d")
        self.progreso.start(10)
        self.estado_texto.set("Estado: Generando estructuras de evaluacion...")
        
        self.txt_consola.config(state="normal")
        self.txt_consola.delete("1.0", tk.END)
        self.txt_consola.config(state="disabled")

        hilo = threading.Thread(target=self._proceso_fondo, args=(orig, dest), daemon=True)
        hilo.start()

    def _proceso_fondo(self, orig, dest):
        resultado = self.manager_backend.purgar_y_extraer_en_crudo(orig, dest)
        self.progreso.stop()
        
        if resultado == "limite_demo":
            self.estado_texto.set("⚠️ VERSION DEMO BLOQUEADA. Requiere activacion.")
            self.lbl_comprar.config(fg="#e74c3c")
            messagebox.showwarning(
                "Limite de Evaluacion", 
                "Se han procesado e indexado los primeros 25 juegos con exito.\n\n"
                "Para procesar el resto de tu catalogo sin restricciones, por favor adquiere la clave de activacion Pro o reinicia el software."
            )
            self.procesando = True 
            
        elif resultado == "exito":
            self.estado_texto.set("Estado: ¡Sistemas indexados correctamente!")
            messagebox.showinfo("Inyeccion Completa", "El lote reducido se completo con exito. Archivos TXT y XML listos.")
            self.procesando = False
            self.btn_ejecutar.config(state="normal", bg="#2ecc71")
        else:
            self.estado_texto.set("Estado: No se encontraron archivos nuevos.")
            self.procesando = False
            self.btn_ejecutar.config(state="normal", bg="#2ecc71")

    def iniciar_programa(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PandarcadeMainWindow()
    app.iniciar_programa()
