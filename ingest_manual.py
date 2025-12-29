import asyncio
import logging
import re
import sys
import trafilatura
from playwright.async_api import async_playwright

# Import from our new modules
from config import OUTPUT_DIR
from utils import (
    setup_logging, get_site_name, slugify, normalize_date, 
    classify_content
)

# --- LOGGING ---
logger = setup_logging("manual_ingest")

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
