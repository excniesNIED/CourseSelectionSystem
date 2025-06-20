# 启动后端服务
Write-Host "启动后端服务..." -ForegroundColor Green

# 检查是否在backend目录
if (-not (Test-Path "run.py")) {
    if (Test-Path "..\backend\run.py") {
        Set-Location backend
    } else {
        Write-Host "错误：找不到后端项目文件" -ForegroundColor Red
        exit 1
    }
}

# 检查.env文件
if (-not (Test-Path ".env")) {
    Write-Host "警告：.env文件不存在，请先配置数据库连接" -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "已创建.env文件，请编辑后重新运行" -ForegroundColor Yellow
    exit 1
}

Write-Host "正在启动Flask后端服务 (http://localhost:5000)..." -ForegroundColor Blue
python run.py
