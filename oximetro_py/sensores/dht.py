import time
import board
import adafruit_dht

# Inicializar el sensor DHT11 (conectado al pin GPIO 4)
dht = adafruit_dht.DHT11(board.D4)

def leer_temperatura():
    """
    Lee la temperatura del sensor DHT11.
    Devuelve la temperatura en Celsius o 0 si hay error.
    """
    try:
        temp_c = dht.temperature
        humidity = dht.humidity  # También leemos humedad aunque no la devolvamos
        
        # Validación básica de valores (el DHT11 devuelve None si hay error)
        if temp_c is None:
            print("Error: Lectura de temperatura inválida")
            return 0
            
        print(f"Lectura exitosa: Temperatura: {temp_c}°C, Humedad: {humidity}%")
        return temp_c
        
    except RuntimeError as e:
        print(f"Error en la lectura del sensor: {e}")
        return 0
    except Exception as e:
        print(f"Error inesperado: {e}")
        return 0

# Ejemplo de uso si se ejecuta este archivo directamente
if __name__ == "__main__":
    try:
        while True:
            temp = leer_temperatura()
            print(f"Temperatura leída: {temp}°C")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Programa detenido")
    finally:
        dht.exit()

