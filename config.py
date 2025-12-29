from pathlib import Path

# --- PATHS ---
BASE_DIR = Path(__file__).parent
URLS_FILE = BASE_DIR / "urls.txt"
OUTPUT_DIR = BASE_DIR / "NotebookLM_Sources"
LOG_FILE = BASE_DIR / "processed_urls.log"

# --- CRAWLER SETTINGS ---
MIN_YEAR = 2022  # Configurable: Ignore content older than this year
MAX_PAGES_PER_SITE = 50
MAX_CONCURRENT_PAGES = 1

# --- KEYWORDS & PATTERNS ---
KEYWORDS = [
    "/blog/", "/research/", "/engineering/", "/white-paper/",
    "/news/", "/post/", "/publications/", "/articles/"
]

NOISE_KEYWORDS = [
    "latest_news", "search_result", "label_", "page_", "tag_",
    "category_", "author_", "archive", "facebook", "twitter",
    "linkedin", "reddit", "signup", "login", "rss_xml",
    "javascript", "void_0", "uncategorized_misc", "newsletter"
]

SKIP_PATTERNS = [
     "twitter.com", "facebook.com", "linkedin.com", "reddit.com",
     "/share", "/intent/tweet", "/login", "/signup", ".xml", "/rss",
     "/label/", "/page/", "/category/", "/tag/", "/author/", "/archives/",
     "javascript:", "void(0)", "google.com/search", "google.com/url"
]

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
