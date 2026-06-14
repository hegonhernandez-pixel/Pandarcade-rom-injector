import os
import shutil

class PandarcadeCore:
    def __init__(self, log_callback):
        # Usamos un callback para mandar los mensajes directo a la consola visual de la pantalla
        self.log = log_callback
        
        # Diccionario maestro de fabricantes probado en tus consolas
        self.MAPA_EMULADORES = {
            'neo-geo': 'fba', 'snk': 'fba', 'igs': 'fba', 
            'capcom play system 1': 'fba', 'capcom play system 2': 'fba', 'capcom': 'fba', 
            'capcom play system 3': 'mame199', 'irem classics': 'mame139', 
            'nichibutsu': 'mame139', 'michibutsu': 'mame139',
            'sega classics': 'mame139', 'taito classics': 'mame139', 'konami classics': 'mame139',
            'midway classics': 'mame139', 'namco classics': 'mame139', 
            'nintendo classics': 'mame78', 'atari classics': 'mame78'
        }

    def purgar_y_extraer_en_crudo(self, ruta_data):
        """Paso 1: Destruye duplicados y extrae las ROMs eliminando basura (.mp4, .txt, .xml)"""
        if not os.path.exists(ruta_data):
            self.log(f"❌ Error: La ruta {ruta_data} no existe.")
            return False

        self.log("🧹 Buscando duplicados y limpiando residuos multimedia...")
        purgados = 0
        rescatados = 0

        for sistema in os.listdir(ruta_data):
            ruta_sistema = os.path.join(ruta_data, sistema)
            if os.path.isdir(ruta_sistema):
                for subcarpeta in os.listdir(ruta_sistema):
                    ruta_subcarpeta = os.path.join(ruta_sistema, subcarpeta)
                    if os.path.isdir(ruta_subcarpeta):
                        if subcarpeta.startswith('.') or subcarpeta.startswith('_'): 
                            continue
                        
                        lista_zips = [z for z in os.listdir(ruta_subcarpeta) if z.lower().endswith('.zip')]
                        if lista_zips:
                            zip_elegido = lista_zips[0]
                            # Si hay conflicto de doble ZIP, salvar el correcto
                            if len(lista_zips) > 1:
                                for z in lista_zips:
                                    if os.path.splitext(z)[0].lower() == subcarpeta.lower():
                                        zip_elegido = z
                                        break
                            
                            ruta_origen = os.path.join(ruta_subcarpeta, zip_elegido)
                            ruta_destino = os.path.join(ruta_sistema, zip_elegido)
                            
                            if not os.path.exists(ruta_destino):
                                shutil.move(ruta_origen, ruta_destino)
                                rescatados += 1
                            
                            try:
                                shutil.rmtree(ruta_subcarpeta)
                                purgados += 1
                            except PermissionError:
                                self.log(f"⚠️ Carpeta retenida por Windows, saltando: {subcarpeta}")
                                continue
        
        self.log(f"✅ Limpieza terminada: {rescatados} juegos extraídos y {purgados} carpetas de basura eliminadas.")
        return True

    def clasificar_por_historial(self, ruta_txt, ruta_origen_zips, raiz_destino_usb):
        """Paso 2: Lee el historial local e inyecta los .zip en crudo auto-creando carpetas"""
        if not os.path.exists(ruta_txt) or not os.path.exists(ruta_origen_zips):
            self.log("❌ Error: Verifica el archivo .txt de origen o la carpeta de juegos revueltos.")
            return False

        if not os.path.exists(raiz_destino_usb):
            os.makedirs(raiz_destino_usb)

        self.log(f"📦 Clasificando automáticamente desde: {ruta_txt}")
        organizados = 0

        with open(ruta_txt, 'r', encoding='utf-8', errors='ignore') as f:
            for linea in f:
                linea_lower = linea.lower()
                if ".zip" in linea_lower and "identified as" in linea_lower:
                    try:
                        partes = linea.split(" - ")
                        nombre_zip = partes[0].strip()
                        detalles = partes[1].lower() if len(partes) > 1 else linea_lower
                        
                        ruta_archivo_origen = os.path.join(ruta_origen_zips, nombre_zip)
                        
                        if os.path.exists(ruta_archivo_origen):
                            emulador_destino = 'mame139' # Default
                            for fabricante, carpeta in self.MAPA_EMULADORES.items():
                                if fabricante in detalles:
                                    emulador_destino = carpeta
                                    break
                            
                            carpeta_final = os.path.join(raiz_destino_usb, emulador_destino)
                            if not os.path.exists(carpeta_final):
                                os.makedirs(carpeta_final)
                                self.log(f"📁 [NUEVA CARPETA] Creada ruta para emulador: {emulador_destino}")
                            
                            shutil.move(ruta_archivo_origen, os.path.join(carpeta_final, nombre_zip))
                            organizados += 1
                    except Exception as e:
                        continue

        self.log(f"✅ ¡Clasificación masiva completada! {organizados} juegos acomodados en su emulador ideal.")
        return True
