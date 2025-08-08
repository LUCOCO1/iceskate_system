@echo off
chcp 65001 > nul
echo 正在启动Node.js环境安装脚本...
PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& {Start-Process PowerShell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File "".\setup_nodejs.ps1""' -Verb RunAs}"
pause 