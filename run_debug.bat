@echo off
REM Run Youtu-GraphRAG Backend with Debug Logging

echo ============================================================
echo Starting Youtu-GraphRAG Backend in DEBUG mode
echo ============================================================
echo.
echo Debug logging is ENABLED for:
echo   - Application core (backend.py)
echo   - GraphRAG constructor (models.constructor)
echo   - GraphRAG retriever (models.retriever)
echo   - Utilities (utils.*)
echo ============================================================
echo.

REM Set debug environment variables
set DEBUG=1
set LOG_LEVEL=DEBUG

REM Run the debug script
python run_debug.py

pause
