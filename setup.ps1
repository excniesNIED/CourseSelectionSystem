# 教务系统启动脚本

Write-Host "=== 教务系统选课管理平台启动脚本 ===" -ForegroundColor Green

# 检查是否在正确的目录
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "错误：请在项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

# 创建.env文件（如果不存在）
if (-not (Test-Path "backend\.env")) {
    Write-Host "创建后端环境配置文件..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "请编辑 backend\.env 文件配置数据库连接信息" -ForegroundColor Yellow
}

# 安装后端依赖
Write-Host "安装后端Python依赖..." -ForegroundColor Blue
Set-Location backend
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "后端依赖安装失败" -ForegroundColor Red
    exit 1
}
Set-Location ..

# 安装前端依赖
Write-Host "安装前端Node.js依赖..." -ForegroundColor Blue
Set-Location frontend
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "前端依赖安装失败" -ForegroundColor Red
    exit 1
}
Set-Location ..

Write-Host ""
Write-Host "=== 安装完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "接下来的步骤：" -ForegroundColor Yellow
Write-Host "1. 安装并启动MariaDB数据库"
Write-Host "2. 编辑 backend\.env 文件配置数据库连接"
Write-Host "3. 导入数据库：mysql -u root -p course_selection_system < database\init.sql"
Write-Host "4. 启动后端：cd backend && python run.py"
Write-Host "5. 启动前端：cd frontend && npm run dev"
Write-Host ""
Write-Host "默认登录信息：" -ForegroundColor Cyan
Write-Host "管理员：admin / admin123"
Write-Host "教师：T001 / teacher123"
Write-Host "学生：202301001001 / student123"
