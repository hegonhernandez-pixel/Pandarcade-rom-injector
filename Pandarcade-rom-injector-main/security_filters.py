import os

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
