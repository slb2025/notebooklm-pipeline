import re
import logging
from urllib.parse import urlparse
from dateparser import parse
from config import CATEGORIES, LOG_FILE

# --- LOGGING SETUP ---
def setup_logging(name, log_file="crawler.log"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create handlers
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    stream_handler = logging.StreamHandler()
    
    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    # Avoid adding handlers multiple times if setup is called repeatedly
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        
    return logger

logger = setup_logging(__name__)

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

def load_processed_urls():
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()

def save_processed_url(url):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(url + "\n")
    except Exception as e:
        logger.error(f"Error saving URL {url}: {e}")

def scan_existing_files(output_dir):
    existing = set()
    if not output_dir.exists(): return existing
    logger.info("📂 Scanning existing files...")
    for file_path in output_dir.rglob("*.md"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for _ in range(10):
                    line = f.readline()
                    if line.startswith("URL:"):
                        existing.add(line.split("URL:", 1)[1].strip())
                        break
        except: pass
    logger.info(f"✅ {len(existing)} URLs found in Drive.")
    return existing
