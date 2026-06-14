import os
import shutil
from DBManager import PandarcadeDatabase
from detector import SonyFormatDetector
from mcgames_builder import PandarcadeMcGamesBuilder  # Importamos tu nuevo constructor eMMC

class PandarcadeCore:
    def __init__(self, log_callback):
        self.log = log_callback
        self.DBManager = PandarcadeDatabase(log_callback)
        self.detector = SonyFormatDetector(log_callback)
        self.mcgames_builder = PandarcadeMcGamesBuilder(log_callback)  # Inicializamos el constructor
        
        # Diccionario maestro de fabricantes
        self.MAPA_EMULADORES = {
            'neo-geo': 'fba', 'snk': 'fba', 'igs': 'fba', 
            'capcom play system 1': 'fba', 'capcom play system 2': 'fba', 'capcom': 'fba', 
            'capcom play system 3': 'mame199', 'irem classics': 'mame139', 
            'nichibutsu': 'mame139', 'michibutsu': 'mame139',
            'sega classics': 'mame139', 'taito classics': 'mame139', 'konami classics': 'mame139',
            'midway classics': 'mame139', 'namco classics': 'mame139', 
            'nintendo classics': 'mame78', 'atari classics': 'mame78'
        }

        # Regla de extensiones nativas por consola actualizada
        self.FORMATOS_POR_CONSOLA = {
            'fba42': {'.zip'}, 'fba': {'.zip'},
            'mame139': {'.zip'}, 'mame79': {'.zip'}, 'mame119': {'.zip'}, 'mame19': {'.zip'}, 'mame37': {'.zip'}, 'mame78': {'.zip'}, 'mame199': {'.zip'}, 'mame': {'.zip'},
            'fc': {'.nes'}, 'family': {'.nes'}, 'nes': {'.nes'},
            'sfc': {'.sfc', '.smc'}, 'snes': {'.sfc', '.smc'},
            'md': {'.md', '.bin'}, 'megadrive': {'.md', '.bin'}, 'genesis': {'.md', '.bin'},
            'mastersystem': {'.sms'}, 'sms': {'.sms'},
            'gba': {'.gba'}, 'gbc': {'.gbc'}, 'gb': {'.gb'},
            'n64': {'.n64', '.z64', '.v64', '.zip'},
            'dc': {'.cdi', '.gdi', '.chd'}, 'dreamcast': {'.cdi', '.gdi', '.chd'},
            'playstation': {'.iso', '.bin', '.cue', '.chd', '.img', '.pbp', '.ccd'}, 
            'psx': {'.iso', '.bin', '.cue', '.chd', '.img', '.pbp', '.ccd'},
            'psp': {'.iso', '.chd', '.cso'}, 
            'wswan': {'.wsc', '.ws'}
        }

    def purgar_y_extraer_en_crudo(self, ruta_data):
        """Destruye duplicados y extrae las ROMs según su formato nativo eliminando basura"""
        if not os.path.exists(ruta_data):
            self.log(f"❌ Error: La ruta {ruta_data} no existe.")
            return False

        self.log("🧹 Iniciando Purga Quirúrgica avanzada (Soporte Inteligente Sony)...")
        purgados = 0
        rescatados = 0

        zips_sueltos = [z for z in os.listdir(ruta_data) if z.lower().endswith(('.zip', '.chd', '.iso', '.pbp', '.cso'))]
        if zips_sueltos:
            self.log(f"ℹ️ Detectados {len(zips_sueltos)} juegos en la raíz. Pasando directo a indexación.")
            return True

        for sistema in os.listdir(ruta_data):
            ruta_sistema = os.path.join(ruta_data, sistema)
            nombre_sistema_lower = sistema.lower()
            
            if os.path.isdir(ruta_sistema):
                ext_validas = self.FORMATOS_POR_CONSOLA.get(nombre_sistema_lower, {'.zip', '.bin', '.cue', '.iso', '.md', '.nes', '.sfc', '.chd', '.cso', '.pbp'})
                
                for subcarpeta in os.listdir(ruta_sistema):
                    ruta_subcarpeta = os.path.join(ruta_sistema, subcarpeta)
                    
                    if os.path.isdir(ruta_subcarpeta):
                        if subcarpeta.startswith('.') or subcarpeta.startswith('_'): 
                            continue
                        
                        archivos_internos = os.listdir(ruta_subcarpeta)
                        juegos_validos_encontrados = []
                        
                        for f_interno in archivos_internos:
                            _, ext = os.path.splitext(f_interno.lower())
                            if ext in ext_validas:
                                ruta_f_completa = os.path.join(ruta_subcarpeta, f_interno)
                                if os.path.getsize(ruta_f_completa) > 0:
                                    juegos_validos_encontrados.append(f_interno)
                        
                        if juegos_validos_encontrados:
                            archivo_a_rescatar = juegos_validos_encontrados
                            
                            if len(juegos_validos_encontrados) > 1:
                                for j_valido in juegos_validos_encontrados:
                                    nombre_juego_sin_ext = os.path.splitext(j_valido).lower()
                                    if nombre_juego_sin_ext == subcarpeta.lower():
                                        archivo_a_rescatar = j_valido
                                        break
                            
                            ruta_origen_file = os.path.join(ruta_subcarpeta, archivo_a_rescatar)
                            
                            _, ext_actual = os.path.splitext(archivo_a_rescatar.lower())
                            ruta_destino_final = os.path.join(ruta_sistema, archivo_a_rescatar)
                            
                            if ext_actual in {'.iso', '.pbp', '.chd'}:
                                consola_detectada = self.sony_detector.analizar_cabecera_sony(ruta_origen_file)
                                if consola_detectada != "indeterminado":
                                    ruta_raiz_games = os.path.dirname(ruta_sistema)
                                    folder_real = "playstation" if consola_detectada == "playstation" else "psp"
                                    ruta_destino_final = os.path.join(ruta_raiz_games, folder_real, archivo_a_rescatar)
                                    
                                    os.makedirs(os.path.dirname(ruta_destino_final), exist_ok=True)
                                    self.log(f"🧠 [FIRMWARE DETECTED] '{archivo_a_rescatar}' identificado como {consola_detectada.upper()}. Redirigiendo.")

                            if not os.path.exists(ruta_destino_final):
                                try:
                                    shutil.move(ruta_origen_file, ruta_destino_final)
                                    rescatados += 1
                                except Exception as e:
                                    self.log(f"⚠️ No se pudo mover {archivo_a_rescatar}: {e}")
                                    continue
                            
                            try:
                                shutil.rmtree(ruta_subcarpeta)
                                purgados += 1
                            except PermissionError:
                                continue
                            except Exception:
                                continue
        
        self.log(f"✅ ¡Purga con escáner Sony completada! {rescatados} juegos en crudo organizados.")
        return True

    def clasificar_e_inyectar_db(self, ruta_txt, ruta_origen_zips, raiz_destino_usb):
        """Clasifica las ROMs, genera la base de datos SQL externa Y compila la estructura mcgames eMMC"""
        if not os.path.exists(ruta_txt) or not os.path.exists(ruta_origen_zips):
            self.log("❌ Error: Estructura de archivos de texto o ruta de origen incompleta.")
            return False

        ruta_games_destino = os.path.join(raiz_destino_usb, "games")
        if not os.path.exists(ruta_games_destino):
            os.makedirs(ruta_games_destino)

        self.log(f"📦 Clasificando juegos e inyectando Base de Datos interna...")
        
        diccionario_para_db = {}
        organizados = 0

        with open(ruta_txt, 'r', encoding='utf-8', errors='ignore') as f:
            for linea in f:
                if ".zip" in linea.lower() and "identified as" in linea.lower():
                    try:
                        partes = linea.split(" - ")
                        nombre_zip = partes.strip()
                        detalles = partes.lower() if len(partes) > 1 else linea_lower
                        
                        ruta_archivo_origen = os.path.join(ruta_origen_zips, nombre_zip)
                        
                        if os.path.exists(ruta_archivo_origen):
                            emulador_destino = 'mame139' 
                            titulo_bonito = nombre_zip
                            
                            if "identified as" in detalles:
                                sub_partes = detalles.split("identified as")
                                if len(sub_partes) > 1:
                                    titulo_bonito = sub_partes.split(" - ").replace("classics", "").strip().title()

                            for fabricante, carpeta in self.MAPA_EMULADORES.items():
                                if fabricante in detalles:
                                    emulador_destino = carpeta
                                    break
                            
                            carpeta_final = os.path.join(raiz_destino_usb, "games", "data", emulador_destino)
                            if not os.path.exists(carpeta_final):
                                os.makedirs(carpeta_final)
                            
                            ruta_archivo_destino = os.path.join(carpeta_final, nombre_zip)
                            if not os.path.exists(ruta_archivo_destino):
                                shutil.move(ruta_archivo_origen, ruta_archivo_destino)
                            
                            diccionario_para_db[nombre_zip] = (titulo_bonito, emulador_destino)
                            organizados += 1
                    except Exception:
                        continue

        # --- INYECCIÓN EN PARALELO (MÉTODO USB EXTERNO Y MÉTODO EMMC INTERNO) ---
        if diccionario_para_db:
            # 1. Creamos la base de datos externa .db nativa
            self.db_manager.registrar_juegos_en_db(ruta_games_destino, diccionario_para_db)
            # 2. Compilamos de forma automatizada el script instalador para la memoria interna soldada
            self.mcgames_builder.construir_estructura_mcgames(raiz_destino_usb, diccionario_para_db)
            self.log(f"✅ ¡Clasificación masiva y Base de Datos completada! {organizados} juegos listos.")
            return True
