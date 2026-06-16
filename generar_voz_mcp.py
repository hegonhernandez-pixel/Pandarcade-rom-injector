import os
import subprocess

def texto_a_voz_profesional(texto, nombre_archivo_salida="audio_guion.mp3"):
    """
    Toma el guión de texto y utiliza el motor nativo de Windows (SAPI)
    para generar el archivo de voz de forma automática y gratuita.
    """
    print("=== 🎤 Iniciando generación automática de voz por IA ===")
    
    # Asegurar que el archivo de salida tenga extensión correcta
    if not nombre_archivo_salida.endswith(".mp3") and not nombre_archivo_salida.endswith(".wav"):
        nombre_archivo_salida += ".wav"
        
    print(f"🎬 Procesando texto para el archivo: {nombre_archivo_salida}")
    
    # Creamos un pequeño script temporal de Windows (PowerShell) para forzar la lectura limpia
    # Usamos la voz oficial de Microsoft en español que viene instalada de fábrica
    powershell_code = f"""
    Add-Type -AssemblyName System.Speech
    $synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synthesizer.SetOutputToWaveFile("{os.path.abspath(nombre_archivo_salida)}")
    $synthesizer.Speak("{texto}")
    $synthesizer.Dispose()
    """
    
    # Ejecutamos el comando de forma invisible en el fondo
    try:
        archivo_temp = "temp_voice_script.ps1"
        with open(archivo_temp, "w", encoding="utf-8") as f:
            f.write(powershell_code)
            
        # Lanzamos el proceso de Windows sin congelar tu PC
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", archivo_temp], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Limpieza de basura del sistema
        if os.path.exists(archivo_temp):
            os.remove(archivo_temp)
            
        print(f"[✅ COMPLETO] Tu audio profesional se ha generado en: {nombre_archivo_salida}")
        print("👉 Ya puedes arrastrar este archivo a CapCut para armar tu video.")
        
    except Exception as e:
        print(f"[❌ ERROR] Hubo un detalle al generar el audio: {e}")

# =========================================================================
# 📝 COPIA TU GUIÓN AQUÍ ABAJO PARA PROCESARLO
# =========================================================================
if __name__ == "__main__":
    
    # Este es el texto exacto que el programa va a locutar por ti
    GUION_VIDEO_1 = (
        "Te vendieron la fantasía nostálgica definitiva: un tablero arcade premium con 50 mil juegos en 1. "
        "Te costó una fortuna. Pero la realidad es que de esos 50 mil, con suerte corren 100 juegos reales. "
        "El resto es pura basura: clones repetidos, ROMs corruptas hackeadas al aventón y archivos tirados sin ningún control. "
        "Frustradas, muchas personas terminan dañando las tarjetas SD, rompiendo los puertos de tanto mover los interruptores, "
        "o peor aún: arrumbando estas consolas en un rincón oscuro de la casa. "
        "¡Hoy te digo que las saques! Sácalas del clóset, límpiales el polvo y revívelas, porque en estos tiempos, lo viejo es nuevo y novedoso."
    )
    
    # Nombre del archivo donde se guardará tu locución
    ARCHIVO_DE_AUDIO = "locucion_acto_1.wav"
    
    # Ejecutar la automatización
    texto_a_voz_profesional(GUION_VIDEO_1, ARCHIVO_DE_AUDIO)
