@echo off
echo ==============================
echo 🚀 Initialisation du projet...
echo ==============================

REM --- Redémarrer PostgreSQL ---
echo 🔄 Redémarrage de PostgreSQL...
pg_ctl restart -D "C:\Program Files\PostgreSQL\17\data"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur lors du redémarrage de PostgreSQL. Vérifiez votre installation.
    pause
    exit /b
)
echo ✅ PostgreSQL a été redémarré avec succès.

REM --- Ouvrir une nouvelle fenêtre CMD pour Django ---
echo 🏗️ Lancement de l'environnement virtuel et du serveur Django...
start cmd /k "call .venv\Scripts\activate && pip install -r requirements.txt && python manage.py runserver"

echo ✅ Tout est prêt !
pause
