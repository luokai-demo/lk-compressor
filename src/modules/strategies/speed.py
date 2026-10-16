# 速度优先策略实现

from .base import CompressionStrategy
from .config_speed import SPEED_STRATEGY_DEFAULTS

class SpeedPriorityStrategy(CompressionStrategy):
    """常规压缩：以最快处理速度为核心目标"""
    
    def __init__(self, config, logger=None, params=None):
        """初始化常规压缩"""
        super().__init__(config, logger, params)
        self.name = "常规压缩"
        self.icon = "⚡"
        self.description = "视觉无损，高质量有损压缩，肉眼不易察觉差异"
        
        # 加载默认参数
        self.default_params = SPEED_STRATEGY_DEFAULTS.copy()
        
        # 合并用户参数和默认参数
        self.params = self.default_params.copy()
        if params:
            self.params.update(params)
            
        self.tools = [
            f'pngquant(质量{self.params["pngquant_quality"]})', 
            f'oxipng(级别{self.params["oxipng_level"]})', 
            f'mozjpeg(质量{self.params["mozjpeg_quality"]})'
        ]
        self.performance = {
            'compression_rate': '96%',
            'speed': '0.1-0.3秒/MB'
        }
        self.recommended_types = ['大量图片', '快速预览', '临时压缩']
        self.use_cases = ['批量处理', '实时压缩', '移动端应用']
    
    def compress(self, file_path):
        """使用常规压缩策略压缩文件"""
        original_size = self.get_file_size(file_path)
        final_size = original_size
        ext = file_path.lower().split('.')[-1]
        
        if ext == 'png':
            final_size = self._compress_png(file_path, original_size)
        elif ext in ['jpg', 'jpeg']:
            final_size = self._compress_jpg(file_path, original_size)
        
        return original_size, final_size
    
    def _compress_png(self, file_path, original_size):
        """压缩PNG文件"""
        final_size = original_size
        
        # 1. 使用pngquant进行有损压缩（视觉无损）
        try:
            tool = self.tools_manager.get_tool('png', 'pngquant')
            new_size = tool.compress(
                file_path, 
                quality=self.params['pngquant_quality'],
                speed=self.params['pngquant_speed']
            )
            if new_size < final_size:
                final_size = new_size
        except Exception as e:
            self.logger.error(f"pngquant压缩失败: {str(e)}")
        
        # 2. 使用oxipng进行快速优化
        try:
            tool = self.tools_manager.get_tool('png', 'oxipng')
            new_size = tool.compress(
                file_path,
                level=self.params['oxipng_level']
            )
            if new_size < final_size:
                final_size = new_size
        except Exception as e:
            self.logger.error(f"oxipng压缩失败: {str(e)}")
        
        return final_size
    
    def _compress_jpg(self, file_path, original_size):
        """压缩JPG文件"""
        final_size = original_size
        
        # 使用mozjpeg进行有损压缩（视觉无损）
        try:
            tool = self.tools_manager.get_tool('jpg', 'mozjpeg')
            new_size = tool.compress(
                file_path,
                quality=self.params['mozjpeg_quality']
            )
            if new_size < final_size:
                final_size = new_size
        except Exception as e:
            self.logger.error(f"mozjpeg压缩失败: {str(e)}")
        
        return final_size
