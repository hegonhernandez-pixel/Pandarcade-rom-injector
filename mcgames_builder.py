import os

class PandarcadeMcGamesBuilder:
    def __init__(self, log_callback=None):
        self.log = log_callback if log_callback else print

    def construir_estructura_mcgames(self, raiz_destino_usb, diccionario_juegos):
        """
        Genera la carpeta mcgames, el archivo install.txt y las subcarpetas con sus .xml
        basándose en los juegos en crudo procesados con éxito.
        """
        ruta_mcgames = os.path.join(raiz_destino_usb, "mcgames")
        
        # Crear la carpeta maestra mcgames si no existe
        if not os.path.exists(ruta_mcgames):
            os.makedirs(ruta_mcgames)
            self.log("📁 [EMMC INJECTION] Creando directorio maestro 'mcgames' en la USB.")

        ruta_install_txt = os.path.join(ruta_mcgames, "install.txt")
        self.log("📝 Generando archivo de autoejecución 'install.txt'...")

        # Mapeo de IDs de emuladores nativos para el script interno de la consola (Core Android)
        mapa_id_emuladores = {'fba': 3, 'mame139': 5, 'mame78': 1, 'mame199': 5, 'megadrive': 2, 'nes': 4}
        juegos_empaquetados = 0

        try:
            # 1. Escribir el listado en install.txt con codificación UTF-8 limpia
            with open(ruta_install_txt, 'w', encoding='utf-8') as f_install:
                for nombre_zip, (titulo_bonito, emulador_slug) in diccionario_juegos.items():
                    # Escribimos el nombre elegante que leerá la interfaz en la línea del instalador
                    f_install.write(f"{titulo_bonito}\n")
                    
                    # 2. Crear la subcarpeta individual del juego (ej: mcgames/Metal Slug 5/)
                    carpeta_juego_individual = os.path.join(ruta_mcgames, titulo_bonito)
                    os.makedirs(carpeta_juego_individual, exist_ok=True)
                    
                    # 3. Generar el archivo de metadatos .xml para engañar al firmware 40S
                    nombre_juego_sin_ext, _ = os.path.splitext(nombre_zip)
                    ruta_xml = os.path.join(carpeta_juego_individual, f"{titulo_bonito}.xml")
                    
                    id_emulador_consola = mapa_id_emuladores.get(emulador_slug, 5)
                    
                    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<game name="{nombre_juego_sin_ext}" emulator="{id_emulador_consola}">
  <information>
    <description>{titulo_bonito}</description>
    <cloneof>null</cloneof>
  </information>
</game>
"""
                    # Guardamos el archivo .xml dentro de su respectiva subcarpeta
                    with open(ruta_xml, 'w', encoding='utf-8') as f_xml:
                        f_xml.write(xml_content)
                    
                    juegos_empaquetados += 1

            self.log(f"⚡ ¡Inyector eMMC Listo! Creadas {juegos_empaquetados} estructuras xml dentro de 'mcgames/'.")
            self.log("💡 Instrucciones: Copia manualmente tus archivos .zip dentro de sus carpetas en 'mcgames' antes de conectar al tablero.")
            return True

        except Exception as e:
            self.log(f"❌ Error crítico al compilar instalador mcgames: {e}")
            return False
