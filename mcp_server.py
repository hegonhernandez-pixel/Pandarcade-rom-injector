#mcp_server.py
import os
import sys
import json
import google.generativeai as genai

# 🔥 LEER LA INYECCIÓN DE LLAVE QUE COLOCASTE
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def procesar_mcp_prompt(prompt_texto):
    """ El núcleo que ejecuta la llamada fromsource nativa sin pasar por Cloud """
    try:
        if not GOOGLE_API_KEY:
            return {"status": "error", "message": "Falta la GOOGLE_API_KEY en el entorno local."}
            
        # Invocamos al modelo ultra-moderno y actualizado de Gemini
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(prompt_texto)
        
        if response and response.text:
            return {"status": "success", "data": response.text}
        return {"status": "error", "message": "El modelo regresó una matriz vacía."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Simulación del protocolo de comunicación por tuberías (STDIN/STDOUT) del estándar MCP
    print("🟩 [PANDARCADE MCP] Servidor de IA activo mediante código fuente local.")
    
    # Pruebita en frío para verificar que tus librerías actuales muerdan el prompt
    test_prompt = "Genera una ráfaga de 3 ideas de prompts visuales cinemáticos para Google Veo sobre Killer Instinct estilo retro arcade."
    resultado = procesar_mcp_prompt(test_prompt)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
