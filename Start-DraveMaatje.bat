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
if exist "..\DraveHanden\handen.py" copy /y "..\DraveHanden\handen.py" handen.py >nul
if exist "..\DraveHanden\klusjes.py" copy /y "..\DraveHanden\klusjes.py" klusjes.py >nul
if exist "..\DraveHanden\paspoort.py" copy /y "..\DraveHanden\paspoort.py" paspoort.py >nul
if exist "..\DraveHanden\bescherm.py" copy /y "..\DraveHanden\bescherm.py" bescherm.py >nul
if exist "..\DraveHanden\handen_qt.py" copy /y "..\DraveHanden\handen_qt.py" handen_qt.py >nul
start "" %PY% main.py
