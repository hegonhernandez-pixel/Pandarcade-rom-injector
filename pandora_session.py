import os
import shutil
import time
import webbrowser # Para abrir el enlace de PayPal en el navegador
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- BACKEND MODIFICADO CON LÍMITE DE TIEMPO (24 HORAS) ---
class PandoraUniversalManager:
    def __init__(self, log_callback=root):
        self.log_callback = log_callback
        self.LIMITE_VERSION_FREE = 25
        self.ARCHIVO_SESION = ".pandora_session"

    def verificar_limite_tiempo(self):
        """
        Revisa si el usuario ya gastó sus 25 juegos diarios.
        Devuelve (True, "Mensaje") si puede continuar, o (False, "Mensaje") si debe esperar.
        """
        ahora = time.time()
        segundos_en_24h = 24 * 60 * 60 # 86,400 segundos

        if not os.path.exists(self.ARCHIVO_SESION):
            # Primera vez que usa el programa o sesión limpia
            return True, 0

        try:
            with open(self.ARCHIVO_SESION, "r") as f:
                datos = f.read().split(",")
                ultimo_acceso = float(datos[0])
                juegos_procesados = int(datos[1])

            # Si ya pasaron las 24 horas, se reinicia el contador automáticamente
            if ahora - ultimo_acceso > segundos_en_24h:
                return True, 0

            # Si está dentro de las 24 horas y ya superó los 25 juegos, se bloquea
            if juegos_procesados >= self.LIMITE_VERSION_FREE:
                tiempo_restante = segundos_en_24h - (ahora - ultimo_acceso)
                horas_restantes = int(tiempo_restante // 3600)
                minutos_restantes = int((tiempo_restante % 3600) // 60)
                return False, f"🛑 Has alcanzado el límite gratuito de {self.LIMITE_VERSION_FREE} juegos diarios.\nEspera {horas_restantes}h y {minutos_restantes}m o apoya el proyecto con una donación."

            return True, juegos_procesados
        except:
            # Si el archivo se corrompe, permitimos el paso por seguridad
            return True, 0

    def registrar_inyeccion(self, cantidad_inyectada):
        """ Guarda el progreso del usuario de forma local """
        ahora = time.time()
        _, juegos_actuales = self.verificar_limite_tiempo()
        nuevo_total = juegos_actuales + cantidad_inyectada
        
        with open(self.ARCHIVO_SESION, "w") as f:
            f.write(f"{ahora},{nuevo_total}")
