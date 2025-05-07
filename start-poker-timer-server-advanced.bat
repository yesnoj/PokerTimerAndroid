@echo off
setlocal enabledelayedexpansion

:: Imposta il titolo e i colori
title Poker Timer Server
color 0A

:: Visualizza un banner
echo.
echo ===============================
echo    POKER TIMER SERVER LAUNCHER
echo ===============================
echo.

:: Verifica se Node.js è installato
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    color 0C
    echo Errore: Node.js non è installato o non è presente nel PATH.
    echo Installare Node.js da https://nodejs.org/
    pause
    exit /b 1
)

:: Mostra la versione di Node.js installata
for /f "tokens=* usebackq" %%a in (`node -v`) do set NODE_VERSION=%%a
echo Versione Node.js installata: %NODE_VERSION%
echo.

:: Naviga alla directory del server
cd /d "%~dp0poker-timer-monitor"

:: Verifica l'esistenza della directory
if not exist "%~dp0poker-timer-monitor" (
    color 0C
    echo Errore: La directory 'poker-timer-monitor' non esiste.
    echo.
    echo Opzioni disponibili:
    echo 1. Creare la directory
    echo 2. Uscire
    echo.
    set /p CHOICE="Seleziona un'opzione (1/2): "
    
    if "!CHOICE!"=="1" (
        mkdir "%~dp0poker-timer-monitor"
        echo Directory creata con successo.
        cd /d "%~dp0poker-timer-monitor"
        
        :: Creare un package.json di base
        echo { "name": "poker-timer-monitor", "version": "1.0.0", "description": "Server per il monitoraggio dei poker timer", "main": "index.js", "dependencies": { "express": "^4.17.1", "cors": "^2.8.5", "body-parser": "^1.19.0" } } > package.json
        
        :: Copia il file index.js fornito nella cartella giusta
        if exist "%~dp0index.js" (
            copy "%~dp0index.js" "%~dp0poker-timer-monitor\index.js"
            echo File index.js copiato nella directory.
        ) else (
            echo AVVISO: File index.js non trovato. Sarà necessario copiarlo manualmente.
        )
        
        :: Crea la cartella public e copia l'index.html se disponibile
        mkdir public
        if exist "%~dp0index.html" (
            copy "%~dp0index.html" "%~dp0poker-timer-monitor\public\index.html"
            echo File index.html copiato nella directory public.
        ) else (
            echo AVVISO: File index.html non trovato. Sarà necessario copiarlo manualmente.
        )
    ) else (
        echo Operazione annullata.
        pause
        exit /b 1
    )
)

:: Verifica se il file index.js esiste
if not exist "index.js" (
    color 0C
    echo Errore: File 'index.js' non trovato nella directory 'poker-timer-monitor'.
    echo Assicurati che il file server sia presente nella directory corretta.
    pause
    exit /b 1
)

:: Verifica se esiste la cartella public
if not exist "public" (
    echo Creazione della directory 'public'...
    mkdir public
)

:: Verifica se il file index.html esiste nella cartella public
if not exist "public\index.html" (
    color 0E
    echo Avviso: File 'index.html' non trovato nella directory 'public'.
    echo Se hai già un file index.html, copialo nella cartella 'public'.
    
    :: Chiedi all'utente se vuole creare un file HTML di base
    set /p CREATE_HTML="Vuoi creare un file HTML di base? (s/n): "
    if /i "!CREATE_HTML!"=="s" (
        echo ^<!DOCTYPE html^> > public\index.html
        echo ^<html lang="it"^> >> public\index.html
        echo ^<head^> >> public\index.html
        echo     ^<meta charset="UTF-8"^> >> public\index.html
        echo     ^<meta name="viewport" content="width=device-width, initial-scale=1.0"^> >> public\index.html
        echo     ^<title^>Poker Timer Monitor^</title^> >> public\index.html
        echo ^</head^> >> public\index.html
        echo ^<body^> >> public\index.html
        echo     ^<h1^>Poker Timer Monitor^</h1^> >> public\index.html
        echo     ^<p^>Pagina di base. Sostituisci con la tua index.html completa.^</p^> >> public\index.html
        echo ^</body^> >> public\index.html
        echo ^</html^> >> public\index.html
        
        echo File HTML di base creato.
    )
)

:: Verifica se la cartella node_modules esiste, altrimenti installa le dipendenze
if not exist "node_modules" (
    echo Installazione dipendenze Node.js...
    echo.
    call npm install
    if %ERRORLEVEL% neq 0 (
        color 0C
        echo Errore nell'installazione delle dipendenze.
        pause
        exit /b 1
    )
    echo.
    echo Dipendenze installate con successo.
)

:: Controlla se la porta 3000 è già in uso
set "PORTA_IN_USO="
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    set "PORTA_IN_USO=1"
)

if defined PORTA_IN_USO (
    color 0E
    echo AVVISO: La porta 3000 è già in uso.
    echo Un'altra applicazione potrebbe già essere in esecuzione su questa porta.
    echo.
    set /p CONTINUE="Continuare comunque? (s/n): "
    if /i not "!CONTINUE!"=="s" (
        echo Operazione annullata.
        pause
        exit /b 1
    )
)

:: Chiedi all'utente se vuole aprire il browser automaticamente
set /p OPEN_BROWSER="Aprire automaticamente il browser dopo l'avvio del server? (s/n): "

:: Avvia il server Node.js
echo.
echo Avvio del server Node.js sulla porta 3000...
start "Poker Timer Server" cmd /c "node index.js & pause"

:: Attendi che il server sia pronto (5 secondi)
echo Attendi avvio del server...
timeout /t 5 /nobreak >nul

:: Apri il browser predefinito sulla pagina locale se l'utente ha scelto di farlo
if /i "%OPEN_BROWSER%"=="s" (
    echo Apertura browser...
    start http://localhost:3000
)

:: Mostra informazioni e istruzioni
color 0A
echo.
echo ===============================
echo    SERVER AVVIATO CON SUCCESSO
echo ===============================
echo.
echo Indirizzo server: http://localhost:3000
echo.
echo Puoi accedere al server da qualsiasi dispositivo sulla rete locale usando:
echo   http://[TUO_INDIRIZZO_IP]:3000
echo.
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    set IP=!IP:~1!
    echo Possibile indirizzo: http://!IP!:3000
)
echo.
echo Per arrestare il server, chiudi la finestra del server o premi CTRL+C.
echo.

:: Mantiene aperta la finestra batch
pause

endlocal