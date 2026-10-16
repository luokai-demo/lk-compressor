"""
极致压缩策略参数配置 (Compression Strategy Config)
独立配置文件，与其他策略完全隔离。
用于 ParameterDialog 的默认值加载。
"""

COMPRESSION_STRATEGY_DEFAULTS = {
    'libimagequant_quality': 15,               # 质量0-100
    'libimagequant_dithering_level': 30,       # 抖动率0-100
    'libimagequant_max_colors': 128,           # 最大色彩数1-256
    'pngquant_quality': 15,                    # 质量0-100
    'oxipng_level': 6,                         # 级别0-6
    'zopflipng_enabled': False,                # 是否启用zopflipng (耗时操作)
    'zopflipng_iterations': 15,                # 迭代次数 (默认15，平衡速度)
    'mozjpeg_quality': 25,                     # 质量0-100
    'jpegoptim_level': 3                       # 级别0-3
}
