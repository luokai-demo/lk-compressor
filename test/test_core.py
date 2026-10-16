"""覆盖核心参数边界和用户配置持久化，不读取本机素材。"""

from pathlib import Path
import tempfile
import unittest

from src.modules.config import Config
from src.modules.parameter import ToolParameter, ParameterValidationError


class ParameterTest(unittest.TestCase):
    """验证参数范围和非法输入会明确报错。"""

    def test_quality_boundaries_are_accepted(self):
        """质量最小值和最大值均可通过验证。"""
        for quality in (0, 100):
            # 当前边界质量值。
            with self.subTest(quality=quality):
                ToolParameter('quality', quality, int, min_value=0, max_value=100).validate()

    def test_outside_quality_range_is_rejected(self):
        """越界质量不得传给外部工具。"""
        for quality in (-1, 101):
            # 当前非法质量值。
            with self.subTest(quality=quality), self.assertRaises(ParameterValidationError):
                ToolParameter('quality', quality, int, min_value=0, max_value=100).validate()

    def test_missing_required_value_is_rejected(self):
        """必填参数缺失时应报告参数错误。"""
        with self.assertRaises(ParameterValidationError):
            ToolParameter('quality', required=True).validate()

    def test_invalid_number_is_rejected(self):
        """不可转换的数值不能静默使用默认值。"""
        with self.assertRaises(ParameterValidationError):
            ToolParameter('quality', 'invalid', int).validate()


class ConfigTest(unittest.TestCase):
    """用户选择和启动设置不依赖开发者本机目录。"""

    def test_input_directory_is_not_preselected(self):
        """新配置不携带开发者的资源目录。"""
        self.assertEqual(Config().default_image_dir, '')

    def test_startup_preference_roundtrip(self):
        """在隔离目录写入用户设置后能够重新读取。"""
        with tempfile.TemporaryDirectory() as directory:
            # 使用临时文件替代真实用户设置路径。
            config = Config()
            config.startup_warning['config_file'] = str(Path(directory) / 'startup.json')
            config.save_startup_warning_config(False)
            config.startup_warning['show'] = True
            config._load_startup_warning_config()
            self.assertFalse(config.should_show_startup_warning())
