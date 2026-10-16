# 压缩策略模块

from .base import CompressionStrategy
from .speed import SpeedPriorityStrategy
from .compression import CompressionPriorityStrategy

# 策略映射表
STRATEGIES = {
    'speed': SpeedPriorityStrategy,
    'compression': CompressionPriorityStrategy
}

# 策略配置信息
STRATEGY_CONFIGS = {
    'speed': {
        'name': '常规压缩',
        'icon': '⚡',
        'description': '视觉无损，高质量有损压缩，肉眼不易察觉差异',
        'tools': ['pngquant(质量80)', 'oxipng(级别3)', 'mozjpeg(质量85)'],
        'performance': {
            'compression_rate': '96%',
            'speed': '0.1-0.3秒/MB'
        },
        'recommended_types': ['大量图片', '快速预览', '临时压缩'],
        'use_cases': ['批量处理', '实时压缩', '移动端应用']
    },
    'compression': {
        'name': '极致压缩策略',
        'icon': '📦',
        'description': '实现最大化压缩效果的同时提升处理效率，建立压缩质量与文件大小的动态平衡机制',
        'tools': ['libimagequant(质量10-25)', 'pngquant(质量10-25)', 'oxipng(级别6)', 'zopflipng(迭代500)', 'mozjpeg(质量20-30)', 'jpegoptim(质量20)'],
        'performance': {
            'compression_rate': '96%',
            'speed': '1.0-2.0秒/MB'
        },
        'recommended_types': ['需要高压缩率的图片', '存储空间有限场景'],
        'use_cases': ['云存储', '网络传输', '资源受限设备']
    }
}
