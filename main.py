import time
import board
import adafruit_dht
import max30100
import RPi.GPIO as GPIO
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random
import logging
import uvicorn

# Configuración de logging para depuración
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configuración de los sensores y buzzer
DHT_PIN = 4  # GPIO 4 para DHT11
BUZZER_PIN = 18  # GPIO 18 para el buzzer
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.LOW)  # Buzzer apagado inicialmente

# Inicializar DHT11
try:
    dht = adafruit_dht.DHT11(board.D4, use_pulseio=False)
except Exception as e:
    logger.warning(f"No se pudo inicializar DHT11: {e}. Usando datos simulados.")
    dht = None

# Inicializar MAX30100
try:
    max_sensor = max30100.MAX30100()
except Exception as e:
    logger.warning(f"No se pudo inicializar MAX30100: {e}. Usando datos simulados.")
    max_sensor = None

# Función para verificar rangos seguros
def valores_en_rango(frec, spo2, temp):
    return 60 <= frec <= 100 and 95 <= spo2 <= 100 and 36 <= temp <= 37.5

# Función para controlar el buzzer
def control_buzzer(alerta):
    if alerta:
        GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Activar buzzer
        logger.info("🚨 Buzzer activado (alerta)")
    else:
        GPIO.output(BUZZER_PIN, GPIO.LOW)  # Desactivar buzzer
        logger.info("Buzzer desactivado")

# Función para leer datos de los sensores
def read_sensors():
    # Leer DHT11 (temperatura y humedad)
    try:
        if dht:
            temperature = dht.temperature
            humidity = dht.humidity
            if temperature is None or humidity is None:
                raise ValueError("Error al leer DHT11")
        else:
            raise ValueError("DHT11 no disponible")
    except Exception as e:
        logger.error(f"Error al leer DHT11: {e}. Usando datos simulados.")
        temperature = round(random.uniform(34.5, 38.5), 1)
        humidity = round(random.uniform(30, 70), 1)

    # Leer MAX30100 (SpO2 y frecuencia cardíaca)
    try:
        if max_sensor:
            max_sensor.enable_spo2()
            time.sleep(1)  # Esperar a que el sensor se estabilice
            spo2_samples = []
            hr_samples = []
            for _ in range(5):
                spo2_samples.append(max_sensor.read_spo2())
                hr_samples.append(max_sensor.read_heart_rate())
                time.sleep(0.1)
            spo2 = sum(spo2_samples) / len(spo2_samples)
            heart_rate = sum(hr_samples) / len(hr_samples)
        else:
            raise ValueError("MAX30100 no disponible")
    except Exception as e:
        logger.error(f"Error al leer MAX30100: {e}. Usando datos simulados.")
        spo2 = random.randint(90, 100)
        heart_rate = random.randint(50, 110)

    # Verificar si hay alerta
    alerta = not valores_en_rango(heart_rate, spo2, temperature)

    # Controlar el buzzer
    control_buzzer(alerta)

    return {
        "spo2": round(spo2, 1),
        "frecuencia": round(heart_rate, 1),
        "temperatura": round(temperature, 1),
        "humedad": round(humidity, 1),
        "edad": 25,
        "ejercicio": "si",
        "alerta": alerta
    }

# Ruta principal para renderizar el HTML
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = read_sensors()
    return templates.TemplateResponse("index.html", {
        "request": request,
        **data
    })

# Endpoint API para datos en formato JSON
@app.get("/api/data")
async def api_data():
    data = read_sensors()
    return data

# Limpieza al cerrar la aplicación
def cleanup():
    GPIO.cleanup()
    logger.info("GPIO limpiado.")

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        logger.error(f"Error en la aplicación: {e}")
        cleanup()