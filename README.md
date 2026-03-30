## 📑 Automação de Conteúdo

A **Automação de Conteúdo** é um orquestrador completo para:

1. **Garimpar tópicos** em subreddits voltados a cripto;
2. **Gerar** notícias, imagens e títulos com a API Gemini;
3. **Revisar** o texto antes da publicação;
4. **Publicar** no blog Ghost (com upload de imagem) e,
5. **Divulgar** automaticamente o artigo na rede X (Twitter);
6. **Responder** a webhooks do Ghost quando posts forem publicados manualmente.

A aplicação foi desenhada para ser **multi-instância**.
Toda a lógica “o que fazer” fica nos *configs* (YAML) e nas variáveis de ambiente; o código não precisa mudar quando você clona o repositório para outros blogs/agentes.

---

### 🗂 Estrutura geral de diretórios

```
automacao-de-conteudo/
│
├── AI_agents/               # Agentes Gemini (escrita)
│   ├── mercury_agent.py     # Gera notícia + HTML a partir do Reddit
│
├── review_agent/
│   └── review_mercury.py    # Revisa/otimiza o HTML
│
├── creta_image/
│   └── mercury_image.py     # Gera imagem com Gemini e salva localmente
│
├── content_colector/
│   └── api_connector_reddit.py  # Faz scraping do Reddit e salva JSON
│
├── post/
│   ├── post_blog.py         # JWT, upload de imagem e criação de post no Ghost
│   └── post_to_x.py         # Publica tweet no X/Twitter
│
├── configs/                 # Um YAML por “instância/agente/blog”
│   ├── flash_crypto.yml     # Prompt, tags, frequências…
│   └── outro_blog.yml       # (exemplo)
│
├── scheduler.py             # Flask + APScheduler + Webhook Ghost
├── main_mercury.py          # Encadeia: gerar → revisar → imagem → Ghost
│
├── requirements.txt         # Dependências Python
├── Dockerfile               # Imagem para Railway/containers
└── .dockerignore
```

> **Config first**
> • Chaves das APIs, domínios e flags ficam em variáveis de ambiente.
> • Prompts, tags, frequência das tarefas e filtros de subreddit ficam nos YAMLs.

---

### 🔄 Fluxo completo

1. **Scheduler (Flask + APScheduler)** sobe → coleta Reddit logo na inicialização.
2. A cada `mercury_frequency_hours`
   • Escolhe um post do JSON
   • `mercury_agent` gera `{title, html}`
   • `review_mercury` refina o HTML
   • `mercury_image` cria PNG/JPG baseado no título
   • `post_blog.upload_feature_image` envia a imagem → obtém URL
   • `post_blog.create_blog_post` grava rascunho (ou publicado) no Ghost
3. **Webhook**: quando o Ghost publica algo (manual ou agendado) → `/ghost-webhook` → `post_to_x` solta um tweet com título + link.
4. **Coleta Reddit** roda isolada a cada `reddit_frequency_hours` para abastecer o JSON.

## Detalhamento de Arquivos

### 1. `AI_agents/`

| Arquivo                | Função                                                                                                                                                                                                                                                                                                                      |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`mercury_agent.py`** | - Carrega `configs/<instância>.yml` (“prompt\_template”, palavras-chave, etc.).<br>- Lê o JSON de tópicos do Reddit.<br>- Monta o prompt a partir do template + título/corpo/URL do post.<br>- Chama Gemini “gemini-2.0-flash” e devolve um **JSON**:<br>`{"title": "...", "html": "…"}`.<br>- Remove o post usado do JSON. |

### 2. `review_agent/`

| Arquivo                 | Função                                                                                                    |
| ----------------------- | --------------------------------------------------------------------------------------------------------- |
| **`review_mercury.py`** | Recebe o HTML, pede ao Gemini correção gramatical, clareza, SEO. Retorna HTML revisado (sem comentários). |

### 3. `creta_image/`

| Arquivo                | Função                                                                                                                                           |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`mercury_image.py`** | Gera uma imagem (PNG/JPEG) via modelo *gemini-2.0-flash-exp-image-generation* usando o título como prompt. Salva localmente e devolve o caminho. |

