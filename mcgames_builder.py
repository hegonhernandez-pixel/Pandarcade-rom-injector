# mcgames_builder.py
import os
import shutil
import xml.etree.ElementTree as ET
from xml.dom import minidom

class PandoraUniversalManager:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        
        # 🔒 CONFIGURACIÓN COMERCIAL: Límite de la versión de evaluación
        self.LIMITE_VERSION_FREE = 25 

        self.FORMATOS_POR_CONSOLA = {
            'fba42': {'.zip'}, 'fba': {'.zip'}, 'mame139': {'.zip'}, 'mame19': {'.zip'},
            'fc': {'.nes'}, 'nes': {'.nes'}, 'sfc': {'.sfc', '.smc'}, 'snes': {'.sfc', '.smc'},
            'md': {'.md', '.bin'}, 'megadrive': {'.md', '.bin'}, 'gba': {'.gba'},
            'n64': {'.n64', '.z64'}, 
            'psx': {'.iso', '.bin', '.cue', '.chd', '.pbp', '.img'}, 
            'psp': {'.iso', '.chd', '.cso', '.pbp'}
        }

        # Cambiamos nombres comerciales por acrónimos técnicos universales
        self.NORMALIZAR_CARPETA_PANDORA = {
            'psx': 'PSX', 
            'psp': 'PSP',
            'fc': 'nes', 'snes': 'sfc', 'megadrive': 'mega', 'md': 'mega'
        }

    def log(self, mensaje):
        if self.log_callback: self.log_callback(mensaje)
        else: print(mensaje)

    def _analizar_cabecera_binaria_segura(self, ruta_archivo):
        """
        Analiza las firmas en bruto por hexadecimal.
        Oculta cualquier string comercial directo en el ejecutable final.
        """
        ext = os.path.splitext(ruta_archivo).lower()
        try:
            if ext in ['.iso', '.bin']:
                with open(ruta_archivo, 'rb') as f:
                    # Leemos los primeros sectores de datos físicos en crudo
                    bloque = f.read(32768)
                    
                    # Identificación por identificador de región de código ejecutable estándar
                    # Buscamos patrones de ejecutables de consolas sin escribir el nombre comercial
                    if b"PSP GAME" in bloque:
                        return "psp"
                    elif b"PLAY" in bloque and b"STATION" in bloque:
                        return "psx"
                    elif b"SLUS_" in bloque or b"SLES_" in bloque or b"SCUS_" in bloque or b"SCES_" in bloque:
                        return "psx"
                        
            elif ext == '.chd':
                with open(ruta_archivo, 'rb') as f:
                    # Firma hexadecimal nativa MComprHD
                    if f.read(8).startswith(b"\x4d\x43\x6f\x6d\x70\x72\x48\x44"):
                        return "psx"
                        
            elif ext == '.pbp':
                with open(ruta_archivo, 'rb') as f:
                    # Firma ejecutable portátil \x00PBP
                    if f.read(4) == b"\x00\x50\x42\x50":
                        return "psp"
        except:
            pass
        return "indeterminado"

