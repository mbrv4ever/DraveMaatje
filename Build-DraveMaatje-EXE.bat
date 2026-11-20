@echo off
cd /d "%~dp0"
set PY=
for %%v in (3.10 3.11 3.12) do (
  if not defined PY ( py -%%v -c "import sys" >nul 2>&1 && set PY=py -%%v )
)
if not defined PY ( echo Geen Python 3.10-3.12 gevonden. & pause & exit /b 1 )
%PY% -c "import PyQt6.QtWidgets" >nul 2>&1 || %PY% -m pip install PyQt6
%PY% -c "import send2trash" >nul 2>&1 || %PY% -m pip install send2trash
%PY% -c "import neuvoice, sounddevice" >nul 2>&1 || %PY% -m pip install "numpy<2" neuvoice sounddevice
%PY% -c "import PyInstaller" >nul 2>&1 || %PY% -m pip install pyinstaller
if exist "..\DraveHanden\handen.py" copy /y "..\DraveHanden\handen.py" handen.py >nul
if exist "..\DraveHanden\klusjes.py" copy /y "..\DraveHanden\klusjes.py" klusjes.py >nul
if exist "..\DraveHanden\paspoort.py" copy /y "..\DraveHanden\paspoort.py" paspoort.py >nul
if exist "..\DraveHanden\bescherm.py" copy /y "..\DraveHanden\bescherm.py" bescherm.py >nul
if exist "..\DraveHanden\handen_qt.py" copy /y "..\DraveHanden\handen_qt.py" handen_qt.py >nul
%PY% make_icon.py
rem jouw gegevens in dist eerst bewaren, na het bouwen terugzetten
if exist _bewaar rmdir /s /q _bewaar
mkdir _bewaar
if exist "dist\DraveMaatje\paspoorten" xcopy /e /i /y /q "dist\DraveMaatje\paspoorten" "_bewaar\paspoorten" >nul
for %%f in (maatje_instellingen.json handen_logboek.txt handen_terug.json) do if exist "dist\DraveMaatje\%%f" copy /y "dist\DraveMaatje\%%f" _bewaar\ >nul
%PY% -m PyInstaller --noconfirm --clean --windowed --onedir --name DraveMaatje --icon assets\icon.ico --hidden-import handen --hidden-import klusjes --hidden-import paspoort --hidden-import bescherm --hidden-import handen_qt --hidden-import stem --hidden-import uitspraak --hidden-import send2trash --collect-all neuvoice --collect-binaries onnxruntime --collect-all sounddevice main.py
if errorlevel 1 ( echo BOUWEN MISLUKT & pause & exit /b 1 )
if not exist "dist\DraveMaatje\DraveMaatje.exe" ( echo GEEN EXE GEVONDEN & pause & exit /b 1 )
xcopy /e /i /y assets "dist\DraveMaatje\assets" >nul
if exist DraveMaatje_snelgids.pdf copy /y DraveMaatje_snelgids.pdf "dist\DraveMaatje\" >nul
for %%f in (maatje_instellingen.json handen_logboek.txt handen_terug.json) do if exist "_bewaar\%%f" copy /y "_bewaar\%%f" "dist\DraveMaatje\" >nul
if exist "_bewaar\paspoorten" xcopy /e /i /y /q "_bewaar\paspoorten" "dist\DraveMaatje\paspoorten" >nul
echo KLAAR: dist\DraveMaatje\DraveMaatje.exe