### 4. `content_colector/`

| Arquivo                       | Função                                                                                                                                        |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **`api_connector_reddit.py`** | Autentica via **PRAW**, coleta `hot(limit=50)` dos subreddits listados, filtra/serializa e grava em `data/api_connector_reddit_content.json`. |

### 5. `post/`

| Arquivo            | Função                                                                                                                                                                                                                            |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`post_blog.py`** | 1️⃣ `generate_jwt` cria token Ghost Admin.<br>2️⃣ `upload_feature_image` faz *multipart upload* → retorna URL da imagem.<br>3️⃣ `create_blog_post` monta `post_data` (tags, status do YAML) e envia à rota `/posts/?source=html`. |
| **`post_to_x.py`** | Faz POST na API v2 do Twitter (X) com OAuth 1.0a.                                                                                                                                                                                 |

### 6. Arquivos de orquestração

| Arquivo               | Função                                                                                                                                                                                                                                                        |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`main_mercury.py`** | Pipeline completo:<br>• Gera conteúdo → revisa HTML → gera imagem → upload → cria post no Ghost.                                                                                                                                                              |
| **`scheduler.py`**    | • `Flask` recebe **`/ghost-webhook`** (evento *post.published*).<br>• `BackgroundScheduler` agenda:<br> - `mercury_main` (intervalo do YAML).<br> - `collect_reddit_posts` (intervalo do YAML).<br>• Executa uma coleta Reddit **imediata** na inicialização. |

### 7. `configs/`

Cada YAML define **uma instância**:

```yaml
agent_name: mercury
prompt_template: | 
  Você é o Mercury…
  Título-origem: {post_title}
  Corpo-origem: {post_body}
  URL-origem: {post_url}
  Gere JSON…
ghost_tags:       ["News","Crypto"]
publish_status:   draft           # ou published
reddit_keywords:  ["crypto","bitcoin"]
mercury_frequency_hours: 3
reddit_frequency_hours: 24
```

Altere apenas esse arquivo para mudar prompt, tags ou cadência.
Selecione o YAML desejado com a variável `CONFIG_FILE`.

---

### 8. Variáveis de Ambiente (Railway / .env)

| Nome                                                                                | Descrição                          |
| ----------------------------------------------------------------------------------- | ---------------------------------- |
| `CONFIG_FILE`                                                                       | Ex.: `flash_crypto.yml`            |
| `GEMINI_API_KEY`                                                                    | Chave Google Generative AI         |
| `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` / `REDDIT_USERNAME` / `REDDIT_PASSWORD` |                                    |
| `GHOST_SECRET`, `GHOST_KEY_ID`                                                      | Chave Admin Integrations           |
| `GHOST_DOMAIN`                                                                      | Domínio (ex.: `airdrop.ghost.io`)  |
| `GHOST_SCHEME`                                                                      | `https` ou `http` (se TLS ausente) |
| `GHOST_VERIFY_TLS`                                                                  | `true` / `false` (upload imagem)   |
| `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`              |                                    |
| `PORT`                                                                              | Definido pelo Railway              |

---

### 9. Docker & Deploy

**Dockerfile** (resumido):

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "scheduler.py"]
```

1. `docker build -t automacao .`
2. `docker run -e CONFIG_FILE=flash_crypto.yml … -p 5000:5000 automacao`

No Railway:

* Apontar “Start Command” para `python scheduler.py`.
* Definir todas as variáveis de ambiente.
* O container sobe, coleta Reddit uma vez, agenda jobs, expõe `/ghost-webhook`.

---

### 🔧 Como criar **nova instância** (outro blog / prompt)

1. Copie `configs/flash_crypto.yml` para `configs/meu_blog.yml`; altere prompt, tags e frequências.
2. No Railway clone o projeto ou crie novo ambiente.
3. Defina `CONFIG_FILE=meu_blog.yml` + novas chaves (Ghost, X).
4. Deploy — nenhum código muda.

Com essa arquitetura **config-first**, o projeto “Automação de Conteúdo” escala para quantos blogs e agentes você precisar apenas com YAML + variáveis de ambiente.