def purgar_y_extraer_en_crudo(self, ruta_origen, ruta_destino):
        if not os.path.exists(ruta_origen) or not os.path.exists(ruta_destino):
            self.log("❌ Error: Rutas inválidas.")
            return "error"

        self.log("🧹 Iniciando optimización de sistema y análisis de metadatos...")
        rescatados = 0
        juegos_indexados = []
        limite_alcanzado = False

        # Recorrer las carpetas de sistemas principales (Ej: fc, sfc, n64, psx)
        for sistema in os.listdir(ruta_origen):
            if limite_alcanzado: break
            ruta_sistema = os.path.join(ruta_origen, sistema)
            nombre_sistema_lower = sistema.lower()
            
            if os.path.isdir(ruta_sistema):
                # Obtener extensiones válidas configuradas para esta consola específica
                ext_validas = self.FORMATOS_POR_CONSOLA.get(
                    nombre_sistema_lower, 
                    {'.zip', '.bin', '.cue', '.iso', '.md', '.nes', '.sfc', '.chd', '.cso', '.pbp'}
                )
                
                # Normalizar el nombre de carpeta que espera la Pandora Box
                emu_pandora = self.NORMALIZAR_CARPETA_PANDORA.get(nombre_sistema_lower, nombre_sistema_lower)
                ruta_destino_consola = os.path.join(ruta_destino, emu_pandora)

                # ====================================================================
                # NUEVA MEJORA: PROCESAR ROMS SUELTAS DIRECTAMENTE EN LA CARPETA DEL SISTEMA
                # ====================================================================
                for elemento_raiz in os.listdir(ruta_sistema):
                    if len(juegos_indexados) >= self.LIMITE_VERSION_FREE:
                        self.log(f"⚠️ Límite de versión Demo alcanzado ({self.LIMITE_VERSION_FREE} juegos).")
                        limite_alcanzado = True
                        break
                        
                    ruta_elemento_raiz = os.path.join(ruta_sistema, elemento_raiz)
                    if os.path.isfile(ruta_elemento_raiz):
                        _, ext_archivo = os.path.splitext(elemento_raiz.lower())
                        
                        # Si el archivo suelto coincide con las extensiones válidas de la consola
                        if ext_archivo in ext_validas and os.path.getsize(ruta_elemento_raiz) > 0:
                            os.makedirs(ruta_destino_consola, exist_ok=True)
                            ruta_final_archivo = os.path.join(ruta_destino_consola, elemento_raiz)
                            
                            if not os.path.exists(ruta_final_archivo):
                                try:
                                    shutil.copy2(ruta_elemento_raiz, ruta_final_archivo)
                                    rescatados += 1
                                    self.log(f"Inyectando: {elemento_raiz}")
                                    juegos_indexados.append((emu_pandora, elemento_raiz))
                                except Exception as e:
                                    self.log(f"⚠️ Error en transferencia: {e}")
                            else:
                                juegos_indexados.append((emu_pandora, elemento_raiz))

                if limite_alcanzado: break

                # ====================================================================
                # LOGICA DE PURGA ORIGINAL: ENTRAR A BUSCAR DENTRO DE SUB-CARPETAS BASURA
                # ====================================================================
                for subcarpeta in os.listdir(ruta_sistema):
                    if limite_alcanzado: break
                    ruta_subcarpeta = os.path.join(ruta_sistema, subcarpeta)
                    
                    if os.path.isdir(ruta_subcarpeta):
                        if subcarpeta.startswith('.') or subcarpeta.startswith('_'): continue
                        # Ignorar carpetas multimedia que traen algunos packs comerciales de ROMs
                        if subcarpeta.lower() in ['images', 'videos', 'media', 'download']: continue
                        
                        archivos_internos = os.listdir(ruta_subcarpeta)
                        juegos_validos_encontrados = []
                        
                        for f_interno in archivos_internos:
                            _, ext = os.path.splitext(f_interno.lower())
                            if ext in ext_validas and os.path.getsize(os.path.join(ruta_subcarpeta, f_interno)) > 0:
                                juegos_validos_encontrados.append(f_interno)
                        
                        if juegos_validos_encontrados:
                            if len(juegos_indexados) >= self.LIMITE_VERSION_FREE:
                                self.log(f"⚠️ Límite de versión Demo alcanzado ({self.LIMITE_VERSION_FREE} juegos).")
                                limite_alcanzado = True
                                break

                            archivo_a_rescatar = juegos_validos_encontrados[0]
                            if len(juegos_validos_encontrados) > 1:
                                for j_valido in juegos_validos_encontrados:
                                    nombre_juego_sin_ext, _ = os.path.splitext(j_valido)
                                    if nombre_juego_sin_ext.lower() == subcarpeta.lower():
                                        archivo_a_rescatar = j_valido
                                        break
                            
                            ruta_orig_file = os.path.join(ruta_subcarpeta, archivo_a_rescatar)
                            _, ext_actual = os.path.splitext(archivo_a_rescatar.lower())
                            
                            folder_final_nombre = nombre_sistema_lower
                            if ext_actual in {'.iso', '.pbp', '.chd'}:
                                deteccion = self._analizar_cabecera_binaria_segura(ruta_orig_file)
                                if deteccion != "indeterminado":
                                    folder_final_nombre = deteccion

                            emu_pandora_sub = self.NORMALIZAR_CARPETA_PANDORA.get(folder_final_nombre, folder_final_nombre)
                            ruta_destino_consola_sub = os.path.join(ruta_destino, emu_pandora_sub)
                            os.makedirs(ruta_destino_consola_sub, exist_ok=True)
                            
                            ruta_final_archivo_sub = os.path.join(ruta_destino_consola_sub, archivo_a_rescatar)

                            if not os.path.exists(ruta_final_archivo_sub):
                                try:
                                    shutil.copy2(ruta_orig_file, ruta_final_archivo_sub)
                                    rescatados += 1
                                    if ext_actual == '.bin' and os.path.exists(ruta_orig_file.replace('.bin', '.cue').replace('.BIN', '.CUE')):
                                        continue
                                    self.log(f"Inyectando: {archivo_a_rescatar}")
                                    juegos_indexados.append((emu_pandora_sub, archivo_a_rescatar))
                                except Exception as e:
                                    self.log(f"⚠️ Error en transferencia: {e}")
                            else:
                                if not (ext_actual == '.bin' and os.path.exists(ruta_orig_file.replace('.bin', '.cue').replace('.BIN', '.CUE'))):
                                    juegos_indexados.append((emu_pandora_sub, archivo_a_rescatar))

                        # Borrado seguro de subcarpetas vacías
                        try:
                            if os.path.exists(ruta_subcarpeta) and not os.listdir(ruta_subcarpeta):
                                os.rmdir(ruta_subcarpeta)
                        except: pass

        if juegos_indexados:
            self._guardar_txt_pandora(ruta_destino, juegos_indexados)
            self._guardar_xml_universal(ruta_destino, juegos_indexados)
            return "limite_demo" if limite_alcanzado else "exito"
        return "vacio"

    def _guardar_txt_pandora(self, ruta, datos):
        lineas = []
        for emu, archivo in datos:
            nombre, _ = os.path.splitext(archivo)
            nombre_limpio = nombre.replace("|", "-").strip()
            lineas.append(f"{emu}_{nombre_limpio}|{emu}|{nombre_limpio}|{emu}/{archivo}\n")
        with open(os.path.join(ruta, "mcgames.txt"), "w", encoding="utf-8") as f:
            f.writelines(lineas)

    def _guardar_xml_universal(self, ruta, datos):
        root = ET.Element("gameList")
        for emu, archivo in datos:
            game_node = ET.SubElement(root, "game")
            path_node = ET.SubElement(game_node, "path")
            path_node.text = f"./{emu}/{archivo}"
            nombre, _ = os.path.splitext(archivo)
            name_node = ET.SubElement(game_node, "name")
            name_node.text = nombre.replace("_", " ").strip()
            desc_node = ET.SubElement(game_node, "desc")
            desc_node.text = "Optimizado por motor de inyeccion automatica universal."
        xml_str = minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent="  ")
        with open(os.path.join(ruta, "gamelist.xml"), "w", encoding="utf-8") as f:
            f.write(xml_str)
