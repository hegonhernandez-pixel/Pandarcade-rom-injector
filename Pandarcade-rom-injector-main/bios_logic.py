import os
import shutil

# Diccionario maestro con mapeo exacto a tu captura de pantalla de Pandora
PANDORA_BIOS_MAP = {
    "scph5501.bin": ["playstation", "BIOS PS1 Americana (Recomendada)"],
    "scph1001.bin": ["playstation", "BIOS PS1 Alternativa"],
    "scph7001.bin": ["playstation", "BIOS PS1 Slim"],
    "scph5501.bin": ["common", "Copia de PS1 en Carpeta Común"],
    "dc_boot.bin": ["dreamcast", "Boot ROM de Dreamcast"],
    "dc_flash.bin": ["dreamcast", "Flash NVRAM de Dreamcast"],
    "awbios.zip": ["dreamcast", "BIOS obligatoria para Atomiswave"],
    "naomi.zip": ["dreamcast", "BIOS obligatoria para Naomi"],
    "awbios.zip": ["common", "Copia de Atomiswave en Carpeta Común"],
    "bios_CD_U.bin": ["common", "BIOS Sega CD - Región USA"],
    "bios_CD_E.bin": ["common", "BIOS Sega CD - Región Europa"],
    "bios_CD_J.bin": ["common", "BIOS Sega CD - Región Japón"],
    "gba_bios.bin": ["gba", "BIOS obligatoria para Game Boy Advance"],
    "syscard3.pce": ["pcengine", "System Card 3.0 para TurboGrafx-16 CD"],
    "neogeo.zip": ["mame19", "BIOS NeoGeo para MAME 19"],
    "neogeo.zip": ["mame37", "BIOS NeoGeo para MAME 37"],
    "neogeo.zip": ["mame78", "BIOS NeoGeo para MAME 78"],
    "neogeo.zip": ["mame139", "BIOS NeoGeo para MAME 139"],
    "neogeo.zip": ["fba42", "BIOS NeoGeo para FinalBurn Alpha"],
    "pgm.zip": ["mame78", "BIOS PolyGame Master"],
}

def buscar_archivo_recursivo(nombre_archivo, ruta_busqueda):
    """Busca un archivo recorriendo recursivamente todas las subcarpetas del pack."""
    for raiz, _, archivos in os.walk(ruta_busqueda):
        if nombre_archivo in archivos:
            return os.path.join(raiz, nombre_archivo)
    return None

def ejecutar_inyeccion_bios(origen, destino, log_callback):
    """Ejecuta la copia e informa el progreso en tiempo real mediante un callback."""
    log_callback("=== ⚙️ Iniciando escaneo del pack de BIOS... ===")
    archivos_copiados = 0

    for archivo_bios, (subcarpeta, descripcion) in PANDORA_BIOS_MAP.items():
        ruta_origen_encontrada = buscar_archivo_recursivo(archivo_bios, origen)
        ruta_destino_final_dir = os.path.join(destino, subcarpeta)
        ruta_destino_completa_archivo = os.path.join(ruta_destino_final_dir, archivo_bios)

        if ruta_origen_encontrada:
            try:
                os.makedirs(ruta_destino_final_dir, exist_ok=True)
                shutil.copy2(ruta_origen_encontrada, ruta_destino_completa_archivo)
                log_callback(f"[✅ COPIADO] {archivo_bios} -> {subcarpeta}/")
                archivos_copiados += 1
            except Exception as e:
                log_callback(f"[❌ ERROR] No se pudo copiar {archivo_bios}. Motivo: {e}")
        else:
            log_callback(f"[🔍 No Encontrado] '{archivo_bios}' no está en tu pack ({descripcion}).")

    log_callback(f"\n=== ✨ PROCESO COMPLETADO ===")
    return archivos_copiados
