# AI Content Automation System

A complete AI-powered content automation system designed to collect trending topics, generate articles, review quality, create images, publish content to Ghost, and automatically share published posts on X (Twitter).

The application was built with a config-first architecture, allowing multiple blog or agent instances to run from YAML configuration files and environment variables, without changing the core codebase.

---

## Overview

This project automates the full content pipeline:

1. Collect trending topics from crypto-focused subreddits
2. Generate article titles, content, and images using Gemini
3. Review and improve the generated HTML before publishing
4. Publish content to Ghost with image upload support
5. Automatically share published posts on X (Twitter)
6. Handle Ghost webhooks for manually published posts

---

## Key Features

- Automated Reddit topic collection
- AI-powered article generation with Gemini
- HTML review and content refinement
- AI-based image generation for posts
- Ghost CMS publishing with image upload
- Automatic posting to X (Twitter)
- Ghost webhook handling
- Multi-instance architecture using YAML configs
- Docker-ready deployment
- Railway-friendly environment setup

---

## Project Structure

```bash
automacao-de-conteudo/
│
├── AI_agents/                    # Gemini writing agents
│   └── mercury_agent.py          # Generates article title and HTML from Reddit content
│
├── review_agent/
│   └── review_mercury.py         # Reviews and improves generated HTML
│
├── creta_image/
│   └── mercury_image.py          # Generates images with Gemini and saves locally
│
├── content_colector/
│   └── api_connector_reddit.py   # Collects Reddit posts and stores them as JSON
│
├── post/
│   ├── post_blog.py              # Ghost JWT, image upload, and post creation
│   └── post_to_x.py              # Posts content to X (Twitter)
│
├── configs/                      # One YAML file per instance / blog / agent
│   ├── flash_crypto.yml
│   └── another_blog.yml
│
├── scheduler.py                  # Flask + APScheduler + Ghost webhook handling
├── main_mercury.py               # Full pipeline: generate -> review -> image -> publish
│
├── requirements.txt
├── Dockerfile
└── .dockerignore
```

---

## Full Workflow

1. The scheduler starts with Flask and APScheduler, and immediately performs an initial Reddit collection
2. Every `mercury_frequency_hours`:
   - Selects one post from the stored JSON
   - Uses `mercury_agent` to generate `{title, html}`
   - Uses `review_mercury` to improve the generated HTML
   - Uses `mercury_image` to generate a PNG or JPG image from the title
   - Uploads the image to Ghost
   - Creates a draft or published post in Ghost
3. When Ghost publishes a post manually or automatically, `/ghost-webhook` triggers `post_to_x`
4. Reddit collection runs independently every `reddit_frequency_hours` to keep the topic source updated

---

## Module Details

### AI Agents
- `mercury_agent.py`
  - Loads the selected YAML config from `configs/<instance>.yml`
  - Reads stored Reddit topics from JSON
  - Builds the generation prompt using the configured template
  - Calls Gemini and returns a JSON response with `title` and `html`
  - Removes the used topic from the JSON source

### Review Agent
- `review_mercury.py`
  - Receives the generated HTML
  - Uses Gemini to improve grammar, clarity, and SEO quality
  - Returns the revised HTML without commentary

### Image Generation
- `mercury_image.py`
  - Generates an image using Gemini image generation
  - Saves the file locally and returns the generated path

### Content Collector
- `api_connector_reddit.py`
  - Authenticates with Reddit using PRAW
  - Collects `hot(limit=50)` posts from configured subreddits
  - Filters, serializes, and stores the data in JSON format

### Publishing Modules
- `post_blog.py`
  - Generates Ghost Admin JWT
  - Uploads feature images to Ghost
  - Creates blog posts using the Ghost Admin API
- `post_to_x.py`
  - Publishes tweets using the X API v2 with OAuth 1.0a

### Orchestration
- `main_mercury.py`
  - Executes the full pipeline from content generation to publication
- `scheduler.py`
  - Runs Flask with `/ghost-webhook`
  - Schedules content generation and Reddit collection jobs
  - Executes an immediate Reddit collection when the app starts

---

## Configuration

Each YAML file inside `configs/` defines one instance of the system.

Example:

```yaml
agent_name: mercury
prompt_template: |
  You are Mercury...
  Source title: {post_title}
  Source body: {post_body}
  Source URL: {post_url}
  Return valid JSON...
ghost_tags: ["News", "Crypto"]
publish_status: draft
reddit_keywords: ["crypto", "bitcoin"]
mercury_frequency_hours: 3
reddit_frequency_hours: 24
```

With this setup, you can create new blog or automation instances by changing only the YAML configuration and environment variables.

---

## Environment Variables

Required environment variables for local development, Docker, or Railway deployment:

- `CONFIG_FILE` — example: `flash_crypto.yml`
- `GEMINI_API_KEY`
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USERNAME`
- `REDDIT_PASSWORD`
- `GHOST_SECRET`
- `GHOST_KEY_ID`
- `GHOST_DOMAIN`
- `GHOST_SCHEME`
- `GHOST_VERIFY_TLS`
- `X_API_KEY`
- `X_API_SECRET`
- `X_ACCESS_TOKEN`
- `X_ACCESS_TOKEN_SECRET`
- `PORT`

---

## Docker

### Build the image

```bash
docker build -t ai-content-automation .
```

### Run the container

```bash
docker run -e CONFIG_FILE=flash_crypto.yml -p 5000:5000 ai-content-automation
```

For Railway deployment:
- Set the start command to `python scheduler.py`
- Configure all required environment variables
- Expose the webhook endpoint `/ghost-webhook`

---

## Creating a New Instance

1. Copy `configs/flash_crypto.yml` to a new file such as `configs/my_blog.yml`
2. Update prompts, tags, keywords, and schedule values
3. Create a new Railway environment or deployment
4. Set `CONFIG_FILE=my_blog.yml`
5. Add the new Ghost and X credentials
6. Deploy without changing the application code

---

## Use Cases

- Automated crypto news generation
- AI-assisted editorial workflows
- Multi-blog content automation
- Ghost CMS publishing pipelines
- Automated social media distribution
- Scalable AI content operations

---

## Author

Developed by João Victor da Silva Souza

---

## License

This project is available for study, adaptation, and extension.
