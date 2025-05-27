from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sensores.oxi import leer_oximetro
from sensores.dht import leer_temperatura

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    try:
        # Lectura del oxímetro con tiempo de muestreo adecuado (10 segundos)
        frecuencia, spo2 = leer_oximetro(duracion=10)
        
        # Lectura de temperatura
        temperatura = leer_temperatura()
        
        # Lógica de alerta (valores médicamente relevantes)
        alerta = (
            frecuencia < 50 or frecuencia > 120 or  # Rango normal de BPM: 50-120
            spo2 < 90 or                           # SpO2 bajo: <90%
            temperatura > 38                        # Fiebre: >38°C
        )
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "frecuencia": frecuencia if frecuencia else 0,
            "spo2": spo2 if spo2 else 0,
            "temperatura": temperatura if temperatura is not None else 0,
            "alerta": alerta
        })
        
    except Exception as e:
        print(f"Error en la lectura de sensores: {e}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "frecuencia": 0,
            "spo2": 0,
            "temperatura": 0,
            "alerta": True  # Activa alerta por fallo del sistema
        })