document.addEventListener('DOMContentLoaded', function() {
    // Ajustar el termómetro según la temperatura
    const liquidoTermometro = document.querySelector('.liquido-termometro');
    const termometroContainer = document.querySelector('.termometro');
    const temp = parseFloat(termometroContainer.dataset.temp);
    
    // Asignar clase según rango de temperatura
    if (temp < 36) {
        liquidoTermometro.classList.add('temp-normal');
    } else if (temp <= 37.5) {
        liquidoTermometro.classList.add('temp-elevada');
    } else if (temp <= 41) {
        liquidoTermometro.classList.add('temp-fiebre');
    } else {
        liquidoTermometro.classList.add('temp-peligro');
    }
    
    // Configurar la animación del corazón según la frecuencia
    const corazon = document.getElementById('corazon');
    const frecuenciaText = document.querySelector('.etiqueta').textContent;
    let frecuencia = 60; // valor por defecto
    
    // Extraer el valor numérico de la frecuencia
    const match = frecuenciaText.match(/\d+/);
    if (match) {
        frecuencia = parseInt(match[0]);
    }
    
    // Calcular duración de la animación basada en la frecuencia cardíaca
    const duracionAnimacion = 60 / frecuencia;
    
    // Aplicar animación con la duración calculada
    corazon.style.animation = `latido ${duracionAnimacion}s infinite`;
    
    // Para la gota de SpO2, cambiar color según valor
    const gotaSangre = document.querySelector('.gota-sangre');
    const valorSpO2Text = document.querySelector('.valor-spo2').textContent;
    const valorSpO2 = parseInt(valorSpO2Text);
    
    // Cambiar color de la gota según el rango de SpO2
    if (valorSpO2 < 90) {
        gotaSangre.style.background = '#e74c3c'; // Rojo para valores bajos
    } else if (valorSpO2 < 95) {
        gotaSangre.style.background = '#f39c12'; // Naranja para valores intermedios
    } else {
        gotaSangre.style.background = '#ff4757'; // Color normal
    }
    
    // Ajustar velocidad de animación del ECG interno según frecuencia
    const lineaECGInterna = document.querySelector('.linea-ecg-interna');
    
    // Más rápido para frecuencias más altas, más lento para bajas
    const duracionECG = 60 / frecuencia * 1.5; // Base duration 1.5s for faster animation
    
    if (lineaECGInterna) {
        lineaECGInterna.style.animation = `moverECGInterno ${duracionECG}s linear infinite`;
    }
});