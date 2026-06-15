import tkinter as tk
from tkinter import ttk

def aplicar_estilo_arcade(root):
    # Configurar fuentes retro/pixeladas instaladas o del sistema
    # 'Courier New' o 'Consolas' dan un look de terminal arcade muy limpio
    FUERTE_TITULO = ("Consolas", 14, "bold")
    FUENTE_TEXTO = ("Consolas", 10)
    
    # Paleta de colores Arcade Neón
    COLOR_FONDO = "#1e1e24"      # Gris oscuro/Casi negro
    COLOR_TEXTO = "#ffffff"      # Blanco
    COLOR_VERDE_NEON = "#39ff14" # Verde Neón (Para botones de éxito/inyección)
    COLOR_CYAN = "#00f0ff"       # Cyan Cyberpunk (Para pestañas y bordes)
    COLOR_BOTON_BG = "#2a2a35"   # Fondo de botones por defecto
    
    # Cambiar el fondo de la ventana principal
    root.configure(bg=COLOR_FONDO)
    
    # Crear el objeto de estilos de TTK
    style = ttk.Style()
    style.theme_use('default') # Usamos el tema base para poder modificar todo
    
    # 🏢 ESTILO DEL CONTENEDOR (Notebook / Pestañas)
    style.configure("TNotebook", background=COLOR_FONDO, borderwidth=0)
    style.configure("TNotebook.Tab", 
                    background=COLOR_BOTON_BG, 
                    foreground=COLOR_TEXTO, 
                    font=FUENTE_TEXTO, 
                    padding=[15, 5])
    
    # Cambiar color de la pestaña cuando está activa
    style.map("TNotebook.Tab", 
              background=[("selected", COLOR_CYAN)], 
              foreground=[("selected", "#000000")]) # Texto negro en pestaña activa

    # 🖼️ ESTILO DE LOS MARCOS (Frames y LabelFrames)
    style.configure("TFrame", background=COLOR_FONDO)
    style.configure("TLabelframe", background=COLOR_FONDO, foreground=COLOR_CYAN, font=FUERTE_TITULO)
    style.configure("TLabelframe.Label", background=COLOR_FONDO, foreground=COLOR_CYAN, font=FUENTE_TEXTO)

    # 🕹️ ESTILO DE LOS BOTONES PREMIUM RETRO
    # Un truco genial en Tkinter para hacer botones hermosos es usar tk.Button nativo con relieves planos
    return {
        "bg_principal": COLOR_FONDO,
        "fg_texto": COLOR_TEXTO,
        "fuente_retro": FUENTE_TEXTO,
        "fuente_titulo": FUERTE_TITULO,
        "verde_neon": COLOR_VERDE_NEON,
        "cyan": COLOR_CYAN,
        "boton_bg": COLOR_BOTON_BG
    }
