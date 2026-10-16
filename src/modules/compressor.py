"""压缩核心模块

该模块负责图片压缩工具的核心压缩逻辑，包括：
- PNG文件压缩
- JPG文件压缩
- 文件扫描和处理
- 压缩统计信息
"""

import os
from .logger import Logger
from .config import Config
from .tools_manager import ToolsManager
from .strategies import STRATEGIES, STRATEGY_CONFIGS

class ImageCompressor:
    """图片压缩器类，负责处理图片压缩的核心逻辑"""

    def __init__(self, logger=None, config=None, strategy_name='speed'):
        """初始化图片压缩器
        
        Args:
            logger (Logger, optional): 日志记录器实例，默认为None
            config (Config, optional): 配置实例，默认为None
            strategy_name (str, optional): 压缩策略名称，默认为'speed'
        """
        self.config = config or Config()
        self.logger = logger or Logger()
        self.tools_manager = ToolsManager(self.config, self.logger)
        self.is_running = False
        self.total_files = 0
        self.processed_files = 0
        self.success_count = 0  # 成功压缩的文件数
        self.failed_count = 0   # 压缩失败的文件数
        self.png_count = 0
        self.jpg_count = 0
        self.audio_count = 0    # 音频文件数
        self.total_original_size = 0  # 总原始大小
        self.total_saved_bytes = 0
        self.current_file = ""
        # 策略管理
        self.current_strategy_name = strategy_name
        self.strategy_parameters = {}
        self.current_strategy = self._create_strategy(strategy_name)
        self.logger.info(f"初始化压缩策略: {self.current_strategy.get_name()}")

    def get_file_size(self, file_path):
        """获取文件大小"""
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0

    def _create_strategy(self, strategy_name):
        """创建策略实例
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            CompressionStrategy: 策略实例
        """
        params = self.strategy_parameters.get(strategy_name, {})
        if strategy_name in STRATEGIES:
            return STRATEGIES[strategy_name](self.config, self.logger, params)
        else:
            raise ValueError(f"ImageCompressor：未知压缩策略 {strategy_name}")

    def set_strategy(self, strategy_name):
        """切换压缩策略
        
        Args:
            strategy_name: 策略名称
        """
        if strategy_name != self.current_strategy_name:
            self.current_strategy_name = strategy_name
            self.current_strategy = self._create_strategy(strategy_name)
            self.logger.info(f"切换压缩策略: {self.current_strategy.get_name()}")
            return True
        return False

    def set_strategy_parameters(self, strategy_name, params):
        """设置策略参数
        
        Args:
            strategy_name: 策略名称
            params: 策略参数字典
        """
        self.strategy_parameters[strategy_name] = params
        self.logger.info(f"更新策略参数: {strategy_name}, 参数: {params}")

        # 如果当前策略就是目标策略，重新创建策略实例以应用新参数
        if strategy_name == self.current_strategy_name:
            self.current_strategy = self._create_strategy(strategy_name)
            self.logger.info(f"已应用新参数到当前策略: {self.current_strategy.get_name()}")
        return True

    def get_current_strategy(self):
        """获取当前压缩策略"""
        return self.current_strategy

    def get_strategy_config(self, strategy_name=None):
        """获取策略配置信息
        
        Args:
            strategy_name: 策略名称，默认为当前策略
            
        Returns:
            dict: 策略配置信息
        """
        if strategy_name is None:
            strategy_name = self.current_strategy_name
        return STRATEGY_CONFIGS.get(strategy_name, {})


    def scan_files(self, root_dir, compress_audio=False):
        """扫描所有支持的图片文件和音频文件
        
        Args:
            root_dir (str): 根目录路径
            compress_audio (bool, optional): 是否扫描音频文件，默认为False
        
        Returns:
            list: 扫描到的文件路径列表
        """
        files_to_process = []

        for root, dirs, files in os.walk(root_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.config.supported_formats:
                    # 图片文件
                    full_path = os.path.join(root, file)
                    files_to_process.append(full_path)
                elif compress_audio and ext in self.config.supported_audio_formats:
                    # 音频文件
                    full_path = os.path.join(root, file)
                    files_to_process.append(full_path)

        return files_to_process

    def compress_images(self, path, progress_callback=None, compress_audio=False):
        """压缩图片，可以是单个文件或目录，支持音频压缩选项
        
        Args:
            path (str): 图片文件或目录路径
            progress_callback (callable, optional): 进度回调函数
            compress_audio (bool, optional): 是否压缩音频文件，默认为False
        """
        self.is_running = True
        self.total_files = 0
        self.processed_files = 0
        self.png_count = 0
        self.jpg_count = 0
        self.audio_count = 0
        self.other_count = 0
        self.total_original_size = 0  # 重置总原始大小
        self.total_saved_bytes = 0
        self.success_count = 0
        self.failed_count = 0

        # 检查路径是否存在
        if not os.path.exists(path):
            self.logger.error(f"路径不存在: {path}")
            self.is_running = False
            return False

        # 调用进度回调，初始化进度
        if progress_callback:
            progress_callback(0)

        # 确定是单个文件还是目录
        if os.path.isfile(path):
            # 单个文件
            ext = os.path.splitext(path)[1].lower()
            if ext not in self.config.supported_formats:
                if compress_audio and ext in self.config.supported_audio_formats:
                    # 单个音频文件
                    files_to_process = [path]
                    self.total_files = 1
                    self.logger.info(f"开始压缩单个音频文件: {path}")
                else:
                    self.logger.error(f"文件 {path} 不是支持的图片格式")
                    self.is_running = False
                    return False
            else:
                # 单个图片文件
                files_to_process = [path]
                self.total_files = 1
                self.logger.info(f"开始压缩单个图片文件: {path}")
        else:
            # 目录 - 扫描图片文件和音频文件
            files_to_process = self.scan_files(path, compress_audio)
            self.total_files = len(files_to_process)

            if self.total_files == 0:
                self.logger.warning(f"在目录 {path} 中未找到支持的图片文件")
                self.is_running = False
                return True

            self.logger.info(f"共找到 {self.total_files} 个文件")

        # 调用进度回调，扫描完成，开始压缩
        if progress_callback:
            progress_callback(5)

        # 开始压缩
        for file_path in files_to_process:
            if not self.is_running:
                break

            self.current_file = file_path
            ext = os.path.splitext(file_path)[1].lower()
            original_size = self.get_file_size(file_path)

            # 检查文件大小，小于0.5kb的文件直接跳过
            if original_size < 512:
                self.logger.info(f"✓ {os.path.basename(file_path)} - 文件太小 (< 0.5KB)，直接跳过")
                self.processed_files += 1
                self.success_count += 1

                # 调用进度回调，更新进度
                if progress_callback:
                    progress = int((self.processed_files / self.total_files) * 90) + 5  # 5%-95%
                    progress_callback(progress, file_path)
                continue

            self.total_original_size += original_size  # 累加总原始大小

            # 调用进度回调，更新当前处理的文件名
            if progress_callback:
                progress = int((self.processed_files / self.total_files) * 90) + 5  # 5%-95%
                progress_callback(progress, file_path)

            try:
                # 确定文件类型
                if ext == '.png' or ext in ['.jpg', '.jpeg']:
                    # 直接使用用户选择的策略
                    self.logger.info(f"✓ {os.path.basename(file_path)} - 使用用户选择的策略: {self.current_strategy_name}")

                    # 使用选定的策略压缩图片
                    original_size, final_size = self.current_strategy.compress(file_path)

                    if ext == '.png':
                        self.png_count += 1
                    elif ext in ['.jpg', '.jpeg']:
                        self.jpg_count += 1
                elif compress_audio and ext in self.config.supported_audio_formats:
                    # 音频文件使用原有的压缩方法
                    original_size, final_size = self.compress_audio(file_path)
                    self.audio_count += 1
                else:
                    # 其他图片类型，尝试使用当前策略压缩
                    original_size, final_size = self.current_strategy.compress(file_path)
                    self.other_count += 1

                # 统计节省空间
                saved_bytes = original_size - final_size
                if saved_bytes > 0:
                    self.total_saved_bytes += saved_bytes
                    self.success_count += 1
                    self.logger.info(f"✓ {os.path.basename(file_path)} - 节省: {saved_bytes} 字节")
                else:
                    self.failed_count += 1
                    self.logger.warning(f"✗ {os.path.basename(file_path)} - 未节省空间")
            except Exception as e:
                self.failed_count += 1
                self.logger.error(f"✗ {os.path.basename(file_path)} - 压缩失败: {str(e)}")

            self.processed_files += 1

            # 调用进度回调，更新进度
            if progress_callback:
                progress = int((self.processed_files / self.total_files) * 90) + 5  # 5%-95%
                progress_callback(progress, file_path)

        # 调用进度回调，压缩完成
        if progress_callback:
            progress_callback(100)

        self.is_running = False
        self.current_file = ""
        return True

    def compress_audio(self, file_path):
        """压缩音频文件"""
        original_size = self.get_file_size(file_path)
        final_size = original_size

        try:
            # 获取ffmpeg工具实例
            tool = self.tools_manager.get_tool('audio', 'ffmpeg')

            # 执行音频压缩
            new_size = tool.compress(file_path)

            # 更新最终大小
            if new_size < final_size:
                final_size = new_size
        except Exception as e:
            self.logger.error(f"使用 ffmpeg 压缩音频文件失败: {str(e)}")

        return original_size, final_size


    def stop_compression(self):
        """停止压缩"""
        self.is_running = False
        self.logger.info("压缩已停止")

    def get_statistics(self):
        """获取压缩统计信息"""
        return {
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'png_count': self.png_count,
            'jpg_count': self.jpg_count,
            'audio_count': self.audio_count,
            'other_count': self.other_count,
            'total_original_size': self.total_original_size,
            'total_saved_bytes': self.total_saved_bytes
        }

    def bytes_to_readable(self, bytes_size):
        """将字节大小转换为可读格式"""
        if bytes_size < 1024:
            return f"{bytes_size} 字节"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.2f} KB"
        elif bytes_size < 1024 * 1024 * 1024:
            return f"{bytes_size / (1024 * 1024):.2f} MB"
        else:
            return f"{bytes_size / (1024 * 1024 * 1024):.2f} GB"
