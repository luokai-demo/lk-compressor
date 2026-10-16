# 压缩率优先策略实现

from .base import CompressionStrategy
from .config_compression import COMPRESSION_STRATEGY_DEFAULTS

class CompressionPriorityStrategy(CompressionStrategy):
    """极致压缩策略：实现最大化压缩效果"""

    def __init__(self, config, logger=None, params=None):
        """初始化极致压缩策略"""
        super().__init__(config, logger)
        self.name = "极致压缩策略"
        self.icon = "📦"
        self.description = "实现最大化压缩效果的同时提升处理效率，建立压缩质量与文件大小的动态平衡机制"

        # 默认参数设置
        self.default_params = COMPRESSION_STRATEGY_DEFAULTS.copy()

        # 合并用户参数和默认参数
        self.params = self.default_params.copy()
        if params:
            self.params.update(params)

        # 更新工具列表显示
        self.tools = [
            f'libimagequant(质量{self.params["libimagequant_quality"]})',
            f'pngquant(质量{self.params["pngquant_quality"]})',
            f'oxipng(级别{self.params["oxipng_level"]})',
            f'zopflipng(迭代{self.params["zopflipng_iterations"]})'
        ]

        self.performance = {
            'compression_rate': '96%',
            'speed': '1.0-2.0秒/MB'
        }
        self.recommended_types = ['需要高压缩率的图片', '存储空间有限场景']
        self.use_cases = ['云存储', '网络传输', '资源受限设备']

    def compress(self, file_path):
        """使用极致压缩策略压缩文件"""
        original_size = self.get_file_size(file_path)
        final_size = original_size
        ext = file_path.lower().split('.')[-1]

        if ext == 'png':
            final_size = self._compress_png(file_path, original_size)
        elif ext in ['jpg', 'jpeg']:
            final_size = self._compress_jpg(file_path, original_size)

        return original_size, final_size

    def _compress_png(self, file_path, original_size):
        """使用多工具级联处理压缩PNG文件，优化压缩率至96%+"""
        final_size = original_size

        # 1. 使用libimagequant进行极致有损压缩（Squoosh使用的算法）
        try:
            # 构建参数字典，使用用户设置的参数
            libimagequant_params = {
                'quality': self.params['libimagequant_quality'],
                'dithering_level': self.params['libimagequant_dithering_level'] / 100.0,  # 转换为0.0-1.0范围
                'max_colors': self.params['libimagequant_max_colors']
            }
            # 使用ToolInvoker调用工具
            new_size = self.tool_invoker.invoke_tool(
                tool_type='png',
                tool_name='libimagequant',
                file_path=file_path,
                params_dict=libimagequant_params
            )
            if new_size < final_size:
                final_size = new_size
                self.logger.info(f"libimagequant极致压缩成功，大小: {final_size} 字节")
        except Exception as e:
            self.logger.warning(f"libimagequant压缩失败，跳过该工具: {str(e)}")

        # 2. 使用pngquant进行极致有损压缩
        try:
            # 构建参数字典
            pngquant_params = {
                'quality': self.params['pngquant_quality']
            }
            # 使用ToolInvoker调用工具
            new_size = self.tool_invoker.invoke_tool(
                tool_type='png',
                tool_name='pngquant',
                file_path=file_path,
                params_dict=pngquant_params
            )
            if new_size < final_size:
                final_size = new_size
                self.logger.info(f"pngquant激进压缩成功，大小: {final_size} 字节")
        except Exception as e:
            self.logger.warning(f"pngquant压缩失败，跳过该工具: {str(e)}")

        # 3. 使用oxipng进行高级优化
        try:
            # 构建参数字典
            oxipng_params = {
                'level': self.params['oxipng_level']
            }
            # 使用ToolInvoker调用工具
            new_size = self.tool_invoker.invoke_tool(
                tool_type='png',
                tool_name='oxipng',
                file_path=file_path,
                params_dict=oxipng_params
            )
            if new_size < final_size:
                final_size = new_size
        except Exception as e:
            self.logger.warning(f"oxipng压缩失败，跳过该工具: {str(e)}")

        # 4. 使用zopflipng进行极致优化 (可选)
        if self.params.get('zopflipng_enabled', False):
            try:
                # 构建参数字典，使用更稳定的过滤器设置
                zopflipng_params = {
                    'iterations': self.params['zopflipng_iterations'],
                    'lossy': True,
                    'lossy_8bit': True,
                    'lossy_transparent': True,
                    'filters': '--filters=01234'
                }
                # 使用ToolInvoker调用工具
                new_size = self.tool_invoker.invoke_tool(
                    tool_type='png',
                    tool_name='zopflipng',
                    file_path=file_path,
                    params_dict=zopflipng_params
                )
                if new_size < final_size:
                    final_size = new_size
                    self.logger.info(f"zopflipng极致压缩成功，大小: {final_size} 字节")
            except Exception as e:
                self.logger.warning(f"zopflipng压缩失败，跳过该工具: {str(e)}")
        else:
            self.logger.info("zopflipng未启用，跳过该步骤")

        return final_size

    def _compress_jpg(self, file_path, original_size):
        """压缩JPG文件，使用极致压缩参数"""
        final_size = original_size

        # 1. 使用mozjpeg进行极致压缩
        try:
            # 构建参数字典
            mozjpeg_params = {
                'quality': self.params['mozjpeg_quality']
            }
            # 使用ToolInvoker调用工具
            new_size = self.tool_invoker.invoke_tool(
                tool_type='jpg',
                tool_name='mozjpeg',
                file_path=file_path,
                params_dict=mozjpeg_params
            )
            if new_size < final_size:
                final_size = new_size
                self.logger.info(f"mozjpeg极致压缩成功，大小: {final_size} 字节")
        except Exception as e:
            self.logger.warning(f"mozjpeg压缩失败，跳过该工具: {str(e)}")

        # 2. 使用jpegoptim进行二次优化
        try:
            # 构建参数字典
            jpegoptim_params = {
                'quality': self.params['mozjpeg_quality']
            }
            # 使用ToolInvoker调用工具
            new_size = self.tool_invoker.invoke_tool(
                tool_type='jpg',
                tool_name='jpegoptim',
                file_path=file_path,
                params_dict=jpegoptim_params
            )
            if new_size < final_size:
                final_size = new_size
                self.logger.info(f"jpegoptim二次优化成功，大小: {final_size} 字节")
        except Exception as e:
            self.logger.warning(f"jpegoptim压缩失败，跳过该工具: {str(e)}")

        return final_size
