import time
import board
import adafruit_dht
import RPi.GPIO as GPIO
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import uvicorn

# Importar la clase MAX30100
from max30100 import MAX30100

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configuración de pines
DHT_PIN = 7     # GPIO 7 para DHT11
BUZZER_PIN = 18 # GPIO 18 para el buzzer
# MAX30100 usa I2C: SDA=GPIO2/Pin3, SCL=GPIO3/Pin5

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.LOW)

print("=" * 50)
print("🚀 INICIANDO SISTEMA DE MONITOREO")
print("=" * 50)

# Inicializar DHT11
try:
    dht = adafruit_dht.DHT11(board.D7, use_pulseio=False)
    print("✅ DHT11 inicializado en GPIO 7")
except Exception as e:
    print(f"❌ Error DHT11: {e}")
    dht = None

# Inicializar MAX30100
try:
    max_sensor = MAX30100(
        mode=0x03,  # Modo SpO2
        sample_rate=100,
        led_current_red=11.0,
        led_current_ir=11.0,
        pulse_width=1600
    )
    print("✅ MAX30100 inicializado en I2C")
except Exception as e:
    print(f"❌ Error MAX30100: {e}")
    max_sensor = None

def valores_en_rango(frec, spo2, temp):
    return 60 <= frec <= 100 and 95 <= spo2 <= 100 and 36 <= temp <= 37.5

def control_buzzer(alerta):
    if alerta:
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        print("🚨 BUZZER ACTIVADO - ALERTA")
    else:
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        print("🔇 Buzzer desactivado")

def read_sensors():
    print("\n" + "="*40)
    print("📊 LEYENDO SENSORES...")
    print("="*40)
    
    # === LEER DHT11 ===
    temperature = None
    humidity = None
    
    if dht:
        print("🌡️  Leyendo DHT11...")
        for attempt in range(5):
            try:
                temperature = dht.temperature
                humidity = dht.humidity
                
                print(f"   Intento {attempt + 1}:")
                print(f"   - Temperatura cruda: {temperature}")
                print(f"   - Humedad cruda: {humidity}")
                
                if temperature is not None and humidity is not None:
                    print(f"✅ DHT11 OK - Temp: {temperature}°C, Hum: {humidity}%")
                    break
                else:
                    print(f"⚠️  Intento {attempt + 1} falló, reintentando...")
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Error en intento {attempt + 1}: {e}")
                time.sleep(1)
        
        if temperature is None or humidity is None:
            print("❌ DHT11: No se pudieron obtener datos válidos")
            return None
    else:
        print("❌ DHT11: Sensor no disponible")
        return None

    # === LEER MAX30100 ===
    spo2 = None
    heart_rate = None
    
    if max_sensor:
        print("\n💓 Leyendo MAX30100...")
        try:
            # Habilitar SpO2
            max_sensor.enable_spo2()
            time.sleep(2)  # Tiempo de estabilización
            
            print("   Tomando muestras...")
            valid_samples = 0
            red_values = []
            ir_values = []
            
            for i in range(20):  # Más muestras para mejor precisión
                try:
                    max_sensor.read_sensor()
                    
                    if max_sensor.red and max_sensor.ir:
                        red_val = max_sensor.red
                        ir_val = max_sensor.ir
                        
                        print(f"   Muestra {i+1}: RED={red_val}, IR={ir_val}")
                        
                        # Filtrar valores válidos (no muy bajos)
                        if red_val > 1000 and ir_val > 1000:
                            red_values.append(red_val)
                            ir_values.append(ir_val)
                            valid_samples += 1
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"   Error en muestra {i+1}: {e}")
            
            print(f"   Muestras válidas obtenidas: {valid_samples}")
            
            if valid_samples > 5:  # Necesitamos al menos 5 muestras válidas
                # Promediar valores
                avg_red = sum(red_values) / len(red_values)
                avg_ir = sum(ir_values) / len(ir_values)
                
                print(f"   Promedio RED: {avg_red:.0f}")
                print(f"   Promedio IR: {avg_ir:.0f}")
                
                # Calcular ratio R
                if avg_ir > 0:
                    ratio = avg_red / avg_ir
                    print(f"   Ratio R (RED/IR): {ratio:.3f}")
                    
                    # Fórmula empírica para SpO2 (calibrable)
                    spo2 = 110 - 25 * ratio
                    spo2 = max(85, min(100, spo2))
                    
                    # Estimación básica de HR basada en variabilidad
                    # En implementación real necesitarías FFT o detección de picos
                    hr_estimate = 70 + (ratio - 0.5) * 30
                    heart_rate = max(50, min(120, hr_estimate))
                    
                    print(f"✅ MAX30100 calculado - SpO2: {spo2:.1f}%, HR: {heart_rate:.1f} bpm")
                else:
                    print("❌ División por cero en cálculo de ratio")
                    return None
            else:
                print("❌ MAX30100: Insuficientes muestras válidas")
                return None
                
        except Exception as e:
            print(f"❌ Error general MAX30100: {e}")
            return None
    else:
        print("❌ MAX30100: Sensor no disponible")
        return None

    # === VERIFICAR ALERTA ===
    alerta = not valores_en_rango(heart_rate, spo2, temperature)
    
    print(f"\n📋 RESUMEN DE LECTURAS:")
    print(f"   🌡️  Temperatura: {temperature:.1f}°C")
    print(f"   💧 Humedad: {humidity:.1f}%")
    print(f"   🫀 Frecuencia: {heart_rate:.1f} bpm")
    print(f"   🩸 SpO2: {spo2:.1f}%")
    print(f"   ⚠️  Alerta: {'SÍ' if alerta else 'NO'}")
    
    if alerta:
        print("🚨 VALORES FUERA DE RANGO NORMAL:")
        if not (60 <= heart_rate <= 100):
            print(f"   - Frecuencia cardíaca: {heart_rate:.1f} (normal: 60-100)")
        if not (95 <= spo2 <= 100):
            print(f"   - SpO2: {spo2:.1f}% (normal: 95-100%)")
        if not (36 <= temperature <= 37.5):
            print(f"   - Temperatura: {temperature:.1f}°C (normal: 36-37.5°C)")

    control_buzzer(alerta)

    return {
        "spo2": round(spo2, 1),
        "frecuencia": round(heart_rate, 1),
        "temperatura": round(temperature, 1),
        "humedad": round(humidity, 1),
        "edad": 25,
        "ejercicio": "no",
        "alerta": alerta
    }

# Rutas de FastAPI
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = read_sensors()
    if data is None:
        # En caso de error, devolver valores por defecto para evitar crash
        data = {
            "spo2": 0,
            "frecuencia": 0,
            "temperatura": 0,
            "humedad": 0,
            "edad": 25,
            "ejercicio": "no",
            "alerta": True
        }
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        **data
    })

@app.get("/api/data")
async def api_data():
    data = read_sensors()
    if data is None:
        return {"error": "No se pudieron leer los sensores"}
    return data

# Limpieza
def cleanup():
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.cleanup()
    print("🧹 GPIO limpiado")

import atexit
atexit.register(cleanup)

if __name__ == "__main__":
    print("\n🌐 Servidor web iniciando en http://0.0.0.0:5000")
    print("💡 Presiona Ctrl+C para detener")
    print("📊 Los datos se mostrarán en consola cada vez que se lean")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida por el usuario")
        cleanup()
    except Exception as e:
        print(f"❌ Error: {e}")
        cleanup()