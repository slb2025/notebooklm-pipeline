import asyncio
import logging
import random
import re
from pathlib import Path
from playwright.async_api import async_playwright
import trafilatura

# Import from our new modules
from config import (
    URLS_FILE, OUTPUT_DIR, MIN_YEAR, MAX_PAGES_PER_SITE,
    MAX_CONCURRENT_PAGES, KEYWORDS, SKIP_PATTERNS
)
from utils import (
    setup_logging, get_site_name, slugify, normalize_date,
    classify_content, load_processed_urls, save_processed_url,
    scan_existing_files
)

# --- LOGGING ---
logger = setup_logging("crawler")

async def process_site(page, base_url, processed_urls):
    logger.info(f"🕸️ Connecting to: {base_url}")
    try:
        # Route blocking for performance (Images, Fonts, CSS)
        await page.route("**/*", lambda route: route.abort() 
            if route.request.resource_type in ["image", "media", "font", "stylesheet"] 
            else route.continue_())

        await page.goto(base_url, timeout=60000, wait_until="domcontentloaded")
        await asyncio.sleep(3) 

        # Deep Scroll: Aggressively trigger infinite scroll
        previous_height = 0
        for _ in range(10): # Try scrolling 10 times
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.5)
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == previous_height:
                break # Stop if no new content loaded
            previous_height = new_height

        # Get all links
        links = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a')).map(a => a.href)
        """)
        
        candidates = set()

        for link in links:
            if not link.startswith("http"): continue
            
            # 1. Skip if matches exclusion patterns
            if any(p in link.lower() for p in SKIP_PATTERNS):
                continue
            
            # 2. Skip "Year Archive" pages (e.g. /blog/2023 without article slug)
            if re.search(r'/\d{4}/?$', link):
                continue
            
            # 3. Skip Main Index Page (Base URL)
            if link.rstrip("/") == base_url.rstrip("/"):
                continue

            if (base_url in link or any(k in link for k in KEYWORDS)) and link not in processed_urls:
                 candidates.add(link)

        logger.info(f"🔎 Found {len(candidates)} potential links on {base_url}")
        
        count = 0
        for link in candidates:
            if count >= MAX_PAGES_PER_SITE: break
            if link in processed_urls: continue

            await asyncio.sleep(random.uniform(1.5, 3)) # Slightly faster due to resource blocking
            
            try:
                await page.goto(link, timeout=30000, wait_until="domcontentloaded")
                html_content = await page.content()
                
                extracted = trafilatura.extract(html_content, output_format="markdown", include_tables=True)
                metadata = trafilatura.extract_metadata(html_content)
                
                if not extracted or len(extracted) < 500:
                    save_processed_url(link)
                    processed_urls.add(link)
                    continue

                date_iso = normalize_date(metadata.date if metadata else None)
                if not date_iso:
                    match = re.search(r'/(\d{4})/', link)
                    if match: date_iso = f"{match.group(1)}-01-01"

                # STRICT DATE CHECK
                year_of_article = 0
                if date_iso:
                    year_of_article = int(date_iso.split('-')[0])
                    if year_of_article < MIN_YEAR:
                        logger.info(f"🕰️ Skipped (Too old: {year_of_article}): {link}")
                        save_processed_url(link)
                        processed_urls.add(link)
                        continue
                
                category, subcategory = classify_content(extracted)
                title = slugify(metadata.title if metadata and metadata.title else link.split("/")[-1])
                
                # Title Safety Net (Avoid Index Pages that slipped through URL filters)
                if any(x in title for x in ["latest_news", "search_result", "index_of"]):
                    logger.info(f"🗑️ Skipped (Title Noise): {title}")
                    save_processed_url(link)
                    processed_urls.add(link)
                    continue

                site_name = get_site_name(link)
                if date_iso:
                    filename = f"{date_iso}_{site_name}_{title}.md"
                    save_dir = OUTPUT_DIR / category / subcategory / str(year_of_article)
                else:
                    filename = f"Undated_{site_name}_{title}.md"
                    save_dir = OUTPUT_DIR / category / subcategory / "Undated"

                save_dir.mkdir(parents=True, exist_ok=True)
                filepath = save_dir / filename
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"--- SOURCE INFO ---\nURL: {link}\nDATE: {date_iso or 'Unknown'}\nCATEGORY: {category}/{subcategory}\n---\n\n{extracted}")
                
                logger.info(f"✅ Saved [{category}/{subcategory}]: {filename}")
                save_processed_url(link)
                processed_urls.add(link)
                count += 1
                
            except Exception as e:
                logger.error(f"Failed to process {link}: {e}")

    except Exception as e:
        logger.error(f"Error crawling site {base_url}: {e}")

async def run_crawler():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    processed_urls = load_processed_urls()
    processed_urls.update(scan_existing_files(OUTPUT_DIR))
    
    if not URLS_FILE.exists():
        logger.error("urls.txt not found")
        return

    with open(URLS_FILE, "r") as f:
        urls = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    async with async_playwright() as p:
        # Launch options for STEALTH configuration
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"] # Mask automation
        )
        
        # User Agent & Viewport
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1
        )
        
        # Anti-detection script injection
        page = await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        for base_url in urls:
            await process_site(page, base_url, processed_urls)
            logger.info("💤 Cooling down between sites...")
            await asyncio.sleep(5)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_crawler())
