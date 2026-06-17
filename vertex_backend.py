# vertex_backend.py
import os
import time
import subprocess
import requests
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Pandarcade Lab Commercial API", version="1.0.0")

# 🔥 INTEGRACIÓN CYBERPUNK: Permitir que tu página web se conecte sin bloqueos de red
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Aquí pondrás la URL final de tu página web de GitHub Pages
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 CONTROL DE ACCESO: Cabecera para validar las cuotas mensuales de los usuarios
API_KEY_NAME = "X-Pandarcade-Token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Simulación de base de datos de usuarios premium que pagan suscripción
USUARIOS_PREMIUM = {
    "user_vip_kinst_tk": {"plan": "Premium", "renders_hoy": 0, "limite": 100},
    "user_demo_arcade_retro": {"plan": "Free", "renders_hoy": 0, "limite": 5}
}

class RequestPrompt(BaseModel):
    prompt: str

def obtener_token_gcloud():
    """ Extrae el token dinámico del servidor de forma interna e invisible """
    try:
        resultado = subprocess.check_output(["gcloud", "auth", "print-access-token"], shell=True)
        return resultado.decode("utf-8").strip()
    except Exception:
        return None

async def validar_suscripcion(api_key: str = Depends(api_key_header)):
    """ Valida analíticamente si el cliente pagó su cuota mensual """
    if not api_key or api_key not in USUARIOS_PREMIUM:
        raise HTTPException(status_code=403, detail="Acceso Denegado: Suscripción inválida o vencida.")
    
    usuario = USUARIOS_PREMIUM[api_key]
    if usuario["renders_hoy"] >= usuario["limite"]:
        raise HTTPException(status_code=429, detail="Límite alcanzado: Has agotado tu cuota de video de hoy.")
    
    return api_key

@app.post("/v1/generate-video")
async def api_generar_video(payload: RequestPrompt, token_cliente: str = Depends(validar_suscripcion)):
    """ Endpoint comercial oculto que canibaliza el motor de Google Veo """
    token_google = obtener_token_gcloud()
    if not token_google:
        raise HTTPException(status_code=500, detail="Error de infraestructura interna de la nube.")

    project_id = "inyector-video"
    location = "us-central1"
    url_api = f"https://{location}://googleapis.com{project_id}/locations/{location}/publishers/google/models/veo-2.0-generate-video:predict"
    
    cabeceras = {
        "Authorization": f"Bearer {token_google}",
        "Content-Type": "application/json"
    }

    datos_json = {
        "instances": [{"prompt": payload.prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "1:1",
            "durationSeconds": 5,
            "outputMimeType": "video/mp4"
        }
    }

    try:
        respuesta = requests.post(url_api, json=datos_json, headers=cabeceras)
        if respuesta.status_code != 200:
            raise HTTPException(status_code=respuesta.status_code, detail="Fallo en la GPU de Google.")

        resultado = respuesta.json()
        predictions = resultado.get("predictions", [])
        
        if predictions and len(predictions) > 0 and "videoBytes" in predictions[0]:
            # Sumar render al contador del cliente que está pagando
            USUARIOS_PREMIUM[token_cliente]["renders_hoy"] += 1
            
            # Devolvemos la cadena en Base64 directa a la página web del cliente
            return {
                "status": "success",
                "videoBytes": predictions[0]["videoBytes"],
                "filename": f"render_{int(time.time())}.mp4"
            }
        
        raise HTTPException(status_code=500, detail="La nube devolvió una matriz vacía.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
