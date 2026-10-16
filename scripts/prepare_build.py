"""检查 Windows 工具并整理随 EXE 分发的 Python 包许可证。"""

from importlib import metadata
from pathlib import Path
import shutil

# 项目根目录与本机工具目录。
project_dir = Path(__file__).resolve().parents[1]
tools_dir = project_dir / 'tools' / 'modes'
# 当前压缩逻辑和打包配置需要的原生文件。
required_files = [
    'pngquant.exe', 'oxipng.exe', 'jpegoptim.exe', 'cjpeg-static.exe',
    'zopfli.exe', 'zopflipng.exe', 'imagequant/__init__.py',
    'imagequant/_libimagequant.pyd', '_cffi_backend.cp313-win_amd64.pyd',
    'ffmpeg/ffmpeg-7.0.2-essentials_build/bin/ffmpeg.exe',
    'licenses/第三方组件.md',
]
# 缺失工具时明确中止，避免生成不完整的发行包。
missing_files = [name for name in required_files if not (tools_dir / name).is_file()]
if missing_files:
    raise FileNotFoundError('构建依赖缺失：' + '、'.join(missing_files))

# Python 运行时依赖的版权和许可文件。
license_dir = tools_dir / 'licenses' / 'python'
license_dir.mkdir(parents=True, exist_ok=True)
for package_name in ['PySide6', 'PySide6_Addons', 'PySide6_Essentials',
                     'shiboken6', 'Pillow', 'cffi', 'pycparser']:
    # 已安装发行包及其声明的文件列表。
    package = metadata.distribution(package_name)
    for package_file in package.files or []:
        # 只复制许可、版权和通知，不带入本机环境信息。
        if not any(word in package_file.name.lower()
                   for word in ['license', 'copying', 'copyright', 'notice']):
            continue
        # 保留包内相对结构，避免同名许可证相互覆盖。
        source_file = Path(package.locate_file(package_file))
        target_file = license_dir / package_name / str(package_file)
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_file, target_file)
print('Windows 工具和许可证检查通过')
