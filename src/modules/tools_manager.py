import os
import subprocess
import shutil
from PIL import Image
from abc import ABC, abstractmethod
from .logger import Logger
from .parameter import ToolParameterSet, ParameterValidationError, TOOL_PARAMETER_DEFINITIONS

class CompressionTool(ABC):
    """压缩工具抽象基类"""

    def __init__(self, tool_path, logger=None):
        self.tool_path = tool_path
        self.logger = logger or Logger()

    def _validate_parameters(self, file_path, **kwargs):
        """验证压缩参数
        
        Args:
            file_path: 文件路径
            **kwargs: 压缩参数
            
        Returns:
            dict: 验证后的参数字典
            
        Raises:
            ParameterValidationError: 参数验证失败时抛出
        """
        # 获取工具名称（类名转换为工具名）
        tool_name = self.__class__.__name__.replace('Tool', '').lower()

        # 创建参数集合
        param_set = ToolParameterSet.from_dict(
            tool_name=tool_name,
            param_dict=kwargs,
            param_definitions=TOOL_PARAMETER_DEFINITIONS.get(tool_name, {})
        )

        # 验证参数
        param_set.validate()

        return param_set.to_dict()

    @abstractmethod
    def compress(self, file_path, **kwargs):
        """压缩文件"""
        pass

    def get_file_size(self, file_path):
        """获取文件大小"""
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0

