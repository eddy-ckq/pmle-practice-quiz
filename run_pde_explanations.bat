@echo off
echo ===================================================
echo     Generating Deep AI Explanations for PDE
echo ===================================================

if not exist GEMINI_API_KEY.txt (
    echo [ERROR] GEMINI_API_KEY.txt not found!
    echo Please create this file and paste your Gemini API key in it.
    pause
    exit /b 1
)

echo Step 1: Querying Gemini API for Explanations...
python generate_deep_explanations.py --file pde_parsed.json

if %ERRORLEVEL% neq 0 (
    echo [ERROR] generate_deep_explanations.py failed.
    pause
    exit /b %ERRORLEVEL%
)

echo Step 2: Formatting Explanations to HTML...
python format_explanations.py pde_parsed.json

if %ERRORLEVEL% neq 0 (
    echo [ERROR] format_explanations.py failed.
    pause
    exit /b %ERRORLEVEL%
)

echo ===================================================
echo     Success! Explanations are now available.
echo ===================================================
pause
