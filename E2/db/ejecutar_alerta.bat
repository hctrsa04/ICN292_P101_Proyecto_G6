@echo off
cd /d "%~dp0"
python alerta_remate.py >> data\registro_alertas.txt 2>&1
