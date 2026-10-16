# 压缩策略基类

from abc import ABC, abstractmethod
from ..tools_manager import ToolsManager
from ..tool_invoker import ToolInvoker
from ..logger import Logger

class CompressionStrategy(ABC):
    """压缩策略抽象基类
    
    所有具体压缩策略都必须继承此类并实现抽象方法
    """

    def __init__(self, config, logger=None, params=None):
        """初始化压缩策略
        
        Args:
            config: 配置对象
            logger: 日志对象
            params: 策略参数字典
        """
        self.config = config
        self.logger = logger or Logger()
        self.tools_manager = ToolsManager(config, logger)
        self.tool_invoker = ToolInvoker(self.tools_manager, logger)
        self.params = params or {}
        self.name = """策略名称"""
        self.icon = """策略图标"""
        self.description = """策略描述"""
        self.tools = []  # 使用的工具列表
        self.performance = {}  # 性能指标
        self.recommended_types = []  # 推荐图像类型
        self.use_cases = []  # 典型应用场景

    @abstractmethod
    def compress(self, file_path):
        """压缩文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            tuple: (原始大小, 压缩后大小)
        """
        pass

    def get_name(self):
        """获取策略名称"""
        return self.name

    def get_description(self):
        """获取策略描述"""
        return self.description

    def get_tools(self):
        """获取使用的工具列表"""
        return self.tools

    def get_performance(self):
        """获取性能指标"""
        return self.performance

    def get_recommended_types(self):
        """获取推荐图像类型"""
        return self.recommended_types

    def get_use_cases(self):
        """获取典型应用场景"""
        return self.use_cases

    def get_file_size(self, file_path):
        """获取文件大小
        
        Args:
            file_path: 文件路径
            
        Returns:
            int: 文件大小（字节）
        """
        import os
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0

    def calculate_compression_rate(self, original_size, final_size):
        """计算压缩率
        
        Args:
            original_size: 原始大小
            final_size: 压缩后大小
            
        Returns:
            float: 压缩率（百分比）
        """
        if original_size == 0:
            return 0.0
        return (original_size - final_size) / original_size * 100
