"""使用合成资源验证 Windows 工具及特殊文件名，不触碰真实资源。"""

import logging
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


@unittest.skipUnless(sys.platform == 'win32', '原生压缩工具仅支持 Windows')
class WindowsCompressionTest(unittest.TestCase):
    """真实调用已准备的 Windows 工具，确认压缩结果有效且体积减小。"""

    def setUp(self):
        """为每个场景准备独立临时目录、配置和日志。"""
        from src.modules.config import Config
        from src.modules.logger import Logger
        # 临时目录同时覆盖中文、空格和命令解释器特殊字符。
        self.directory = Path(tempfile.mkdtemp(prefix='合成资源 & 发布验证 '))
        self.config = Config()
        self.logger = Logger(str(self.directory / 'logs'))
        self.assertEqual(self.config.validate_tools(), [])

    def tearDown(self):
        """先关闭日志句柄，再清理本轮合成资源。"""
        for handler in list(logging.getLogger('ImageCompressor').handlers):
            # 文件句柄必须在 Windows 删除临时目录前释放。
            handler.close()
            logging.getLogger('ImageCompressor').removeHandler(handler)
        shutil.rmtree(self.directory)

    def test_png_and_jpeg_for_both_strategies(self):
        """两种策略均能压缩合成 PNG/JPEG，并保留可解码图像。"""
        from PIL import Image
        from src.modules.compressor import ImageCompressor
        # 渐变图便于验证真实压缩，不使用私有图片。
        image = Image.new('RGB', (256, 256))
        image.putdata([(x, y, (x + y) % 256) for y in range(256) for x in range(256)])
        for strategy in ('speed', 'compression'):
            for extension in ('png', 'jpg'):
                # 每种策略、格式使用独立源文件，避免重复压缩影响结论。
                with self.subTest(strategy=strategy, extension=extension):
                    path = self.directory / f'合成图片 & {strategy}.{extension}'
                    if extension == 'png':
                        image.save(path, compress_level=0)
                    else:
                        image.save(path, quality=100, subsampling=0)
                    original_size = path.stat().st_size
                    compressor = ImageCompressor(self.logger, self.config, strategy)
                    self.assertTrue(compressor.compress_images(str(path)))
                    self.assertLess(path.stat().st_size, original_size)
                    with Image.open(path) as compressed:
                        self.assertEqual(compressed.size, (256, 256))
                        compressed.verify()

    def test_mp3_is_compressed_and_remains_decodable(self):
        """合成高码率 MP3 压缩后仍能由 FFmpeg 解码。"""
        from src.modules.compressor import ImageCompressor
        # 用 FFmpeg 生成固定频率的测试音频。
        path = self.directory / '合成音频 & 测试.mp3'
        ffmpeg = self.config.get_tool_path('ffmpeg')
        subprocess.run([ffmpeg, '-y', '-f', 'lavfi', '-i',
                        'sine=frequency=440:duration=2', '-b:a', '320k', str(path)],
                       check=True, capture_output=True, timeout=30)
        original_size = path.stat().st_size
        compressor = ImageCompressor(self.logger, self.config, 'speed')
        self.assertTrue(compressor.compress_images(str(path), compress_audio=True))
        self.assertLess(path.stat().st_size, original_size)
        subprocess.run([ffmpeg, '-v', 'error', '-i', str(path), '-f', 'null', '-'],
                       check=True, capture_output=True, timeout=30)

    def test_unknown_strategy_is_rejected(self):
        """移除旧策略后，无效标识必须给出明确错误。"""
        from src.modules.compressor import ImageCompressor
        with self.assertRaisesRegex(ValueError, '未知压缩策略'):
            ImageCompressor(self.logger, self.config, 'balanced')
