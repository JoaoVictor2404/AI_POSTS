# AI_agents/mercury_agent.py
import re, os, json, random, pathlib, yaml
import google.generativeai as genai
from dotenv import load_dotenv

# ------------------------------------------------------------------
# 1. Carrega o arquivo de configuração escolhido via variável de amb.
# ------------------------------------------------------------------
CONFIG_NAME = os.getenv("CONFIG_FILE", "flash_crypto.yml")
CFG_PATH = pathlib.Path("configs") / CONFIG_NAME

with open(CFG_PATH, "r", encoding="utf-8") as fh:
    CFG = yaml.safe_load(fh)

PROMPT_TEMPLATE: str = CFG["prompt_template"]
#KEYWORDS = [k.lower() for k in CFG.get("reddit_keywords", [])] or ["crypto"]

# ------------------------------------------------------------------
def generate_mercury_post(reddit_file_path: str) -> dict:
    load_dotenv()

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=dict(
            temperature=0.7, top_p=0.95, top_k=40,
            max_output_tokens=8192, response_mime_type="text/plain"
        ),
    )

    # ---- Lê posts já baixados do Reddit --------------------------
    with open(reddit_file_path, encoding="utf-8") as fp:
        posts = json.load(fp)
    if not posts:
        raise RuntimeError("Arquivo JSON de tópicos está vazio.")

    # ---- Escolhe um post que contenha as palavras-chave ----------
    #filt = [p for p in posts if any(k in p["title"].lower() for k in KEYWORDS)]
    chosen = random.choice(posts)

    # ---- Preenche o template de prompt ---------------------------
    prompt = PROMPT_TEMPLATE.format(
        post_title=chosen["title"],
        post_body=chosen.get("selftext", ""),
        post_url=chosen.get("url", "")
    )

    # ---- Chama o Gemini -----------------------------------------
    chat = model.start_chat(history=[])
    resp = chat.send_message(prompt)
    txt  = resp.text.strip()
    txt  = re.sub(r"```(?:json)?", "", txt)  # remove code-fences
    try:
        out = json.loads(txt)
    except Exception:
        out = {"title": chosen["title"], "html": txt}

    # ---- Remove post usado p/ não repetir ------------------------
    with open(reddit_file_path, "w", encoding="utf-8") as fp:
        json.dump([p for p in posts if p != chosen], fp, ensure_ascii=False, indent=2)

    return out

# ------------------------------------------------------------------
if __name__ == "__main__":
    sample_json = "data/api_connector_reddit_content.json"
    print(json.dumps(generate_mercury_post(sample_json), indent=2, ensure_ascii=False))
