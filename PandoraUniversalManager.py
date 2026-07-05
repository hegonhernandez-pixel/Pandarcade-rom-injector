import os
import shutil
import xml.etree.ElementTree as ET
from xml.dom import minidom

class PandoraUniversalManager:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.LIMITE_VERSION_FREE = 100
        # ... (aquí irían tus diccionarios y constantes)

    def log(self, mensaje):
        if self.log_callback:
            self.log_callback(mensaje)
        else:
            print(mensaje)

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
        except:
            pass
        return "indeterminado"
    self.NORMALIZAR_CARPETA_PANDORA = {
            'psx': 'PSX', 'psp': 'PSP', 'fc': 'nes', 'snes': 'sfc', 'megadrive': {'mega','md'},
            'fba42': {'.zip'}, 'fba': {'.zip'}, 'mame139': {'.zip'}, 'mame19': {'.zip'},
            'fc': {'.nes'}, 'nes': {'.nes'}, 'sfc': {'.sfc', '.smc'}, 'snes': {'.sfc', '.smc'},
            'md': {'.md', '.bin'}, 'megadrive': {'.md', '.bin'}, 'gba': {'.gba'},
            'n64': {'.n64', '.z64'}, 'psx': {'.iso', '.bin', '.cue', '.chd', '.pbp', '.img'}, 
            'psp': {'.iso', '.chd', '.cso', '.pbp'}
        }
 

    self.PANDORA_BIOS_MAP = {
    # --- PlayStation 1 ---
    "scph5501.bin": ["playstation", "BIOS PS1 Americana (Recomendada)"],
    "scph1001.bin": ["playstation", "BIOS PS1 Alternativa"],
    "scph7001.bin": ["playstation", "BIOS PS1 Slim"],
    "scph5501.bin": ["common", "Copia de PS1 en Carpeta Común"],

    # --- Dreamcast / Naomi / Atomiswave ---
    "dc_boot.bin": ["dreamcast", "Boot ROM de Dreamcast"],
    "dc_flash.bin": ["dreamcast", "Flash NVRAM de Dreamcast"],
    "awbios.zip": ["dreamcast", "BIOS obligatoria para Atomiswave"],
    "naomi.zip": ["dreamcast", "BIOS obligatoria para Naomi"],
    "awbios.zip": ["common", "Copia de Atomiswave en Carpeta Común"],

    # --- Sega CD / Mega CD ---
    "bios_CD_U.bin": ["common", "BIOS Sega CD - Región USA"],
    "bios_CD_E.bin": ["common", "BIOS Sega CD - Región Europa"],
    "bios_CD_J.bin": ["common", "BIOS Sega CD - Región Japón"],

    # --- Game Boy Advance ---
    "gba_bios.bin": ["gba", "BIOS obligatoria para Game Boy Advance"],

    # --- PC Engine ---
    "syscard3.pce": ["pcengine", "System Card 3.0 para TurboGrafx-16 CD"],

    # --- Arcades (Copias requeridas dentro de cada core activo) ---
    "neogeo.zip": ["mame19", "BIOS NeoGeo para MAME 19"],
    "neogeo.zip": ["mame37", "BIOS NeoGeo para MAME 37"],
    "neogeo.zip": ["mame78", "BIOS NeoGeo para MAME 78"],
    "neogeo.zip": ["mame139", "BIOS NeoGeo para MAME 139"],
    "neogeo.zip": ["fba42", "BIOS NeoGeo para FinalBurn Alpha"],
    "pgm.zip": ["mame78", "BIOS PolyGame Master"],
}

class BiosInjectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pandarcade - Inyector Inteligente de BIOS")
        self.root.geometry("650x450")
        self.root.resizable(False, False)

        self.origen_path = tk.StringVar()
        self.destino_path = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Título principal
        title_label = tk.Label(self.root, text="Inyector Automático de BIOS (Pandora 3D/3DS)", font=("Arial", 14, "bold"))
        title_label.pack(pady=15)

        # Marco de Selección de Origen (El Pack Revuelto)
        frame_origen = tk.LabelFrame(self.root, text=" 1. Carpeta de Origen (Donde está tu pack de BIOS revueltas) ", font=("Arial", 10, "bold"), padx=10, pady=10)
        frame_origen.pack(fill="x", padx=20, pady=10)

        tk.Entry(frame_origen, textvariable=self.origen_path, width=55, state="readonly").pack(side="left", padx=5)
        tk.Button(frame_origen, text="Buscar Pack...", command=self.seleccionar_origen, bg="#e1e1e1").pack(side="right", padx=5)

        # Marco de Selección de Destino (La carpeta 'data' de la captura)
        frame_destino = tk.LabelFrame(self.root, text=" 2. Carpeta de Destino (Debe ser la carpeta 'data' de tu Pandora) ", font=("Arial", 10, "bold"), padx=10, pady=10)
        frame_destino.pack(fill="x", padx=20, pady=10)

        tk.Entry(frame_destino, textvariable=self.destino_path, width=55, state="readonly").pack(side="left", padx=5)
        tk.Button(frame_destino, text="Buscar Destino...", command=self.seleccionar_destino, bg="#e1e1e1").pack(side="right", padx=5)

        # Consola / Cuadro de estado de copia
        self.txt_log = tk.Text(self.root, height=10, width=75, state="disabled", font=("Courier", 9))
        self.txt_log.pack(pady=15)

        # Botón de acción principal
        self.btn_procesar = tk.Button(self.root, text="PROCESAR E INYECTAR BIOS", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", command=self.procesar_bios, state="disabled")
        self.btn_procesar.pack(pady=5)

    def seleccionar_origen(self):
        path = filedialog.askdirectory(title="Selecciona la carpeta contenedora de tu Pack de BIOS")
        if path:
            self.origen_path.set(path)
            self.verificar_botones()

    def seleccionar_destino(self):
        path = filedialog.askdirectory(title="Selecciona la carpeta 'data' de tu Pandora")
        if path:
            # Validación rápida para asegurar que están en el directorio correcto de la captura
            if not os.path.basename(path) == "data" and not os.path.exists(os.path.join(path, "playstation")):
                messagebox.showwarning("Ruta Inusual", "La carpeta seleccionada no parece ser 'data' o no contiene las subcarpetas de emuladores. Asegúrate de que sea la carpeta correcta de tu captura.")
            self.destino_path.set(path)
            self.verificar_botones()

    def verificar_botones(self):
        if self.origen_path.get() and self.destino_path.get():
            self.btn_procesar.config(state="normal")

    def log(self, mensaje):
        self.txt_log.config(state="normal")
        self.txt_log.insert(tk.END, mensaje + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")
        self.root.update_idletasks()

    def buscar_archivo_recursivo(self, nombre_archivo, ruta_busqueda):
        """Busca un archivo de forma inteligente recorriendo todas las subcarpetas del pack."""
        for raiz, carpetas, archivos in os.walk(ruta_busqueda):
            if nombre_archivo in archivos:
                return os.path.join(raiz, nombre_archivo)
        return None

    def procesar_bios(self):
        origen = self.origen_path.get()
        destino = self.destino_path.get()

        self.txt_log.config(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.config(state="disabled")

        self.log("=== ⚙️ Iniciando escaneo del pack de BIOS... ===")
        archivos_copiados = 0

        # Mapeamos los objetivos del diccionario de forma segura
        for archivo_bios, (subcarpeta, descripcion) in PANDORA_BIOS_MAP.items():
            # Buscar el archivo de forma recursiva en el pack revuelto
            ruta_origen_encontrada = self.buscar_archivo_recursivo(archivo_bios, origen)
            ruta_destino_final_dir = os.path.join(destino, subcarpeta)
            ruta_destino_completa_archivo = os.path.join(ruta_destino_final_dir, archivo_bios)

            if ruta_origen_encontrada:
                try:
                    # Crear la carpeta del emulador si por alguna razón no existía
                    os.makedirs(ruta_destino_final_dir, exist_ok=True)
                    
                    # Copiar de forma segura conservando metadatos sin borrar nada más
                    shutil.copy2(ruta_origen_encontrada, ruta_destino_completa_archivo)
                    self.log(f"[✅ COPIADO] {archivo_bios} -> {subcarpeta}/")
                    archivos_copiados += 1
                except Exception as e:
                    self.log(f"[❌ ERROR] No se pudo copiar {archivo_bios}. Motivo: {e}")
            else:
                self.log(f"[🔍 No Encontrado] '{archivo_bios}' no está en tu pack ({descripcion}).")


# ==================== CONFIGURACIÓN DE RUTAS ====================
# 1. Pon aquí la carpeta de tu memoria que quieres revisar y limpiar:
RUTA_A_REVISAR = "e:/download/roms"

# 2. Pon aquí la ubicación de tu computadora donde quieres guardar los descartes:
# (El script creará una carpeta llamada "Archivos_Pequenos_Descartados" en tu Escritorio)
RUTA_DONDE_GUARDAR_DESCARTE = "e:/download"
# ================================================================

# 1 Megabyte en bytes equivale exactamente a 1,048,576 bytes
LIMITE_BYTES = 1048576 

if not os.path.exists(RUTA_A_REVISAR):
    print(f"Error: La ruta a revisar '{RUTA_A_REVISAR}' no existe.")
    input("\nPresiona Enter para salir...")
    exit()

# Si la carpeta de descarte no existe en tu PC, el script la crea automáticamente
if not os.path.exists(RUTA_DONDE_GUARDAR_DESCARTE):
    os.makedirs(RUTA_DONDE_GUARDAR_DESCARTE)

print("==================================================================")
print("     SCRIPT CONFIGURABLE: SEPARAR ARCHIVOS MENORES A 1 MB        ")
print("==================================================================")
print(f"📁 Carpeta analizada: {RUTA_A_REVISAR}")
print(f"📥 Carpeta de descarte: {RUTA_DONDE_GUARDAR_DESCARTE}\n")

archivos_movidos = 0

# Escaneamos los archivos sueltos de la carpeta objetivo
for archivo in os.listdir(RUTA_A_REVISAR):
    ruta_completa_archivo = os.path.join(RUTA_A_REVISAR, archivo)
    
    if os.path.isfile(ruta_completa_archivo):
        tamano_actual_bytes = os.path.getsize(ruta_completa_archivo)
        
        # Validación de peso menor a 1 MB
        if tamano_actual_bytes < LIMITE_BYTES:
            tamano_en_mb = tamano_actual_bytes / (1024 * 1024)
            print(f"⚠️ [DETECTADO] '{archivo}' pesa solo {tamano_en_mb:.2f} MB. Moviendo...")
            
            try:
                # Movemos el archivo de forma segura hacia la ruta visible del PC
                shutil.move(ruta_completa_archivo, os.path.join(RUTA_DONDE_GUARDAR_DESCARTE, archivo))
                archivos_movidos += 1
            except Exception as e:
                print(f"   [ERROR] No se pudo mover el archivo {archivo}: {e}")

print("\n==================================================================")
print("¡otganizacion completada!")
if archivos_movidos > 0:
    print(f"Se movieron con éxito {archivos_movidos} archivos pequeños a tu PC.")
    print(f"Ruta de destino: {RUTA_DONDE_GUARDAR_DESCARTE}")
else:

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
    # Extensiones críticas que contienen código de emulación o sistemas
CRITICAL_EXTENSIONS = {'.bin', '.rom', '.bios', '.cue'}

# Archivos ZIP o comprimidos específicos que NO son ROMs sino BIOS de sistema
PROTECTED_BIOS_FILES = {
    'neogeo.zip', 'pgm.zip', 'awbios.zip', 'naomi.zip', 
    'syscard3.pce', 'dc_boot.bin', 'dc_flash.bin'
}

def es_archivo_protegido(nombre_archivo):
    """
    Evalúa si un archivo es una BIOS crítica y no debe ser borrado ni alterado.
    Devuelve True si está protegido, False si es seguro operar con él.
    """
    nombre_lower = nombre_archivo.lower()
    
    # 1. Verificar si el nombre exacto está en la lista de BIOS protegidas
    if nombre_lower in PROTECTED_BIOS_FILES:
        return True
        
    # 2. Verificar si tiene una extensión de sistema crítica (.bin, .rom, etc.)
    _, ext = os.path.splitext(nombre_lower)
    if ext in CRITICAL_EXTENSIONS:
        return True
        
    return False

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
