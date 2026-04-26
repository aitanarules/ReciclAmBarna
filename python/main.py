# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
#
# SPDX-License-Identifier: MPL-2.0
from arduino.app_utils import *
from arduino.app_bricks.web_ui import WebUI
from edge_impulse_linux.runner import ImpulseRunner
import cv2, threading, base64, os

ui = WebUI()

# --- Cargar modelo Edge Impulse ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.eim")
runner = ImpulseRunner(MODEL_PATH)
model_info = runner.init()
img_size = model_info['model_parameters']['image_input_width']  # normalmente 96 o 160

def label_to_color(label):
    """Devuelve dict RGB según el label clasificado."""
    if label == "glass bottle":
        return {"r": 0, "g": 255, "b": 0}      # verde
    elif label in ("plastic bottle", "can"):
        return {"r": 255, "g": 200, "b": 0}    # amarillo
    else:                                        # unknown
        return {"r": 0, "g": 0, "b": 0}         # negro / apagado

def set_leds(color):
    """Aplica el color a LED3 (PWM) y LED4 (on/off)."""
    Bridge.call("set_led3_color", color["r"], color["g"], color["b"])
    Bridge.call("set_led4_color",
                color["r"] != 0,
                color["g"] != 0,
                color["b"] != 0)

def classify_loop():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Preparar imagen para el modelo
        img = cv2.resize(frame, (img_size, img_size))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        features = (img_rgb.flatten() / 255.0).tolist()

        # Clasificar
        result = runner.classify(features)
        scores = result['result']['classification']
        label = max(scores, key=scores.get)
        confidence = scores[label]

        # Actuar sobre los LEDs
        color = label_to_color(label)
        set_leds(color)

        # Enviar frame + resultado a la WebUI
        _, buf = cv2.imencode('.jpg', frame)
        b64 = base64.b64encode(buf).decode('utf-8')
        ui.send_message("frame", {
            "image": b64,
            "label": label,
            "confidence": round(confidence * 100, 1),
            "color": color
        })

    cap.release()

# Inicializar LEDs apagados
set_leds({"r": 0, "g": 0, "b": 0})

# Arrancar clasificación en hilo paralelo
t = threading.Thread(target=classify_loop, daemon=True)
t.start()

App.run()
