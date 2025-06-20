# 启动前端服务
Write-Host "启动前端服务..." -ForegroundColor Green

# 检查是否在frontend目录
if (-not (Test-Path "package.json")) {
    if (Test-Path "..\frontend\package.json") {
        Set-Location frontend
    } else {
        Write-Host "错误：找不到前端项目文件" -ForegroundColor Red
        exit 1
    }
}

# 检查node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "安装前端依赖..." -ForegroundColor Yellow
    npm install
}

Write-Host "正在启动Vue前端服务 (http://localhost:3000)..." -ForegroundColor Blue
npm run dev
