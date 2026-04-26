// SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);

const LABEL_INFO = {
  "glass bottle":   { text: "🟢 Vidrio",      color: "#00cc44" },
  "plastic bottle": { text: "🟡 Plástico",     color: "#ffcc00" },
  "can":            { text: "🟡 Lata",          color: "#ffcc00" },
  "unknown":        { text: "⚫ Desconocido",   color: "#444444" },
};

document.addEventListener('DOMContentLoaded', () => {
  initSocketIO();
});

function initSocketIO() {
  socket.on('connect', () => {
    document.getElementById('status').textContent = 'Conectado';
    document.getElementById('error-container').style.display = 'none';
  });

  socket.on('disconnect', () => {
    document.getElementById('status').textContent = 'Desconectado';
    document.getElementById('error-container').style.display = 'block';
    document.getElementById('error-container').textContent =
      'Conexión perdida. Comprueba la placa.';
  });

  socket.on('frame', (data) => {
    const { image, label, confidence } = data;
    const info = LABEL_INFO[label] || LABEL_INFO["unknown"];

    // Imagen
    document.getElementById('cam').src = 'data:image/jpeg;base64,' + image;

    // Borde cámara
    document.getElementById('cam').style.borderColor = info.color;

    // Label
    document.getElementById('label-text').textContent =
      `${info.text}  (${confidence}%)`;
    document.getElementById('label-text').style.color = info.color;

    // Indicador LED
    const led = document.getElementById('led-indicator');
    led.style.background = info.color;
    led.style.boxShadow = label !== 'unknown'
      ? `0 0 24px 6px ${info.color}88`
      : 'none';

    // Status
    document.getElementById('status').textContent =
      `${label} — ${confidence}%`;
  });
}
