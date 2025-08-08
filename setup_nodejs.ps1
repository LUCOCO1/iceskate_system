# 冰刀系统 - Node.js 环境自动安装脚本
# 此脚本将自动安装Node.js、配置环境并安装项目依赖

# 设置脚本执行策略为允许执行
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 定义颜色函数，用于输出彩色文本
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# 显示欢迎信息
Write-ColorOutput Green "====================================================="
Write-ColorOutput Green "      欢迎使用冰刀系统 Node.js 环境自动安装脚本"
Write-ColorOutput Green "====================================================="
Write-Output ""

# 检查是否已安装Node.js
$nodeInstalled = $false
try {
    $nodeVersion = node -v
    $npmVersion = npm -v
    $nodeInstalled = $true
    Write-ColorOutput Green "已检测到Node.js安装:"
    Write-Output "Node.js版本: $nodeVersion"
    Write-Output "NPM版本: $npmVersion"
} catch {
    Write-ColorOutput Yellow "未检测到Node.js，将进行安装..."
}

# 如果未安装Node.js，则下载并安装
if (-not $nodeInstalled) {
    # 直接下载Node.js安装包
    Write-ColorOutput Cyan "正在下载Node.js安装包..."
    $nodeUrl = "https://nodejs.org/dist/v18.18.2/node-v18.18.2-x64.msi"
    $nodeInstaller = "$env:TEMP\node-v18.18.2-x64.msi"
    
    try {
        Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeInstaller
        Write-ColorOutput Green "Node.js安装包下载完成，开始安装..."
        
        # 运行Node.js安装程序
        Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$nodeInstaller`" /quiet /norestart" -Wait
        
        # 刷新环境变量
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # 验证安装
        try {
            $nodeVersion = & "$env:ProgramFiles\nodejs\node.exe" -v
            $npmVersion = & "$env:ProgramFiles\nodejs\npm.cmd" -v
            Write-ColorOutput Green "Node.js安装成功:"
            Write-Output "Node.js版本: $nodeVersion"
            Write-Output "NPM版本: $npmVersion"
            
            # 设置临时环境变量，使当前会话可以使用node和npm命令
            $env:Path = "$env:ProgramFiles\nodejs;$env:Path"
        } catch {
            Write-ColorOutput Red "Node.js安装可能成功，但无法验证版本。"
            Write-ColorOutput Yellow "请重启计算机后再尝试使用Node.js。"
            Write-Output "错误信息: $_"
        }
    } catch {
        Write-ColorOutput Red "自动安装失败，请手动安装Node.js。"
        Write-ColorOutput Red "您可以从 https://nodejs.org/en/download/ 下载安装包。"
        Write-Output "错误信息: $_"
        exit 1
    }
} else {
    Write-ColorOutput Green "已安装Node.js，跳过安装步骤。"
}

# 配置npm镜像源为淘宝镜像，加速下载
Write-ColorOutput Cyan "正在配置npm镜像源为淘宝镜像..."
try {
    & npm config set registry https://registry.npmmirror.com
    Write-ColorOutput Green "npm镜像源配置完成！"
} catch {
    Write-ColorOutput Yellow "npm镜像源配置失败，将使用默认镜像源。"
    Write-Output "错误信息: $_"
}

# 进入前端目录并安装依赖
Write-ColorOutput Cyan "正在进入前端目录并安装项目依赖..."
Set-Location -Path ".\frontend"

# 检查是否存在package.json
if (Test-Path -Path "package.json") {
    # 安装项目依赖
    Write-ColorOutput Cyan "正在安装项目依赖，这可能需要几分钟时间..."
    try {
        & npm install
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput Green "项目依赖安装成功！"
        } else {
            Write-ColorOutput Red "项目依赖安装失败，请检查错误信息。"
            exit 1
        }
    } catch {
        Write-ColorOutput Red "安装依赖时出错。"
        Write-ColorOutput Yellow "如果刚刚安装了Node.js，请重启计算机后再尝试。"
        Write-Output "错误信息: $_"
        exit 1
    }
} else {
    Write-ColorOutput Red "未找到package.json文件，请确认您在正确的项目目录中。"
    exit 1
}

# 显示启动项目的命令
Write-ColorOutput Green "====================================================="
Write-ColorOutput Green "环境配置完成！您可以使用以下命令启动开发服务器："
Write-ColorOutput Cyan "cd frontend"
Write-ColorOutput Cyan "npm run dev"
Write-ColorOutput Green "====================================================="

# 询问是否立即启动开发服务器
$startDev = Read-Host "是否立即启动开发服务器？(y/n)"
if ($startDev -eq "y" -or $startDev -eq "Y") {
    Write-ColorOutput Cyan "正在启动开发服务器..."
    try {
        & npm run dev
    } catch {
        Write-ColorOutput Red "启动开发服务器失败。"
        Write-ColorOutput Yellow "如果刚刚安装了Node.js，请重启计算机后再尝试。"
        Write-Output "错误信息: $_"
    }
} else {
    Write-ColorOutput Yellow "您可以稍后手动启动开发服务器。"
} 