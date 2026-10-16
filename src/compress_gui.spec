# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

# 使用打包配置所在目录定位源码、工具和资源，不依赖调用位置。
source_dir = Path(SPECPATH)
project_dir = source_dir.parent
tools_dir = project_dir / 'tools' / 'modes'
# 只嵌入实际使用的工具，移除未调用的 JPEG 辅助程序。
tool_names = ['pngquant.exe', 'oxipng.exe', 'jpegoptim.exe',
              'cjpeg-static.exe', 'zopfli.exe', 'zopflipng.exe']
# 第三方可执行文件和许可证随 EXE 分发。
resource_files = [(str(tools_dir / name), 'modes') for name in tool_names]
resource_files += [
    (str(tools_dir / 'ffmpeg/ffmpeg-7.0.2-essentials_build/bin/ffmpeg.exe'),
     'modes/ffmpeg/ffmpeg-7.0.2-essentials_build/bin'),
    (str(tools_dir / 'licenses'), 'licenses'),
    (str(project_dir / 'image/icon.jpg'), 'image'),
]
# 明确声明 Windows 原生扩展，让打包器同时分析其 DLL 依赖。
native_files = [
    (str(tools_dir / 'imagequant/_libimagequant.pyd'), 'imagequant'),
    (str(tools_dir / '_cffi_backend.cp313-win_amd64.pyd'), '.'),
]
# 模块分析结果；不再引入项目没有使用的 NumPy 和 SciPy。
analysis = Analysis(
    [str(source_dir / 'compress_gui.py')],
    pathex=[str(source_dir), str(tools_dir)],
    binaries=native_files,
    datas=resource_files,
    hiddenimports=['imagequant', 'cffi', 'pycparser', 'PIL.Image', 'PIL.ImageDraw'],
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=['tkinter', 'customtkinter', 'tkinterdnd2'],
    noarchive=False, optimize=0,
)
# Python 模块压缩包。
python_archive = PYZ(analysis.pure)
# 发布单文件程序，保留原软件名称及关于窗口作者信息。
exe = EXE(
    python_archive, analysis.scripts, analysis.binaries, analysis.datas, [],
    name='图片压缩工具', debug=False, bootloader_ignore_signals=False,
    strip=False, upx=False, console=False,
    icon=str(project_dir / 'image/icon.jpg'),
)
