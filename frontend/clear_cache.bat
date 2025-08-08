@echo off
echo 正在清除前端缓存...
cd /d "%~dp0"
if exist node_modules rmdir /s /q node_modules
if exist dist rmdir /s /q dist
if exist .vite rmdir /s /q .vite
npm cache clean --force
echo 重新安装依赖...
npm install
echo 缓存清理完成，请手动启动开发服务器：npm run dev
pause 