  import os

class SonyFormatDetector:
    def __init__(self, log_callback=None):
        self.log = log_callback if log_callback else print

    def analizar_cabecera_sony(self, ruta_completa_archivo):
        """
        Abre el archivo de forma binaria y lee los primeros sectores.
        Retorna 'playstation', 'psp' o 'indeterminado'.
        """
        if not os.path.exists(ruta_completa_archivo):
            return "indeterminado"

        try:
            # Abrimos el archivo en modo lectura binaria ('rb')
            with open(ruta_completa_archivo, 'rb') as f:
                # Leemos los primeros 2048 bytes (el tamaño estándar de un sector de disco)
                bloque_inicial = f.read(2048)
                
                # --- CASO 1: ARCHIVOS .PBP (EBOOTS) ---
                if b"~PBP" in bloque_inicial:
                    # Inspeccionamos si dentro tiene las firmas de región clásicas de PSX
                    if b"SLUS" in bloque_inicial or b"SLES" in bloque_inicial or b"SCUS" in bloque_inicial or b"SCES" in bloque_inicial:
                        return "playstation"
                    return "psp"

                # --- CASO 2: ARCHIVOS .ISO / .BIN ---
                # Buscamos las cadenas de texto que graba el sistema de archivos de Sony
                if b"PSP GAME" in bloque_inicial or b"UMD_DATA" in bloque_inicial:
                    return "psp"
                
                if b"PLAYSTATION" in bloque_inicial or b"cdrom:\\" in bloque_inicial:
                    return "playstation"

            # --- CASO 3: DETECCIÓN POR NOMBRE O CÓDIGO (FALLBACK DE SEGURIDAD) ---
            nombre_archivo_lower = os.path.basename(ruta_completa_archivo).lower()
            if "slus-" in nombre_archivo_lower or "sles-" in nombre_archivo_lower or "sces-" in nombre_archivo_lower:
                return "playstation"
            if "ulus-" in nombre_archivo_lower or "ules-" in nombre_archivo_lower or "npugh" in nombre_archivo_lower:
                return "psp"

            # --- CASO 4: FILTRO POR PESO INTEGRADO ---
            # Si la cabecera está encriptada, recurrimos al límite físico del hardware.
            # El CD-ROM de PSX no supera los 750 MB. El UMD de PSP llega hasta 1.8 GB.
            peso_mb = os.path.getsize(ruta_completa_archivo) / (1024 * 1024)
            if peso_mb < 720:
                return "playstation"
            return "psp"

        except Exception as e:
            self.log(f"⚠️ Alerta en detector binario: {e}")
            return "indeterminado"
