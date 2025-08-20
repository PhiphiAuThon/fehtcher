@echo off
title FEH Data Fetcher - Interactive Launcher
echo.
python "src\launcher.py"

echo.
echo 🧹 Auto-cleaning Python cache files...
python "src\cache_cleanup\clean_cache.py"

echo.
echo ✅ All done! Cache cleaned automatically.
pause
