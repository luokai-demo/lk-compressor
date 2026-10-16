# Windows 压缩工具准备

这些文件只用于本机运行和打包，不提交到 Git。请从本项目相同版本 [Release](https://github.com/luokai-demo/lk-compressor/releases) 下载 `windows-build-tools.zip`，核对 SHA256 后解压到项目根目录。

```text
tools/modes/
├── pngquant.exe
├── oxipng.exe
├── jpegoptim.exe
├── cjpeg-static.exe
├── zopfli.exe
├── zopflipng.exe
├── _cffi_backend.cp313-win_amd64.pyd
├── imagequant/
│   ├── __init__.py
│   └── _libimagequant.pyd
├── ffmpeg/ffmpeg-7.0.2-essentials_build/bin/ffmpeg.exe
└── licenses/                 上游许可证、版权及来源说明
```

`imagequant` 和 CFFI 原生扩展对应 Python 3.13、Windows x64。Python 依赖另通过根目录 `requirements-dev.txt` 安装；不要把其他 Python 版本或操作系统的原生文件混入工具包。

`djpeg`、`jpegtran`、`rdjpgcom`、`wrjpgcom`、FFplay、FFprobe 不是当前运行或打包所需文件，不再分发。旧测试音频和压缩脚本也不属于构建依赖。

来源和许可见 [第三方组件说明](../../docs/第三方组件.md)。更新工具时，应保留对应版本的上游许可及源码获取方式，并重新验证发布包。
