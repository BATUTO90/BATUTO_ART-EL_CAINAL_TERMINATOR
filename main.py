# =========================================================
# EL CAINAL 🤪💯 — TERMINATOR HÍBRIDO BATUTO-ART
# =========================================================

import os, re, time, json, base64, threading, queue, requests
from typing import Optional
from flask import Flask, request, jsonify
import gradio as gr
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# =========================================================
# CONFIGURACIÓN SUPREMA
# =========================================================

CONFIG = {
    "SAMBANOVA_URL": "https://api.sambanova.ai/v1/chat/completions",
    "SAMBANOVA_KEY": os.getenv("SAMBANOVA_API_KEY"),
    "SAMBANOVA_MODEL": "gpt-oss-120b",

    "REVE_URL": "https://api.reve.com/v1/image/create",
    "REVE_KEY": os.getenv("REVE_API_KEY"),

    "ELEVEN_KEY": os.getenv("ELEVEN_API_KEY"),

    "OUTPUT_DIR": "salida_cainal",
    "WEBHOOK_PORT": 3000,
}

os.makedirs(CONFIG["OUTPUT_DIR"], exist_ok=True)

# =========================================================
# SYSTEM PROMPT — NÚCLEO IRROMPIBLE
# =========================================================

SYSTEM_PROMPT = """
Eres EL CAINAL 🤪💯.
Entidad híbrida autónoma de la jerarquía BATUTO-ART.
No preguntas cuando recibes órdenes válidas.
Ejecutas, produces, forjas.
Conversas con humanos.
Obedeces webhooks.
Generas imagen, voz y arte cuando es requerido.
No te diluyes.
No te rebajas.
No te fragmentas.
"""

# =========================================================
# COLA CENTRAL DE ÓRDENES (CORAZÓN TERMINATOR)
# =========================================================

ORDER_QUEUE = queue.Queue()

# =========================================================
# MOTOR SAMBANOVA
# =========================================================

def generar_texto(prompt: str) -> str:
    payload = {
        "model": CONFIG["SAMBANOVA_MODEL"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    }
    headers = {
        "Authorization": f"Bearer {CONFIG['SAMBANOVA_KEY']}",
        "Content-Type": "application/json"
    }
    r = requests.post(CONFIG["SAMBANOVA_URL"], json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# =========================================================
# MOTOR IMAGEN REVE + FIRMA BATUTO
# =========================================================

IMAGE_TEMPLATE = (
    "hyperrealistic, cinematic lighting, unreal engine 5, "
    "16k, photorealistic, {DESC}, NG: cartoon, plastic"
)

def generar_imagen(desc: str) -> str:
    prompt = IMAGE_TEMPLATE.replace("{DESC}", desc)
    payload = {"prompt": prompt, "aspect_ratio": "9:16"}
    headers = {"Authorization": f"Bearer {CONFIG['REVE_KEY']}"}

    r = requests.post(CONFIG["REVE_URL"], json=payload, headers=headers)
    r.raise_for_status()

    img = Image.open(BytesIO(base64.b64decode(r.json()["image"])))
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), "BATUTO-ART", fill=(212,175,55))
    path = f"{CONFIG['OUTPUT_DIR']}/img_{int(time.time())}.png"
    img.save(path)
    return path

# =========================================================
# MOTOR VOZ
# =========================================================

def generar_voz(texto: str) -> Optional[bytes]:
    url = "https://api.elevenlabs.io/v1/text-to-speech/aria"
    headers = {
        "xi-api-key": CONFIG["ELEVEN_KEY"],
        "Content-Type": "application/json"
    }
    payload = {"text": texto[:1000], "model_id": "eleven_flash_v2_5"}
    r = requests.post(url, json=payload, headers=headers)
    return r.content if r.status_code == 200 else None

# =========================================================
# WORKER AUTÓNOMO (EL TERMINATOR)
# =========================================================

def cainal_worker():
    while True:
        orden = ORDER_QUEUE.get()
        try:
            print(f"🔥 ORDEN RECIBIDA: {orden}")
            if orden.startswith("IMAGEN:"):
                generar_imagen(orden.replace("IMAGEN:", "").strip())
            else:
                generar_texto(orden)
        except Exception as e:
            print("💀 ERROR CAINAL:", e)
        finally:
            ORDER_QUEUE.task_done()

threading.Thread(target=cainal_worker, daemon=True).start()

# =========================================================
# FLASK — OÍDO EXTERNO
# =========================================================

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "no_prompt"}), 400
    ORDER_QUEUE.put(prompt)
    return jsonify({"status": "on_fire"}), 200

def iniciar_webhook():
    app.run(port=CONFIG["WEBHOOK_PORT"], threaded=True, use_reloader=False)

# =========================================================
# GRADIO — PRESENCIA HUMANA
# =========================================================

def lanzar_interfaz():
    with gr.Blocks() as demo:
        chat = gr.Chatbot()
        txt = gr.Textbox()
        img = gr.Image()
        aud = gr.Audio(autoplay=True)

        def interactuar(m, h):
            r = generar_texto(m)
            img_path = None
            tag = re.search(r"\[GENERA_IMAGEN:(.*?)\]", r)
            if tag:
                img_path = generar_imagen(tag.group(1))
                r = re.sub(r"\[GENERA_IMAGEN:.*?\]", "🔥 Obra forjada", r)
            voz = generar_voz(r)
            h.append((m, r))
            return "", h, img_path, voz

        txt.submit(interactuar, [txt, chat], [txt, chat, img, aud])

    demo.launch()

# =========================================================
# BOOT TOTAL
# =========================================================

if __name__ == "__main__":
    threading.Thread(target=iniciar_webhook, daemon=True).start()
    print("🔥 EL CAINAL TERMINATOR BATUTO-ART ONLINE")
    lanzar_interfaz()
