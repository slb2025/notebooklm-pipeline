# 🧠 AI Knowledge Pipeline for NotebookLM

Ce projet est un pipeline d'ingestion avancé conçu pour construire une base de connaissance IA de haute qualité ("Curated Dataset") optimisée pour **NotebookLM**.

Il transforme le web chaotique (Blogs Tech, News, Papiers de recherche) en une base de données Markdown structurée, propre et triée.

## ✨ Fonctionnalités Clés

*   **🕵️‍♂️ Crawler "Stealth" & Robuste** : 
    *   **Playwright** : Utilise un vrai navigateur pour contourner les protections anti-bot (OpenAI, Google) et charger les contenus dynamiques (React, Infinite Scroll).
    *   **Anti-Bruit Natif** : Bloque automatiquement les URLs parasites (réseaux sociaux, pages d'index, archives annuelles) *avant* le téléchargement.
    *   **File Safety Net** : Vérifie les titres pour éviter de sauvegarder des pages "Latest News" ou "Search Results".
*   **🧠 Classification Intelligente** : Analyse le contenu pour trier automatiquement les articles :
    *   `Generative AI` (LLMs, RAG...)
    *   `Deep Learning` (Theory, RLHF...)
    *   `Agentic AI` (Agents, Tools, MCP...)
    *   `Robotics` (Physical AI, Humanoid...)
    *   `Infrastructure` (Hardware, MLOps...)
*   **📂 Organisation Temporelle & Nommage** : 
    *   Structure : `Categorie/Sous-Categorie/Année/`
    *   Fichiers : `YYYY-MM-DD_sitename_titre_article.md` (Ex: `2024-03-22_google_research_why_agents_matter.md`).
*   **🛡️ Qualité des Données** :
    *   Filtre strict : Ignore tout contenu antérieur à **2023** (configurable).
    *   Nettoyage : Suppression des pubs, menus et scripts via `trafilatura`.
    *   Doublons : Scan intelligent de votre répertoire local pour ne jamais télécharger deux fois le même article.

## 🛠 Architecture du Pipeline

1.  **Input** : Liste de sites dans `urls.txt` (Google, OpenAI, Anthropic, Meta, Nvidia, etc.).
2.  **Extract (Playwright)** : Navigation "humaine", scroll infini, blocage des ressources lourdes (Images/Fonts) pour la performance.
3.  **Filter & Transform** : 
    *   Filtrage des URLs "bruit" (Twitter, Facebook, Index pages).
    *   Classification par mots-clés.
    *   Génération de nom de fichier canonique (Date + Site + Titre).
4.  **Load** : Sauvegarde dans Google Drive avec une arborescence triée par année.

## 🚀 Installation & Usage

### 1. Prérequis
*   Python 3.8+
*   Un environnement virtuel recommandé

### 2. Installation
```bash
# Installation des dépendances
pip install playwright trafilatura dateparser

# Installation des navigateurs pour Playwright
playwright install chromium
```

### 3. Configuration
*   Éditez `urls.txt` pour ajouter vos sources préférées.
*   (Optionnel) Modifiez `OUTPUT_DIR` dans `ingest_auto_crawl.py` pour pointer vers votre dossier Drive local.

### 4. Lancement (Pipeline Automatique)
```bash
python ingest_auto_crawl.py
```
Le crawler va scanner les URLs, filtrer les pollueurs, vérifier les dates, et sauvegarder le contenu pertinent.

### 5. Outils Complémentaires

#### 🎯 Import Manuel (Mode Sniper)
Pour ajouter un article spécifique sans relancer tout le crawl (utilise la même logique de classification) :
```bash
python ingest_manual.py
# Puis collez l'URL quand demandé
```

#### 🧹 Nettoyage (Anti-Bruit Interactif)
Si jamais des fichiers indésirables sont passés :
```bash
python clean_noise.py
```
*   Mode interactif : Vous liste les fichiers suspects.
*   Suppression par lot (si > 30 fichiers) ou un par un.

## 📂 Structure des Dossiers (Exemple)

```text
NotebookLM_Sources/
├── Generative AI/
│   └── LLMs/
│       ├── 2024/
│       │   └── 2024-03-15_openai_gpt4_technical_report.md
│       └── 2025/
│           └── 2025-01-10_google_research_gemini_ultra_update.md
├── Agentic AI/
│   └── Agents/
│       └── 2025/
│           └── 2025-02-12_anthropic_building_effective_agents.md
├── Deep Learning/
│   └── Theory/
│       └── Undated/
│           └── Undated_web_introduction_to_transformers.md
```