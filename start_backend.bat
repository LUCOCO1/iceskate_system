@echo off
chcp 65001 >nul
title 冰刀系统后端服务器

echo =======================================
echo       启动后端 Django 服务器
echo =======================================
echo.

echo 正在启动后端服务器...
.\venv\Scripts\python.exe manage.py runserver

echo.
echo 服务器已停止
pause 