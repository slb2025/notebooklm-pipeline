import os
from config import OUTPUT_DIR, NOISE_KEYWORDS
from utils import setup_logging

# --- LOGGING ---
logger = setup_logging("clean_noise")

def is_noise(file_path):
    """Détermine si un fichier est du bruit basé sur son nom ou son contenu."""
    filename = file_path.name.lower()
    
    # 1. Check filename patterns
    if any(k in filename for k in NOISE_KEYWORDS):
        return True, f"Nom suspect ({next(k for k in NOISE_KEYWORDS if k in filename)})"

    # 2. Check content (URL headers)
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for _ in range(10):
                line = f.readline()
                if line.startswith("URL:"):
                    url = line.split("URL:", 1)[1].strip().lower()
                    if any(k in url for k in ["/label/", "/tag/", "/category/", "/page/", "share="]):
                        return True, "URL d'index/pagination"
                    break
    except:
        pass

    return False, None

def clean_noise():
    if not OUTPUT_DIR.exists():
        logger.error(f"❌ Dossier introuvable : {OUTPUT_DIR}")
        return

    logger.info(f"🔍 Analyse en cours dans : {OUTPUT_DIR}...")
    
    noisy_files = []
    scanned_count = 0

    # 1. Identification (Identify all candidates first)
    for file_path in OUTPUT_DIR.rglob("*.md"):
        scanned_count += 1
        is_noisy, reason = is_noise(file_path)
        if is_noisy:
            noisy_files.append((file_path, reason))

    total_noise = len(noisy_files)
    logger.info(f"📂 Fichiers scannés : {scanned_count}")
    logger.info(f"⚠️ Fichiers identifiés comme 'bruit' : {total_noise}")

    if total_noise == 0:
        logger.info("✨ Aucun fichier à nettoyer. Tout est propre !")
        return

    # 2. Validation & Deletion Logic
    deleted_count = 0
    
    if total_noise < 30:
        logger.info("\n Validation un par un (< 30 fichiers) :")
        for file_path, reason in noisy_files:
            print(f"\n📄 {file_path.name}")
            print(f"   ↳ Raison : {reason}")
            choice = input("   ❌ Supprimer ? (y/n) : ").lower()
            if choice == 'y':
                try:
                    os.remove(file_path)
                    print(f"   🗑️ Supprimé.")
                    deleted_count += 1
                except Exception as e:
                    print(f"   ⚠️ Erreur : {e}")
            else:
                print("   conservé.")
    else:
        logger.info("\n Validation par paquets de 5 (>= 30 fichiers) :")
        # Process in chunks of 5
        for i in range(0, len(noisy_files), 5):
            batch = noisy_files[i:i+5]
            print(f"\n--- Lot {i+1} à {min(i+5, len(noisy_files))} sur {total_noise} ---")
            for fp, reason in batch:
                print(f"  • {fp.name} ({reason})")
            
            choice = input("❌ Supprimer ce lot ? (y/n) : ").lower()
            if choice == 'y':
                for file_path, _ in batch:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except Exception as e:
                        print(f"   ⚠️ Erreur sur {file_path.name} : {e}")
                print("   🗑️ Lot supprimé.")
            else:
                print("   Lot conservé.")

    logger.info("-" * 30)
    logger.info(f"✨ Nettoyage terminé.")
    logger.info(f"🗑️ Total supprimés : {deleted_count} / {total_noise}")

if __name__ == "__main__":
    clean_noise()
