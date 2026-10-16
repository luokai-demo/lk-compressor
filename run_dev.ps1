# 使用当前已激活的 Python 环境启动 Windows 开发版本。
$ErrorActionPreference = 'Stop'
if (-not $IsWindows -and $env:OS -ne 'Windows_NT') { throw '此脚本只支持 Windows' }
Push-Location $PSScriptRoot
try {
    python src/compress_gui.py
    if ($LASTEXITCODE -ne 0) { throw '图片压缩工具启动失败，请检查依赖和日志' }
} finally {
    Pop-Location
}
