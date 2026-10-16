# 构建 Windows x64 单文件 EXE，使用当前已激活的 Python 环境。
$ErrorActionPreference = 'Stop'
# 项目目录与发布输出目录。
$projectDir = $PSScriptRoot
$distDir = Join-Path $projectDir 'dist'
if (-not $IsWindows -and $env:OS -ne 'Windows_NT') { throw '此脚本只支持 Windows' }
Push-Location $projectDir
try {
    python -X utf8 -c "import struct,sys; assert sys.version_info[:2] == (3,13) and struct.calcsize('P') == 8, '需要 Python 3.13 x64'"
    if ($LASTEXITCODE -ne 0) { throw 'Python 环境不符合要求' }
    python -X utf8 scripts/prepare_build.py
    if ($LASTEXITCODE -ne 0) { throw '构建依赖检查失败' }
    python -X utf8 -m PyInstaller --noconfirm --clean src/compress_gui.spec
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller 打包失败' }
    python -X utf8 -m pip freeze | Set-Content (Join-Path $distDir 'build-dependencies.txt') -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw '依赖版本记录失败' }
    Write-Host "构建完成：$distDir\图片压缩工具.exe"
} finally {
    Pop-Location
}
