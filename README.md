# RaspberryPi

# 🚀 Proceso Recomendado para Configurar tu API en la Raspberry Pi

Este documento detalla los pasos necesarios para configurar y ejecutar tu API en una Raspberry Pi, incluyendo la instalación de dependencias y la ejecución del servidor FastAPI. Sigue cada paso cuidadosamente para evitar problemas.

## 📋 Resumen del Proceso

Configurarás tu Raspberry Pi para ejecutar una API basada en FastAPI que interactúa con sensores (DHT22 y MAX30100). Esto incluye actualizar el sistema, instalar Python y pip, configurar el hardware, crear un entorno virtual, instalar librerías, transferir tu proyecto y ejecutar la API.

---

## 🛠️ Pasos para la Configuración

### 1️⃣ **Actualiza el Sistema e Instala Python y pip**

Asegúrate de que tu Raspberry Pi esté actualizada y que tengas Python y pip instalados:

- **comandos:**
    
    `sudo apt update
    sudo apt install python3 python3-pip python3-dev libatlas-base-dev -y`
    
- **Verifica pip**:
    
    `python3 -m pip --version`
    
- **Si pip falla, instálalo manualmente**:
    
    `curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py`
    

> 💡 Nota: Si pip no funciona después de instalarlo con apt, el script get-pip.py lo instalará directamente para tu versión de Python.
> 

---

### 2️⃣ **Habilita Interfaces de Hardware**

Habilita I2C para el sensor MAX30100 y verifica otras interfaces si es necesario.

- **Habilita I2C**:
    
    `sudo raspi-config`
    
    - Ve a *Interfacing Options* > Habilita I2C.
    - Sal y reinicia si se solicita:
        
        `sudo reboot`
        

---

### 3️⃣ **Crea un Entorno Virtual**

Usa un entorno virtual para aislar las dependencias de tu proyecto.

- **Crea un directorio para tu proyecto**:
    
    `mkdir /home/pi/Oxisense
    cd /home/pi/Oxisense`
    
- **Crea y activa el entorno virtual**:
    
    `python3 -m venv venv
    source venv/bin/activate`
    

> ✅ Confirmación: Cuando el entorno virtual esté activado, verás (venv) en tu terminal.
> 

---

### 4️⃣ **Instala las Librerías con pip**

Instala todas las librerías necesarias para tu API, incluyendo las específicas para los sensores.

- **Comando para instalar todo**:

`pip install Adafruit-Blinka adafruit-circuitpython-dht max30100 RPi.GPIO fastapi uvicorn jinja2 setuptools`

`pip3 install --upgrade adafruit-blinka adafruit-platformdetect`

- **copiar el repositorio de la libreria max30100**
    - `git clone https://github.com/mfitzp/max30100`

### 📦 **Lista de Librerías Instaladas**

- Adafruit-Blinka: Para el módulo board.
- adafruit-circuitpython-dht: Para el sensor DHT22.
- max30100: Para el sensor MAX30100.
- RPi.GPIO: Para controlar GPIO.
- fastapi: Framework para la API.
- uvicorn: Servidor para FastAPI.
- jinja2: Para renderizar plantillas HTML.
- setuptools: Para evitar errores con pkg_resources.

---

### 5️⃣ **Si pip Falla, Usa apt para lo que Puedas**

Si no puedes usar pip, intenta instalar algunas librerías con apt, pero ten en cuenta que no todas estarán disponibles.

- **Instala con apt**:
    
    `sudo apt install python3-rpi.gpio python3-jinja2 python3-fastapi python3-setuptools -y`
    
- **Limitaciones**:
    - Módulos como max30100, adafruit-circuitpython-dht y uvicorn no están en apt y requieren pip.

> ⚠️ Advertencia: Resuelve el problema con pip lo antes posible, ya que es la forma más confiable de instalar todas las dependencias.
> 

---

### 6️⃣ **Copia tu Carpeta y Ejecuta**

Transfiere tu proyecto a la Raspberry Pi y ejecuta tu API.

- **Copia tu Carpeta**:
    - **Opción 1: USB**
    Copia la carpeta Oxisense a un USB, conéctalo a la Raspberry Pi y muévela a /home/pi/Oxisense.
    - **Opción 2: SCP**
    Desde tu portátil:
    
    (Reemplaza <IP-de-tu-Raspberry-Pi> con la IP de tu Raspberry, como 192.168.1.x).
        
        `scp -r /ruta/en/tu/portatil/Oxisense pi@<IP-de-tu-Raspberry-Pi>:/home/pi/Oxisense`
        
    - **Opción 3: Git**
    Si tu proyecto está en un repositorio:
        
        `git clone <URL-de-tu-repositorio>`
        
- **Verifica la Estructura**:
Asegúrate de que /home/pi/Oxisense tenga:
    - main.py
    - static/script.js
    - static/style.css
    - templates/index.html
- **Ejecuta la API**:
    
    `python -m uvicorn main:app --host 0.0.0.0 --port 5000`
    
    - Accede desde un navegador: http://<IP-de-tu-Raspberry-Pi>:5000.

---

## 🌟 Consejos Adicionales

- **Pruebas Iniciales**: Usa Thonny para probar pequeños fragmentos de código (como la lectura de sensores), pero ejecuta la API con uvicorn desde la terminal para mejor control.
- **Depuración**: Si encuentras errores, verifica los logs en la terminal y asegúrate de que todas las librerías estén instaladas.
- **Acceso Remoto**: Si usas --host 0.0.0.0, puedes acceder a la API desde otros dispositivos en la misma red usando la IP de la Raspberry Pi.

---

## 📝 Notas Finales

Este proceso está diseñado para que tu API funcione correctamente en la Raspberry Pi. Si encuentras problemas (como errores al instalar pip o módulos), revisa las soluciones en cada paso. ¡Tu proyecto está a punto de funcionar! 🚀

**Entorno Virtual y Thonny**:

- Thonny no usa automáticamente el entorno virtual (venv). Si instalaste las librerías en un entorno virtual, Thonny podría usar el intérprete global de Python, donde las librerías no están instaladas.
- Esto causaría errores como ModuleNotFoundError.

**Solución**:
Configura Thonny para usar el intérprete del entorno virtual:

- Abre Thonny.
- Ve a Tools > Options > Interpreter.
- Selecciona el intérprete de tu entorno virtual (por ejemplo, /home/pi/Oxisense/venv/bin/python3).
- Aplica los cambios y reinicia Thonny.
