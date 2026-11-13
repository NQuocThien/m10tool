@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title Squeezing Tech Studio
cd /d "%~dp0"
python app.py
if errorlevel 1 pause
