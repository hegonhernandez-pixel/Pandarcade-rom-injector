# mcp_server.py
import os
import sys
import json

# 🔥 ACTUALIZACIÓN DE VANGUARDIA: Usamos el nuevo paquete unificado de Google
try:
    from google import genai
    from google.genai import types
    SDK_NUEVO = True
except ImportError:
    SDK_NUEVO = False

# 🔐 INYECCIÓN COMERCIAL DIRECTA: Pega aquí tu clave de Gemini (la de ai.google.dev)
# Esto elimina el error de "Falta la llave" de golpe y para siempre
MI_LLAVE_SECRET_GEMINI = "Ask-svcacct-_1chcTsEOPPE52hn01qxCJfBilAYipHn7Vm_Hib3iRzoGlZ3rN4U0oM29PSX7y8or1gGVaxj0CT3BlbkFJxbmRZcIYXv5Is2imcWUeCzsZCklgC4_rfsY1Q_VHsRwvqi9AFHK_l5GedkamqOhOPyt-yJvAoA"

def procesar_mcp_prompt(prompt_texto):
    """ El núcleo 'from source' que ejecuta la llamada usando el nuevo SDK global """
    try:
        # Usamos tu llave fija o buscamos si hay una en el entorno
        llave_activa = MI_LLAVE_SECRET_GEMINI if MI_LLAVE_SECRET_GEMINI != "AQUÍ_PEGA_TU_LLAVE_API_DE_GEMINI" else os.getenv("GOOGLE_API_KEY")
        
        if not llave_activa:
            return {"status": "error", "message": "Falta configurar tu LLAVE API dentro del archivo mcp_server.py."}
            
        if not SDK_NUEVO:
            return {"status": "error", "message": "Falta instalar el nuevo paquete. Corre: pip install google-genai"}

        # Instanciamos el cliente moderno oficial de Google
        client = genai.Client(api_key=llave_activa)
        
        # El método moderno de última generación que Google exige
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_texto,
        )
        
        if response and response.text:
            return {"status": "success", "data": response.text}
        return {"status": "error", "message": "El modelo de nueva generación regresó una matriz vacía."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("🔮 [PANDARCADE MCP V.NEXT] Servidor con SDK Unificado de Google Activo.")
    
    # Pruebita en frío para verificar el destrabe del bus de datos
    test_prompt = "Genera una ráfaga de 3 ideas de prompts visuales cinemáticos para Google Veo sobre Killer Instinct estilo retro arcade."
    resultado = procesar_mcp_prompt(test_prompt)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
