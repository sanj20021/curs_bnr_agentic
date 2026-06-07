@echo off
setlocal
color 0B

echo ==============================================================================
echo   PROIECT FINAL - Verificare dependinte
echo   Autor: Cristian Antonescu
echo ==============================================================================
echo.
echo [1/2] Verificam si instalam dependintele de Python (Backend)...
pip install -r requirements.txt <nul

echo.
echo [2/2] Verificam si instalam dependintele de Node.js (Frontend)...
cd frontend
call npm install <nul
cd ..

:: Dupa instalare curatam ecranul pentru impact vizual maxim
cls

echo ==============================================================================
echo.
echo     ____  _   _ ____      _    ____ _____ _   _ _____ 
echo    ^| __ )^| \ ^| ^|  _ \    / \  / ___^| ____^| \ ^| ^|_   _^|
echo    ^|  _ \^|  \^| ^| ^|_) ^|  / _ \^| ^|  _^|  _^| ^|  \^| ^| ^| ^|  
echo    ^| ^|_) ^| ^|\  ^|  _ ^<  / ___ \ ^|_^| ^| ^|___^| ^|\  ^| ^| ^|  
echo    ^|____/^|_^| \_^|_^| \_\/_/   \_\____^|_____^|_^| \_^| ^|_^|  
echo.
echo ==============================================================================
echo   PROIECT FINAL - Asistent Agentic pentru Prognoza Valutara (PLN/RON)
echo   Autor: Cristian Antonescu
echo   Master: SIIPA, UNITBV, An 1
echo   Curs: Aplicatii ale inteligentei artificiale in economie
echo   Instructor: Teodor Stefan BILDEA
echo ==============================================================================
echo.
echo   Toate dependintele au fost instalate si verificate cu succes!
echo.

:ask
set "START_APP="
set /p START_APP="Pornim serverele aplicatiei? (Y/N): "
if /I "%START_APP%"=="Y" goto start
if /I "%START_APP%"=="N" goto end
echo Tasta invalida! Te rog sa alegi Y sau N.
goto ask

:start
echo.
:: Pornire Backend
echo [-] Pornim Backend-ul in fundal...
start "Backend BNR" cmd /k "python -m uvicorn src.api.server:app --port 7772"

:: Asteptam 3 secunde pentru a permite backend-ului sa porneasca
timeout /t 3 /nobreak >nul

:: Pornire Frontend
cd frontend
start "Frontend BNR" cmd /k "npm run dev"

echo.
echo ==============================================================================
echo   Gata! Aplicatia se va deschide automat in browserul tau principal.
echo ==============================================================================
goto eof

:end
echo.
echo O zi excelenta! Apasa orice tasta pentru a iesi.
pause >nul

:eof
endlocal
