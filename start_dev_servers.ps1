#!/usr/bin/env pwsh

# 冰刀系统开发服务器启动脚本
Write-Host "=== 冰刀系统开发服务器启动脚本 ===" -ForegroundColor Green
Write-Host "正在启动后端和前端开发服务器..." -ForegroundColor Yellow

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# 后端服务器启动
Write-Host "`n启动后端 Django 服务器..." -ForegroundColor Cyan
$BackendJob = Start-Job -ScriptBlock {
    param($ProjectPath)
    Set-Location $ProjectPath
    & ".\venv\Scripts\python.exe" manage.py runserver
} -ArgumentList $ScriptDir

# 前端服务器启动
Write-Host "启动前端 Vue 服务器..." -ForegroundColor Cyan
$FrontendJob = Start-Job -ScriptBlock {
    param($ProjectPath)
    Set-Location "$ProjectPath\frontend"
    npm run dev
} -ArgumentList $ScriptDir

# 等待一下让服务器启动
Start-Sleep -Seconds 3

Write-Host "`n=== 服务器启动完成 ===" -ForegroundColor Green
Write-Host "后端服务器: http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "前端服务器: http://localhost:5173/" -ForegroundColor White
Write-Host "`n按 Ctrl+C 停止所有服务器" -ForegroundColor Yellow

# 监控作业状态
try {
    while ($true) {
        # 检查作业是否还在运行
        if ((Get-Job -Id $BackendJob.Id).State -eq "Failed") {
            Write-Host "后端服务器启动失败!" -ForegroundColor Red
            Receive-Job -Id $BackendJob.Id
        }
        
        if ((Get-Job -Id $FrontendJob.Id).State -eq "Failed") {
            Write-Host "前端服务器启动失败!" -ForegroundColor Red
            Receive-Job -Id $FrontendJob.Id
        }
        
        Start-Sleep -Seconds 1
    }
}
catch {
    Write-Host "`n正在停止所有服务器..." -ForegroundColor Yellow
}
finally {
    # 清理作业
    Stop-Job -Id $BackendJob.Id -ErrorAction SilentlyContinue
    Stop-Job -Id $FrontendJob.Id -ErrorAction SilentlyContinue
    Remove-Job -Id $BackendJob.Id -ErrorAction SilentlyContinue
    Remove-Job -Id $FrontendJob.Id -ErrorAction SilentlyContinue
    Write-Host "所有服务器已停止。" -ForegroundColor Green
} 