class PNGQuantTool(CompressionTool):
    """pngquant压缩工具实现"""

    def compress(self, file_path, **kwargs):
        """使用pngquant压缩PNG文件"""
        original_size = self.get_file_size(file_path)
        tmp_file = file_path + ".tmp"

        try:
            # 验证参数
            validated_params = self._validate_parameters(file_path, **kwargs)

            # 获取验证后的参数
            quality = validated_params.get('quality', 15)
            speed = validated_params.get('speed', 1)

            # 使用最基本的参数，避免复杂选项导致的错误
            cmd = [
                self.tool_path,
                f"--quality={quality}-{quality+15}",  # 质量范围
                f"--speed={speed}",  # 速度参数
                "--force",
                "--output", tmp_file,
                file_path
            ]

            # 直接执行参数列表，避免资源路径中的特殊字符被命令解释器执行。
            result = subprocess.run(cmd, capture_output=True, text=True, shell=False, encoding='utf-8', errors='ignore')

            # 详细日志
            self.logger.debug(f"pngquant命令: {' '.join(cmd)}")
            self.logger.debug(f"pngquant返回码: {result.returncode}")
            self.logger.debug(f"pngquant标准输出: {result.stdout}")
            self.logger.debug(f"pngquant标准错误: {result.stderr}")

            if result.returncode == 0 and os.path.exists(tmp_file):
                new_size = self.get_file_size(tmp_file)
                self.logger.info(f"pngquant压缩后大小: {new_size} 字节")

                if new_size < original_size:
                    shutil.move(tmp_file, file_path)
                    self.logger.info(f"pngquant压缩成功，文件变小，已覆盖原文件")
                    return new_size
                else:
                    os.remove(tmp_file)
                    self.logger.warning(f"pngquant压缩后文件未变小，跳过覆盖")
            else:
                self.logger.error(f"pngquant压缩失败: {result.stderr} (错误码: {result.returncode})")
        except ParameterValidationError as e:
            self.logger.error(f"pngquant参数验证失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"pngquant压缩异常: {str(e)}")
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

        return original_size

class OxipngTool(CompressionTool):
    """oxipng压缩工具实现"""

    def compress(self, file_path, **kwargs):
        """使用oxipng优化PNG文件"""
        original_size = self.get_file_size(file_path)
        tmp_file = file_path + ".tmp"

        try:
            # 验证参数
            validated_params = self._validate_parameters(file_path, **kwargs)

            # 获取验证后的参数
            level = validated_params.get('level', 6)

            # 使用固定的最激进参数
            cmd = [
                self.tool_path,
                "-o", str(level),  # 优化级别
                "--out", tmp_file,
                "--strip", "all",  # 移除所有元数据
                "--interlace=1",  # 启用隔行扫描
                "--fix",  # 修复PNG文件
                file_path
            ]

            # 直接执行参数列表，避免资源路径中的特殊字符被命令解释器执行。
            result = subprocess.run(cmd, capture_output=True, text=True, shell=False, encoding='utf-8', errors='ignore')

            if result.returncode == 0 and os.path.exists(tmp_file):
                new_size = self.get_file_size(tmp_file)
                self.logger.info(f"oxipng优化后大小: {new_size} 字节")

                if new_size < original_size:
                    shutil.move(tmp_file, file_path)
                    self.logger.info(f"oxipng优化成功，文件变小，已覆盖原文件")
                    return new_size
                else:
                    os.remove(tmp_file)
                    self.logger.warning(f"oxipng优化后文件未变小，跳过覆盖")
            else:
                self.logger.error(f"oxipng优化失败: {result.stderr}")
        except ParameterValidationError as e:
            self.logger.error(f"oxipng参数验证失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"oxipng优化异常: {str(e)}")
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

        return original_size

class JpegoptimTool(CompressionTool):
    """jpegoptim压缩工具实现"""

    def __init__(self, tool_path, logger=None, config=None):
        super().__init__(tool_path, logger)
        self.config = config

    def compress(self, file_path, **kwargs):
        """使用jpegoptim压缩JPG文件"""
        original_size = self.get_file_size(file_path)
        tmp_file = f"{file_path}.tmp"

        try:
            # 验证参数
            validated_params = self._validate_parameters(file_path, **kwargs)

            # 复制原文件到临时文件
            shutil.copy2(file_path, tmp_file)

            # 从验证后的参数获取值
            quality = validated_params.get('quality', 10)
            self.logger.info(f"使用质量: {quality}% 压缩JPG文件")

            cmd = [
                self.tool_path,
                f"--max={quality}",
                "--strip-all",
                "--all-progressive",
                "--force",
                "--preserve"
            ]

            cmd.append(tmp_file)

            # 直接执行参数列表，避免资源路径中的特殊字符被命令解释器执行。
            result = subprocess.run(cmd, capture_output=True, text=True, shell=False, encoding='utf-8', errors='ignore')

            if result.returncode == 0 and os.path.exists(tmp_file):
                new_size = self.get_file_size(tmp_file)

                if new_size < original_size:
                    shutil.move(tmp_file, file_path)
                    self.logger.info(f"JPG压缩成功，文件变小，已覆盖原文件")
                    return new_size
                else:
                    os.remove(tmp_file)
                    self.logger.warning(f"JPG压缩后文件未变小，跳过覆盖")
            else:
                os.remove(tmp_file)
                self.logger.error(f"jpegoptim压缩失败: {result.stderr}")
        except ParameterValidationError as e:
            self.logger.error(f"jpegoptim参数验证失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"JPG压缩异常: {str(e)}")
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

        return original_size

class MozjpegTool(CompressionTool):
    """mozjpeg压缩工具实现"""

    def __init__(self, tool_path, logger=None, config=None):
        super().__init__(tool_path, logger)
        self.config = config

    def compress(self, file_path, **kwargs):
        """使用mozjpeg压缩JPG文件"""
        original_size = self.get_file_size(file_path)
        tmp_file = f"{file_path}.tmp"

        try:
            # 检查文件扩展名是否为JPG/JPEG
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in ['.jpg', '.jpeg']:
                self.logger.warning(f"mozjpeg只支持JPG/JPEG文件，跳过压缩: {file_path}")
                return original_size

            # 验证参数
            validated_params = self._validate_parameters(file_path, **kwargs)

            # 从验证后的参数获取值
            quality = validated_params.get('quality', 10)
            self.logger.info(f"使用质量: {quality}% 压缩JPG文件")

            # 构建mozjpeg命令，使用最激进的参数
            cmd = [
                self.tool_path,
                "-quality",
                f"{quality}",
                "-progressive",  # 渐进式压缩
                "-tune-ms-ssim",  # 优化SSIM质量
                "-quant-table",
                "3",  # 更激进的量化表
                "-dct",
                "float",  # 更高质量的DCT算法
                "-outfile",
                tmp_file,
                file_path
            ]

            # 确保临时文件目录存在
            tmp_dir = os.path.dirname(tmp_file)
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir, exist_ok=True)

            # 直接执行参数列表，避免资源路径中的特殊字符被命令解释器执行。
            result = subprocess.run(cmd, capture_output=True, text=True, shell=False, encoding='utf-8', errors='ignore')

            if result.returncode == 0 and os.path.exists(tmp_file):
                new_size = self.get_file_size(tmp_file)

                if new_size < original_size:
                    shutil.move(tmp_file, file_path)
                    self.logger.info(f"mozjpeg压缩成功，文件变小，已覆盖原文件")
                    return new_size
                else:
                    os.remove(tmp_file)
                    self.logger.warning(f"mozjpeg压缩后文件未变小，跳过覆盖")
            else:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
                self.logger.error(f"mozjpeg压缩失败: {result.stderr}")
        except ParameterValidationError as e:
            self.logger.error(f"mozjpeg参数验证失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"mozjpeg压缩异常: {str(e)}")
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

        return original_size

class ZopfliTool(CompressionTool):
    """zopfli压缩工具实现"""

    def __init__(self, tool_path, logger=None, config=None):
        super().__init__(tool_path, logger)
        self.config = config

    def compress(self, file_path, **kwargs):
        """使用zopflipng压缩PNG文件"""
        original_size = self.get_file_size(file_path)
        tmp_file = f"{file_path}.tmp"

        try:
            self.logger.info(f"使用zopflipng压缩PNG文件")

            # 检查文件扩展名是否为PNG
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext != '.png':
                self.logger.warning(f"zopflipng只支持PNG文件，跳过压缩: {file_path}")
                return original_size

            # 验证参数
            validated_params = self._validate_parameters(file_path, **kwargs)

            # 获取验证后的参数
            iterations = validated_params.get('iterations', 500)

            # 构建zopflipng命令，使用更简单和更稳定的参数
            cmd = [
                self.tool_path,
                f"--iterations={iterations}",  # 使用验证后的迭代次数
                "-y"  # 不询问是否覆盖文件
            ]

            # 处理其他参数
            lossy = validated_params.get('lossy', True)
            lossy_8bit = '--lossy_8bit' if validated_params.get('lossy_8bit', True) else ''
            lossy_transparent = '--lossy_transparent' if validated_params.get('lossy_transparent', True) else ''
            filters = validated_params.get('filters', '--filters=01234')

            # 添加有损压缩参数
            if lossy:
                if lossy_8bit:
                    cmd.append(lossy_8bit)
                if lossy_transparent:
                    cmd.append(lossy_transparent)

            # 添加过滤器参数
            cmd.append(filters)

            # 添加输入输出文件
            cmd.append(file_path)  # 输入文件
            cmd.append(tmp_file)  # 输出文件

            # 详细日志：记录完整命令
            self.logger.info(f"zopflipng命令: {' '.join(cmd)}")
            self.logger.info(f"zopflipng工具路径: {self.tool_path}")
            self.logger.info(f"zopflipng输入文件: {file_path}")
            self.logger.info(f"zopflipng输出文件: {tmp_file}")

            # 检查工具路径是否存在
            if not os.path.exists(self.tool_path):
                self.logger.error(f"zopflipng工具不存在: {self.tool_path}")
                return original_size

            # 检查工具是否可执行
            if not os.access(self.tool_path, os.X_OK):
                self.logger.error(f"zopflipng工具不可执行: {self.tool_path}")
                return original_size

            # 设置超时时间，避免长时间阻塞
            # 直接执行参数列表，避免资源路径中的特殊字符被命令解释器执行。
            result = subprocess.run(cmd, capture_output=True, text=True, shell=False, encoding='utf-8', errors='ignore', timeout=60)

            # 详细日志：记录执行结果
            self.logger.info(f"zopflipng返回码: {result.returncode}")
            if result.stdout:
                self.logger.info(f"zopflipng标准输出: {result.stdout}")
            if result.stderr:
                self.logger.info(f"zopflipng标准错误: {result.stderr}")

            # 检查zopflipng是否生成了压缩文件
            if os.path.exists(tmp_file):
                new_size = self.get_file_size(tmp_file)
                self.logger.info(f"zopflipng压缩后大小: {new_size} 字节")

                if new_size < original_size:
                    shutil.move(tmp_file, file_path)
                    self.logger.info(f"zopflipng压缩成功，文件变小，已覆盖原文件")
                    return new_size
                else:
                    os.remove(tmp_file)
                    self.logger.warning(f"zopflipng压缩后文件未变小，跳过覆盖")
            else:
                self.logger.error(f"zopflipng压缩失败，未生成输出文件 (错误码: {result.returncode})")
                if result.stderr:
                    self.logger.error(f"zopflipng错误详情: {result.stderr}")
        except ParameterValidationError as e:
            self.logger.error(f"zopflipng参数验证失败: {str(e)}")
        except subprocess.TimeoutExpired:
            self.logger.error(f"zopflipng压缩超时，已停止执行")
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
        except Exception as e:
            self.logger.error(f"zopflipng压缩异常: {str(e)}")
            import traceback
            self.logger.error(f"异常堆栈: {traceback.format_exc()}")
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

        return original_size

class LibImageQuantTool(CompressionTool):
    """libimagequant压缩工具实现"""

    def __init__(self, tool_path, logger=None, config=None):
        super().__init__(tool_path, logger)
        self.config = config
        # 导入libimagequant库
        try:
            import sys
            import os

            self.logger.info(f"尝试导入libimagequant库")

            # 检查是否是打包环境
            is_meipass = hasattr(sys, '_MEIPASS')
            if is_meipass:
                meipass_path = sys._MEIPASS
                self.logger.info(f"打包环境路径: {meipass_path}")

            # 获取项目根目录和tools目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(current_dir)
            project_root = os.path.dirname(src_dir)
            tools_modes_dir = os.path.join(project_root, 'tools', 'modes')

            # 简化导入逻辑，确保能正确处理打包环境和非打包环境
            # 1. 检查sys.path中是否已包含imagequant路径，如果没有则添加
            if is_meipass:
                # 打包环境下，imagequant目录应该直接在_MEIPASS下
                imagequant_path = os.path.join(meipass_path, 'imagequant')
                if imagequant_path not in sys.path:
                    sys.path.insert(0, imagequant_path)

                # 同时添加当前目录和modes目录到sys.path
                sys.path.insert(0, meipass_path)
                sys.path.insert(0, os.path.join(meipass_path, 'modes'))
            else:
                # 非打包环境下，imagequant目录在tools/modes下
                imagequant_path = os.path.join(tools_modes_dir, 'imagequant')
                if imagequant_path not in sys.path:
                    sys.path.insert(0, imagequant_path)

                # 添加tools/modes目录到sys.path
                if tools_modes_dir not in sys.path:
                    sys.path.insert(0, tools_modes_dir)

            # 直接尝试导入imagequant
            import imagequant
            self.imagequant = imagequant
            self.logger.info(f"成功导入libimagequant库")
        except ImportError as e:
            self.logger.error(f"导入imagequant模块失败: {str(e)}")
            self.logger.error(f"当前sys.path: {sys.path}")
            # 打印更详细的错误信息
            import traceback
            traceback.print_exc()

            # 如果是打包环境，检查imagequant目录结构
            if hasattr(sys, '_MEIPASS'):
                meipass_path = sys._MEIPASS
                self.logger.error(f"打包环境目录: {meipass_path}")

                # 检查是否存在imagequant目录
                imagequant_path = os.path.join(meipass_path, 'imagequant')
                if os.path.exists(imagequant_path):
                    self.logger.error(f"imagequant目录存在，内容: {os.listdir(imagequant_path)}")
                else:
                    self.logger.error(f"imagequant目录不存在")

                # 检查modes目录
                modes_path = os.path.join(meipass_path, 'modes')
                if os.path.exists(modes_path):
                    self.logger.error(f"modes目录存在，内容: {os.listdir(modes_path)}")

            self.imagequant = None
        except Exception as e:
            self.logger.error(f"导入libimagequant库失败: {str(e)}")
            import traceback
            traceback.print_exc()
            self.imagequant = None

    def compress(self, file_path, **kwargs):
        """使用libimagequant压缩PNG文件"""
        if self.imagequant is None:
            self.logger.error("libimagequant库未正确导入，跳过压缩")
            return self.get_file_size(file_path)

        original_size = self.get_file_size(file_path)
        tmp_file = f"{file_path}.tmp"

        try:
            self.logger.info(f"使用libimagequant压缩PNG文件")

            # 检查文件扩展名是否为PNG
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext != '.png':
                self.logger.warning(f"libimagequant只支持PNG文件，跳过压缩: {file_path}")
                return original_size

            # 验证参数
            validated_params = self._validate_parameters(file_path, **kwargs)

            # 打开并读取图像
            with Image.open(file_path) as img:
                # 获取验证后的参数
                quality = validated_params.get('quality', 15)
                # 优先使用用户设置的min/max_quality，否则根据quality动态计算
                min_quality = max(0, validated_params.get('min_quality', quality - 5))
                max_quality = min(100, validated_params.get('max_quality', quality + 5))
                dithering_level = validated_params.get('dithering_level', 0.3)
                max_colors = validated_params.get('max_colors', 128)

                # 确保max_colors在1-256之间（双重保障，因为已在参数验证中处理）
                max_colors = max(1, min(256, max_colors))
                # 确保抖动率在合理范围内（双重保障）
                dithering_level = max(0.1, min(1.0, dithering_level))

                self.logger.info(f"libimagequant参数 - 质量范围: {min_quality}-{max_quality}, 抖动级别: {dithering_level}, 最大颜色数: {max_colors}")

                # 量化图像
                quantized_img = self.imagequant.quantize_pil_image(
                    img,
                    dithering_level=dithering_level,
                    max_colors=max_colors,
                    min_quality=min_quality,
                    max_quality=max_quality
                )

                # 写入压缩后的PNG文件
                quantized_img.save(tmp_file, format='PNG', optimize=True)

                # 检查压缩结果
                if os.path.exists(tmp_file):
                    new_size = self.get_file_size(tmp_file)
                    self.logger.info(f"libimagequant压缩后大小: {new_size} 字节")

                    if new_size < original_size:
                        shutil.move(tmp_file, file_path)
                        self.logger.info(f"libimagequant压缩成功，文件变小，已覆盖原文件")
                        return new_size
                    else:
                        os.remove(tmp_file)
                        self.logger.warning(f"libimagequant压缩后文件未变小，跳过覆盖")
        except ParameterValidationError as e:
            self.logger.error(f"libimagequant参数验证失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"libimagequant压缩异常: {str(e)}")
            import traceback
            traceback.print_exc()
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

        return original_size

class FFmpegTool(CompressionTool):
    """ffmpeg音频压缩工具实现"""

    def __init__(self, tool_path, logger=None):
        super().__init__(tool_path, logger)

    def compress(self, file_path, **kwargs):
        """使用ffmpeg压缩音频文件"""
        original_size = self.get_file_size(file_path)

        # 获取文件扩展名和文件名
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(file_name)[0]
        ext = os.path.splitext(file_path)[1].lower()

        # 创建带有原始扩展名的临时文件，确保ffmpeg能识别输出格式
        tmp_file = os.path.join(file_dir, f"{name_without_ext}_tmp{ext}")

        try:
            self.logger.info(f"使用ffmpeg压缩音频文件")

            # 验证参数
            validated_params = self._validate_parameters(file_path, **kwargs)

            # 获取验证后的参数
            bitrate = validated_params.get('bitrate', 32)

            # 构建ffmpeg命令
            cmd = [
                self.tool_path,
                "-i", file_path,
                "-y",  # 覆盖输出文件
                "-b:a", f"{bitrate}k",  # 使用验证后的比特率
            ]

            # 根据不同音频格式设置编码器
            if ext == '.mp3':
                # MP3格式使用libmp3lame编码器
                cmd.extend([
                    "-codec:a", "libmp3lame",
                ])
            elif ext == '.wav':
                # WAV格式使用libmp3lame编码器，保持WAV格式
                cmd.extend([
                    "-codec:a", "libmp3lame",
                    "-f", "wav",  # 保持WAV格式
                ])
            elif ext in ['.ogg', '.oga']:
                # OGG格式使用libvorbis编码器
                cmd.extend([
                    "-codec:a", "libvorbis",
                ])
            elif ext == '.flac':
                # FLAC格式使用flac编码器
                cmd.extend([
                    "-codec:a", "flac",
                ])
            elif ext in ['.aac', '.m4a']:
                # AAC格式使用aac编码器
                cmd.extend([
                    "-codec:a", "aac",
                ])
            else:
                # 默认使用libmp3lame编码器
                cmd.extend([
                    "-codec:a", "libmp3lame",
                ])

            # 添加输出文件，使用带有原始扩展名的临时文件
            cmd.append(tmp_file)

            # 直接执行参数列表，避免资源路径中的特殊字符被命令解释器执行。
            result = subprocess.run(cmd, capture_output=True, text=True, shell=False, encoding='utf-8', errors='ignore')

            if result.returncode == 0 and os.path.exists(tmp_file):
                new_size = self.get_file_size(tmp_file)
                self.logger.info(f"ffmpeg压缩后大小: {new_size} 字节")

                if new_size < original_size:
                    # 原位置替换，保持原扩展名
                    shutil.move(tmp_file, file_path)
                    self.logger.info(f"音频压缩成功，文件变小，已覆盖原文件")
                    return new_size
                else:
                    os.remove(tmp_file)
                    self.logger.warning(f"ffmpeg压缩后文件未变小，跳过覆盖")
            else:
                self.logger.error(f"ffmpeg压缩失败: {result.stderr}")
        except ParameterValidationError as e:
            self.logger.error(f"ffmpeg参数验证失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"ffmpeg压缩异常: {str(e)}")
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

        return original_size

class ToolsManager:
    """压缩工具管理器"""

    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger or Logger()
        self.tools = {}

    def get_tool(self, tool_type, tool_name):
        """获取压缩工具实例"""
        key = f"{tool_type}_{tool_name}"

        if key not in self.tools:
            tool = self._create_tool(tool_type, tool_name)
            self.tools[key] = tool

        return self.tools[key]

    def _create_tool(self, tool_type, tool_name):
        """创建压缩工具实例"""
        # 对于libimagequant，不需要实际的工具路径，因为它是通过Python库调用的
        if tool_name == "libimagequant":
            if tool_type == "png":
                return LibImageQuantTool("", self.logger, self.config)

        tool_path = self.config.get_tool_path(tool_name)

        if not os.path.exists(tool_path):
            self.logger.error(f"压缩工具不存在: {tool_path}")
            raise FileNotFoundError(f"压缩工具不存在: {tool_path}")

        if tool_type == "png":
            if tool_name == "pngquant":
                return PNGQuantTool(tool_path, self.logger)
            elif tool_name == "oxipng":
                return OxipngTool(tool_path, self.logger)
            elif tool_name == "zopfli" or tool_name == "zopflipng":
                return ZopfliTool(tool_path, self.logger, self.config)
            elif tool_name == "libimagequant":
                return LibImageQuantTool(tool_path, self.logger, self.config)
        elif tool_type == "jpg":
            if tool_name == "jpegoptim":
                return JpegoptimTool(tool_path, self.logger)
            elif tool_name == "mozjpeg":
                return MozjpegTool(tool_path, self.logger)
        elif tool_type == "audio":
            if tool_name == "ffmpeg":
                return FFmpegTool(tool_path, self.logger)

        raise ValueError(f"不支持的压缩工具类型或名称: {tool_type}_{tool_name}")
