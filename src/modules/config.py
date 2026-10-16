"""配置管理模块

该模块负责管理图片压缩工具的配置信息，包括：
- 工具路径配置
- 压缩策略配置
- 支持的文件格式
"""

import os
import sys
from datetime import datetime

class Config:
    """配置类，管理压缩工具的配置信息"""
    
    def __init__(self):
        # 处理PyInstaller打包后的情况
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件路径
            self.root_dir = os.path.dirname(os.path.abspath(sys.executable))
            # 处理PyInstaller打包后的资源路径
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller打包后，所有资源会被解压到_MEIPASS目录
                self.tools_dir = os.path.join(sys._MEIPASS, 'modes')
            else:
                # 备用方案，使用可执行文件所在目录的modes子目录
                self.tools_dir = os.path.join(self.root_dir, 'modes')
        else:
            # 直接运行Python脚本的情况
            self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # 直接运行时的工具目录
            self.tools_dir = os.path.join(os.path.dirname(self.root_dir), 'tools', 'modes')
        
        # 默认图片目录 - 不设置默认路径，用户需要手动选择
        self.default_image_dir = ""
        
        # 默认策略
        self.default_strategy = 'speed'
        
        # 当前选择的策略
        self.current_strategy = self.default_strategy
        
        # 启动提示配置
        self.startup_warning = {
            'show': True,  # 是否显示启动提示
            'config_file': os.path.join(self.root_dir, 'startup_warning_config.json')
        }
        
        # 加载启动提示配置
        self._load_startup_warning_config()
        
        # 压缩工具配置
        self.tools_config = {
            'pngquant': {
                'path': os.path.join(self.tools_dir, 'pngquant.exe'),
                'type': 'png',
                'description': 'PNG有损压缩工具',
                'compatible_types': ['png']
            },
            'oxipng': {
                'path': os.path.join(self.tools_dir, 'oxipng.exe'),
                'type': 'png',
                'description': 'PNG无损优化工具',
                'compatible_types': ['png']
            },
            'zopflipng': {
                'path': os.path.join(self.tools_dir, 'zopflipng.exe'),
                'type': 'png',
                'description': 'PNG专用无损压缩工具（基于zopfli算法，针对PNG优化）',
                'compatible_types': ['png']
            },
            'libimagequant': {
                'path': '',  # 不需要实际路径，因为是Python库
                'type': 'png',
                'description': 'PNG图像量化库（Squoosh使用的算法）',
                'compatible_types': ['png']
            },
            'jpegoptim': {
                'path': os.path.join(self.tools_dir, 'jpegoptim.exe'),
                'type': 'jpg',
                'description': 'JPG压缩工具',
                'compatible_types': ['jpg', 'jpeg']
            },
            'mozjpeg': {
                'path': os.path.join(self.tools_dir, 'cjpeg-static.exe'),
                'type': 'jpg',
                'description': 'JPG压缩工具（高压缩率）',
                'compatible_types': ['jpg', 'jpeg']
            },
            'zopfli': {
                'path': os.path.join(self.tools_dir, 'zopfli.exe'),
                'type': 'general',
                'description': '通用无损压缩工具（基于zopfli算法）',
                'compatible_types': ['png', 'jpg', 'jpeg']
            },
            'ffmpeg': {
                'path': os.path.join(self.tools_dir, 'ffmpeg', 'ffmpeg-7.0.2-essentials_build', 'bin', 'ffmpeg.exe'),
                'type': 'audio',
                'description': '音频压缩工具',
                'compatible_types': ['mp3', 'wav', 'ogg', 'flac', 'aac', 'wma', 'm4a']
            }
        }
        
        # 支持的图片格式
        self.supported_formats = ['.png', '.jpg', '.jpeg']
        
        # 支持的音频格式
        self.supported_audio_formats = ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.wma', '.m4a']
        
        
    
    def validate_tools(self):
        """验证压缩工具是否存在"""
        missing_tools = []
        
        # 验证所有工具，跳过libimagequant，因为它是Python库
        for tool_name, tool_info in self.tools_config.items():
            # 跳过libimagequant，因为它是Python库，不需要实际路径
            if tool_name == 'libimagequant':
                continue
            
            tool_path = tool_info['path']
            if not os.path.exists(tool_path):
                missing_tools.append(tool_name + '.exe')
        
        return missing_tools
    
    def get_tool_path(self, tool_name):
        """获取指定工具的路径"""
        if tool_name in self.tools_config:
            return self.tools_config[tool_name]['path']
        return None
    
    def get_tool_type(self, tool_name):
        """获取指定工具的类型"""
        if tool_name in self.tools_config:
            return self.tools_config[tool_name]['type']
        return None
    
    def set_current_strategy(self, strategy_name):
        """设置当前策略"""
        self.current_strategy = strategy_name
    
    def get_current_strategy(self):
        """获取当前策略"""
        return self.current_strategy
    
    def get_all_tools(self):
        """获取所有配置的压缩工具"""
        return list(self.tools_config.keys())
    
    def get_tools_by_type(self, tool_type):
        """获取指定类型的所有压缩工具"""
        return [tool_name for tool_name, tool_info in self.tools_config.items() if tool_info['type'] == tool_type]
    
    def get_tool_info(self, tool_name):
        """获取工具详细信息"""
        return self.tools_config.get(tool_name, {})
    
    def _load_startup_warning_config(self):
        """加载启动提示配置"""
        try:
            if os.path.exists(self.startup_warning['config_file']):
                import json
                with open(self.startup_warning['config_file'], 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.startup_warning['show'] = config.get('show', True)
        except Exception as e:
            # 如果加载失败，使用默认值
            self.startup_warning['show'] = True
            import logging
            logging.error(f"加载启动提示配置失败: {str(e)}")
    
    def save_startup_warning_config(self, show_warning):
        """保存启动提示配置"""
        try:
            import json
            config = {
                'show': show_warning,
                'last_updated': str(datetime.now())
            }
            with open(self.startup_warning['config_file'], 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.startup_warning['show'] = show_warning
        except Exception as e:
            import logging
            logging.error(f"保存启动提示配置失败: {str(e)}")
    
    def should_show_startup_warning(self):
        """检查是否应该显示启动提示"""
        return self.startup_warning['show']
