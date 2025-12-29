@echo off
chcp 65001 > nul
echo ===================================================
echo      🚀 Lancement du Pipeline NotebookLM
echo ===================================================
echo.

cd /d "C:\Users\steve\Desktop\Changement carrière\Projets Python\my-notebooklm-pipeline"

echo 1. Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo 2. Lancement du Crawler (Playwright)...
python ingest_auto_crawl.py

echo.
echo ===================================================
echo      🧹 Nettoyage des fichiers parasites ?
echo ===================================================
set /p clean="Voulez-vous lancer le script de nettoyage (y/n) ? "
if /i "%clean%"=="y" (
    python clean_noise.py
)

echo.
echo ✅ Terminé.
pause