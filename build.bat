@echo off
REM ==== Rode este arquivo com o ambiente virtual (venv) ATIVADO ====

echo Instalando PyInstaller (se necessario)...
pip install pyinstaller

echo.
echo Gerando o executavel...
python -m PyInstaller Crosshair.spec

echo.
echo Copiando recursos para a pasta do app...
copy /Y icon.ico "dist\Crosshair\" >nul
if exist fonts xcopy /E /I /Y fonts "dist\Crosshair\fonts" >nul

echo.
echo ============================================
echo  Pronto! Abra:  dist\Crosshair\Crosshair.exe
echo  Para distribuir: zipe a pasta dist\Crosshair
echo ============================================
pause
