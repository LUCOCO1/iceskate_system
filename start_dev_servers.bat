@echo off
chcp 65001 >nul
title 冰刀系统开发服务器

echo =======================================
echo     冰刀系统开发服务器启动脚本
echo =======================================
echo.

echo 启动后端 Django 服务器...
start "后端服务器" cmd /k ".\venv\Scripts\python.exe manage.py runserver"

echo 等待后端服务器启动...
timeout /t 3 /nobreak >nul

echo 启动前端 Vue 服务器...
start "前端服务器" cmd /k "cd frontend && npm run dev"

echo.
echo =======================================
echo     服务器启动完成
echo =======================================
echo 后端服务器: http://127.0.0.1:8000/
echo 前端服务器: http://localhost:5173/
echo.
echo 关闭此窗口不会停止服务器
echo 请在各自的服务器窗口中按 Ctrl+C 停止服务器
echo.
pause 