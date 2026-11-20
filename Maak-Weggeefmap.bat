@echo off
rem Maak-Weggeefmap.bat - een schone map om DraveMaatje weg te geven.
rem ZONDER jouw eigen gegevens: geen paspoorten, geen logboek, geen terugzet-bestand, geen instellingen, geen cache.
cd /d "%~dp0"
if not exist "dist\DraveMaatje\DraveMaatje.exe" ( echo Eerst bouwen: Build-DraveMaatje-EXE.bat & pause & exit /b 1 )
if exist "weggeven\DraveMaatje" rmdir /s /q "weggeven\DraveMaatje"
mkdir "weggeven\DraveMaatje"
robocopy "dist\DraveMaatje" "weggeven\DraveMaatje" /E /NFL /NDL /NJH /NJS /XD paspoorten cache _bewaar /XF maatje_instellingen.json handen_logboek.txt handen_terug.json *.log >nul
if errorlevel 8 ( echo KOPIEREN MISLUKT & pause & exit /b 1 )
copy /y "Lees_mij_eerst.pdf" "weggeven\DraveMaatje\" >nul
copy /y "DraveMaatje_snelgids.pdf" "weggeven\DraveMaatje\" >nul
if exist "DraveMaatje_uitleg.mp4" copy /y "DraveMaatje_uitleg.mp4" "weggeven\DraveMaatje\" >nul
if not exist "weggeven\DraveMaatje\DraveMaatje.exe" ( echo GEEN EXE IN DE WEGGEEFMAP & pause & exit /b 1 )
echo KLAAR: weggeven\DraveMaatje
