import os
import shutil
import xml.etree.ElementTree as ET
from xml.dom import minidom

class PandoraUniversalManager:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.LIMITE_VERSION_FREE = 100 
        self.FORMATOS_POR_CONSOLA = {
            'fba42': {'.zip'}, 'fba': {'.zip'}, 'mame139': {'.zip'}, 'mame19': {'.zip'},
            'fc': {'.nes'}, 'nes': {'.nes'}, 'sfc': {'.sfc', '.smc'}, 'snes': {'.sfc', '.smc'},
            'md': {'.md', '.bin'}, 'megadrive': {'.md', '.bin'}, 'gba': {'.gba'},
            'n64': {'.n64', '.z64'}, 'psx': {'.iso', '.bin', '.cue', '.chd', '.pbp', '.img'}, 
            'psp': {'.iso', '.chd', '.cso', '.pbp'}
        }
        self.NORMALIZAR_CARPETA_PANDORA = {
            'psx': 'PSX', 'psp': 'PSP', 'fc': 'nes', 'snes': 'sfc', 'megadrive': 'mega', 'md': 'mega'
        }

    def log(self, mensaje):
        if self.log_callback: self.log_callback(mensaje)
        else: print(mensaje)

    def _analizar_cabecera_binaria_segura(self, ruta_archivo):
        _, ext = os.path.splitext(ruta_archivo)
        ext = ext.lower()
        try:
            if ext in ['.iso', '.bin']:
                with open(ruta_archivo, 'rb') as f:
                    bloque = f.read(32768)
                    if b"PSP GAME" in bloque: return "psp"
                    if b"PLAY" in bloque and b"STATION" in bloque: return "psx"
                    if any(x in bloque for x in [b"SLUS_", b"SLES_", b"SCUS_", b"SCES_"]): return "psx"
            elif ext == '.chd':
                with open(ruta_archivo, 'rb') as f:
                    if f.read(8).startswith(b"\x4d\x43\x6f\x6d\x70\x72\x48\x44"): return "psx"
            elif ext == '.pbp':
                with open(ruta_archivo, 'rb') as f:
                    if f.read(4) == b"\x00\x50\x42\x50": return "psp"
        except: pass
        return "indeterminado"

    def _guardar_txt_pandora(self, ruta_destino, juegos_indexados):
        archivo_txt = os.path.join(ruta_destino, "juegos_instalados.txt")
        with open(archivo_txt, "w", encoding="utf-8") as f:
            for sistema, nombre in juegos_indexados:
                f.write(f"[{sistema}] {nombre}\n")

    def _guardar_xml_universal(self, ruta_destino, juegos_indexados):
        root = ET.Element("gameList")
        for sistema, nombre in juegos_indexados:
            game = ET.SubElement(root, "game")
            path = ET.SubElement(game, "path")
            path.text = f"./{sistema}/{nombre}"
            name = ET.SubElement(game, "name")
            name.text = os.path.splitext(nombre)[0]
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(os.path.join(ruta_destino, "gamelist.xml"), "w", encoding="utf-8") as f:
            f.write(xml_str)

    def purgar_y_extraer_en_crudo(self, ruta_origen, ruta_destino):
        if not os.path.exists(ruta_origen) or not os.path.exists(ruta_destino): return "error"
        
        juegos_indexados = []
        for sistema in os.listdir(ruta_origen):
            ruta_sistema = os.path.join(ruta_origen, sistema)
            if not os.path.isdir(ruta_sistema): continue
            
            ext_validas = self.FORMATOS_POR_CONSOLA.get(sistema.lower(), {'.zip', '.bin', '.cue', '.iso'})
            emu_pandora = self.NORMALIZAR_CARPETA_PANDORA.get(sistema.lower(), sistema.lower())
            ruta_destino_consola = os.path.join(ruta_destino, emu_pandora)

            for nombre_archivo in os.listdir(ruta_sistema):
                if len(juegos_indexados) >= self.LIMITE_VERSION_FREE: break
                
                ruta_orig_file = os.path.join(ruta_sistema, nombre_archivo)
                if not os.path.isfile(ruta_orig_file): continue
                
                _, ext = os.path.splitext(nombre_archivo.lower())
                if ext in ext_validas:
                    os.makedirs(ruta_destino_consola, exist_ok=True)
                    ruta_final = os.path.join(ruta_destino_consola, nombre_archivo)
                    
                    if not os.path.exists(ruta_final):
                        shutil.copy2(ruta_orig_file, ruta_final)
                        juegos_indexados.append((emu_pandora, nombre_archivo))
                        self.log(f"Inyectado: {nombre_archivo}")
                        
                        # Copia automática de .cue si existe
                        if ext == '.bin':
                            archivo_cue = nombre_archivo.replace('.bin', '.cue').replace('.BIN', '.CUE')
                            ruta_cue_orig = os.path.join(ruta_sistema, archivo_cue)
                            if os.path.exists(ruta_cue_orig):
                                shutil.copy2(ruta_cue_orig, os.path.join(ruta_destino_consola, archivo_cue))
                                juegos_indexados.append((emu_pandora, archivo_cue))
                                self.log(f" + Par .cue detectado e inyectado")
        
        if juegos_indexados:
            self._guardar_txt_pandora(ruta_destino, juegos_indexados)
            self._guardar_xml_universal(ruta_destino, juegos_indexados)
        return "exito"
