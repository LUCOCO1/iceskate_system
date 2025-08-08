@echo off
chcp 65001 >nul
title 冰刀系统前端服务器

echo =======================================
echo       启动前端 Vue 服务器
echo =======================================
echo.

echo 正在启动前端服务器...
cd frontend
npm run dev

echo.
echo 服务器已停止
pause 