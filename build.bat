@echo off
REM ==== Este script usa o Python de DENTRO do venv (venv\Scripts\python.exe) ====
REM Assim o empacotamento sempre usa o ambiente certo, com o PySide6 instalado,
REM em vez de depender do "python" solto do PATH (que pode cair no Python global).

set PY=venv\Scripts\python.exe

if not exist "%PY%" (
    echo ERRO: nao encontrei venv\Scripts\python.exe
    echo Crie o ambiente virtual primeiro:  python -m venv venv
    pause
    exit /b 1
)

echo Instalando dependencias no venv (PySide6 + PyInstaller)...
"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install PySide6 pyinstaller

echo.
echo Gerando o executavel...
"%PY%" -m PyInstaller --noconfirm Crosshair.spec

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
