from max30100 import MAX30100
from scipy.signal import find_peaks
import time 

def leer_oximetro(duracion=5):
    """
    Lee los datos del sensor MAX30100 conectado a los pines I2C (SDA: GPIO 3, SCL: GPIO 5)
    Devuelve: (bpm, spo2)
    - bpm: Pulsaciones por minuto (redondeado)
    - spo2: Saturación de oxígeno en sangre (redondeado)
    """
    sensor = MAX30100()
    sensor.enable_spo2()
    ir_data = []
    
    try:
        start = time.time()
        print(f"Iniciando lectura de {duracion} segundos...")
        
        while time.time() - start < duracion:
            sensor.read_sensor()
            if sensor.ir is not None:
                ir_data.append(sensor.ir)
            time.sleep(0.01)  # Intervalo más corto para mejor precisión
        
        # Procesamiento de señales
        if len(ir_data) < 10:  # Mínimo de muestras
            return 0, 0
            
        peaks, _ = find_peaks(ir_data, distance=15, height=0.6*max(ir_data))
        bpm = (len(peaks) / duracion) * 60 if len(peaks) > 1 else 0
        
        return round(bpm), round(sensor.red if sensor.red else 0)
        
    except Exception as e:
        print(f"Error en lectura del oxímetro: {e}")
        return 0, 0
    finally:
        sensor.shutdown()

# Ejemplo de uso
if __name__ == "__main__":
    while True:
        try:
            bpm, spo2 = leer_oximetro(10)  # 10 segundos de medición
            print(f"BPM: {bpm}, SpO2: {spo2}%")
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nMedición finalizada")
            break
