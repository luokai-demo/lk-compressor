"""
常规压缩策略参数配置 (Speed Strategy Config)
独立配置文件，与其他策略完全隔离。
"""

SPEED_STRATEGY_DEFAULTS = {
    'pngquant_quality': 80,    # 质量 80 (平衡体积与画质)
    'pngquant_speed': 3,       # 速度 3 (平衡速度与质量)
    'oxipng_level': 3,         # 级别 3 (快速优化)
    'mozjpeg_quality': 85      # 质量 85 (JPEG黄金质量点)
}
