# LK 压缩 · Windows 图片音频资源压缩工具

面向 Windows 10/11 x64 的桌面 EXE 软件，用于批量压缩游戏或应用中的图片、音频资源。使用 Python、PySide6 和多种本地压缩工具，支持拖放、目录扫描、参数调整、进度统计与日志查看。

## 下载与运行

前往 [Release 下载页面](https://github.com/luokai-demo/lk-compressor/releases/latest)，下载 `LK-Compressor-v2.1.0-Windows-x64.exe`，双击运行；使用打包版本无需安装 Python，也无需另外配置压缩工具。当前发行版未进行代码签名。

**压缩会在原位置覆盖变小的文件。请先备份或复制资源，再在副本上测试。** 常规压缩和极致压缩都可能产生有损结果；音频使用低码率编码，不适合对音质要求高的原始素材。

## 当前功能

- 图片：PNG、JPG、JPEG。
- 音频：MP3、WAV、FLAC、OGG、AAC、M4A、WMA，可选择同时处理。
- 常规压缩：较高质量的有损压缩，兼顾速度与体积。
- 极致压缩：串联量化和优化工具，支持调整质量、迭代次数等参数。
- 拖入文件或文件夹，查看处理进度、结果统计及可折叠日志，支持停止任务。
- 仅在输出文件变小时覆盖；不改变原文件扩展名。此行为不等于画质、音质或内容完全无损。

## Windows 源码开发

使用 **Python 3.13 x64** 和 PowerShell。仓库只保存源码、文档与图标；本机工具、运行日志、用户配置、历史测试数据和 EXE 不进入 Git。

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

从同一版本 Release 下载 `windows-build-tools.zip`，核对 `SHA256SUMS.txt` 后解压到项目根目录。解压后应出现 `tools/modes/pngquant.exe` 等文件，详见 [压缩工具准备](tools/modes/README.md)。工具包含 Windows 原生扩展，不能用 macOS/Linux 环境替代。

```powershell
.
un_dev.ps1
.uild.ps1
```

构建产物位于 `dist/图片压缩工具.exe`。脚本使用当前 Python 环境，请先激活虚拟环境。图标和第三方工具的许可范围见 [第三方组件说明](docs/第三方组件.md)。

## 验证与发布

```powershell
python -m compileall -q src test
python -m unittest discover -s test -v
```

GitHub Actions 执行语法检查、核心单元测试、CodeQL 分析；Windows 构建流程还会执行合成 PNG/JPEG/音频压缩测试，并启动实际打包的 EXE，再上传 Release 附件。发布步骤见 [发布说明](docs/发布说明.md)，参数契约见 [API 文档](docs/API文档.md)。

## 隐私与安全

软件在本机调用工具处理文件。日志可能包含所选资源的文件名、完整路径和工具输出，分享前请自行脱敏；不要将日志、项目私有素材或凭证加入仓库。软件“关于”窗口保留作者信息。

漏洞请使用仓库 **Security → Report a vulnerability** 私密报告，详见 [安全策略](SECURITY.md)。一般问题可提交 Issue，并使用合成样例说明，避免上传公司或个人原始资源。

## 目录

```text
src/                  界面、压缩逻辑与打包配置
image/                应用图标
test/                 可重复运行的核心测试
scripts/              Windows 发行包验证
.github/              自动检查、依赖更新和构建流程
docs/                 API、工具许可与发布说明
tools/modes/README.md 压缩工具目录要求
build.ps1             Windows 打包入口
run_dev.ps1           Windows 开发启动入口
```

本项目自有代码按 [MIT 许可证](LICENSE) 提供；第三方工具和图标不因本项目许可证而变更其原有权利。
