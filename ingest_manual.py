import asyncio
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from dateparser import parse
from playwright.async_api import async_playwright
import trafilatura

# --- CONFIGURATION (Identique au crawler auto) ---
OUTPUT_DIR = Path(r"G:\Mon Drive\NotebookLM\NotebookLM_Sources")

CATEGORIES = {
    "Generative AI": {
        "LLMs": ["llm", "large language model", "gpt", "gemini", "claude", "llama", "chatgpt", "bard", "mistral"],
        "RAG": ["rag", "retrieval augmented", "vector database", "embedding", "context window"],
        "Computer Vision": ["diffusion model", "image generation", "video generation", "midjourney", "dall-e", "stable diffusion"],
        "Audio": ["text-to-speech", "audio generation", "musicgen", "whisper"]
    },
    "Infrastructure": {
        "Hardware": ["gpu", "tpu", "h100", "accelerator", "nvidia", "cuda", "inference"],
        "MLOps": ["mlops", "pipeline", "serving", "deployment", "monitoring", "kubernetes", "docker"]
    },
    "Deep Learning": {
        "Theory": ["transformer", "attention mechanism", "loss function", "optimization", "backpropagation", "neural network"],
        "Reinforcement Learning": ["rlhf", "ppo", "q-learning", "agent", "reinforcement learning"]
    },
    "Agentic AI": {
        "Agents": ["autonomous agent", "agentic", "auto-gpt", "babyagi", "crewai", "langgraph", "autogen", "agent framework"],
        "Tools": ["tool use", "function calling", "mcp", "model context protocol"]
    },
    "Robotics": {
        "Physical AI": ["robotics", "humanoid", "optimus", "figure", "boston dynamics", "physical ai", "embodied ai", "manipulation"]
    },
    "General_AI_News": {
        "News": ["startup", "funding", "regulation", "policy", "ethics", "announcement"]
    }
}

from urllib.parse import urlparse

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# --- HELPERS (Duplicated for standalone usage) ---
def get_site_name(url):
    """Extracts a short, readable site name from the URL."""
    try:
        netloc = urlparse(url).netloc.lower().replace("www.", "")
        if "openai" in netloc: return "openai"
        if "google" in netloc: return "google_research"
        if "meta" in netloc: return "meta_ai"
        if "anthropic" in netloc: return "anthropic"
        if "nvidia" in netloc: return "nvidia"
        if "amazon" in netloc or "aws" in netloc: return "aws"
        if "huggingface" in netloc: return "huggingface"
        return netloc.split('.')[0]
    except:
        return "web"

def slugify(text):
    if not text: return "sans_titre"
    return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')

def normalize_date(raw_date):
    if not raw_date: return None
    try:
        parsed = parse(str(raw_date))
        return parsed.strftime("%Y-%m-%d") if parsed else None
    except: return None

def classify_content(content):
    content_lower = content.lower()
    scores = {}
    for cat, subcats in CATEGORIES.items():
        for subcat, keywords in subcats.items():
            count = sum(content_lower.count(k) for k in keywords)
            if count > 0: scores[(cat, subcat)] = count
    
    if not scores: return "Uncategorized", "Misc"
    return max(scores, key=scores.get)

# --- CORE LOGIC ---
async def process_single_url(url):
    logger.info(f"🎯 Sniper activé sur : {url}")
    
    async with async_playwright() as p:
        # Launch stealth browser
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            # Resource Blocking
            await page.route("**/*", lambda route: route.abort() 
                if route.request.resource_type in ["image", "media", "font", "stylesheet"] 
                else route.continue_())

            logger.info("⏳ Chargement de la page...")
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await asyncio.sleep(2) # Wait for hydration

            # Scroll once just in case
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)

            html_content = await page.content()
            
            # Extraction
            extracted = trafilatura.extract(html_content, output_format="markdown", include_tables=True)
            metadata = trafilatura.extract_metadata(html_content)

            if not extracted:
                logger.error("❌ Échec : Impossible d'extraire du contenu texte pertinent.")
                return

            date_iso = normalize_date(metadata.date if metadata else None)
            if not date_iso:
                 # Try URL date pattern
                 match = re.search(r'/(\d{4})/', url)
                 if match: date_iso = f"{match.group(1)}-01-01"

            # Classification
            category, subcategory = classify_content(extracted)
            title = slugify(metadata.title if metadata and metadata.title else url.split("/")[-1])
            site_name = get_site_name(url)

            # Save Logic
            if date_iso:
                year = date_iso.split('-')[0]
                filename = f"{date_iso}_{site_name}_{title}.md"
                save_dir = OUTPUT_DIR / category / subcategory / year
            else:
                filename = f"Undated_{site_name}_{title}.md"
                save_dir = OUTPUT_DIR / category / subcategory / "Undated"

            save_dir.mkdir(parents=True, exist_ok=True)
            filepath = save_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"--- SOURCE INFO ---\nURL: {url}\nDATE: {date_iso or 'Unknown'}\nCATEGORY: {category}/{subcategory}\n---\n\n{extracted}")

            logger.info(f"✅ SUCCÈS : Fichier créé !")
            logger.info(f"📂 Chemin : {filepath}")

        except Exception as e:
            logger.error(f"❌ Erreur critique : {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = input("🔗 Entrez l'URL à aspirer : ").strip()
    
    if target_url:
        asyncio.run(process_single_url(target_url))
