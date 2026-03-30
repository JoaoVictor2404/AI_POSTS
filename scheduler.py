# scheduler.py
import os, yaml, pathlib
import os
import json
import threading
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

# importa suas tarefas
from main_mercury import main as mercury_main
from content_colector.api_connector_reddit import collect_reddit_posts
from post.post_to_x import post_to_x

CONFIG_NAME = os.getenv("CONFIG_FILE", "flash_crypto.yml")
CONFIG_PATH = pathlib.Path("configs") / CONFIG_NAME

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)


load_dotenv()

app = Flask(__name__)

# ------------------------
# Webhook endpoint Ghost
# ------------------------
@app.route('/ghost-webhook', methods=['POST'])
def ghost_webhook():
    data = request.get_json(force=True)
    
    # Ghost envia algo como {"post": {"current": { … }}, "previous": {...}}
    post_wrapper = data.get("post", {})
    post_info = post_wrapper.get("current") or post_wrapper.get("previous")
    
    # Pode ainda vir em data["current"] ou data["data"]["post"], mas esses caminhos não nos interessam aqui
    if not post_info:
        return jsonify({"message": "Payload sem campo post.current"}), 400

    title = post_info.get("title")
    post_url = post_info.get("url")

    if not title or not post_url:
        return jsonify({"message": "Faltando title ou url em post.current"}), 400

    message = f"🚀 Nova publicação no Flash Crypto Blog:\n\n{title}\n\nLeia mais: {post_url}"
    post_to_x(message)
    return jsonify({"message": "Tweet enviado com sucesso"}), 200


# ------------------------
# Configura e inicia o scheduler em background
# ------------------------
def start_scheduler():
    # 1️⃣ Coleta inicial assim que o serviço sobe
    print("Coletando tópicos do Reddit na inicialização…")
    collect_reddit_posts()
    scheduler = BackgroundScheduler()
    # job Mercury a cada 3 horas
    scheduler.add_job(mercury_main, 'interval', hours=CFG["mercury_frequency_hours"], id='mercury_job')
    # job Reddit a cada 24 horas
    scheduler.add_job(collect_reddit_posts, 'interval', hours=CFG["reddit_frequency_hours"], id='reddit_job')
    scheduler.start()
    print("Scheduler iniciado:")
    print("- Mercury postará a cada 3 horas.")
    print("- Coleta do Reddit ocorrerá a cada 24 horas.")

# ------------------------
# Rodando tudo junto
# ------------------------
if __name__ == "__main__":
    # inicia scheduler numa thread separada (opcional, mas garante que ele não bloqueie o Flask)
    threading.Thread(target=start_scheduler, daemon=True).start()

    # Levanta o Flask para receber o webhook
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
