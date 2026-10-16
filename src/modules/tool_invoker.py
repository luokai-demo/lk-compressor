"""工具调用器模块

该模块负责统一管理工具调用，包括：
- ToolInvoker类：统一工具调用入口
- 处理工具参数验证和转换
- 实现策略驱动的工具调用
"""

from .parameter import ToolParameterSet, ParameterValidationError, TOOL_PARAMETER_DEFINITIONS
from .logger import Logger

class ToolInvoker:
    """工具调用器，统一管理工具调用"""
    
    def __init__(self, tools_manager, logger=None):
        """初始化工具调用器
        
        Args:
            tools_manager: 工具管理器实例
            logger: 日志记录器实例
        """
        self.tools_manager = tools_manager
        self.logger = logger or Logger()
    
    def invoke_tool(self, tool_type, tool_name, file_path, params_dict=None):
        """调用指定工具压缩文件
        
        Args:
            tool_type: 工具类型（png, jpg, audio等）
            tool_name: 工具名称
            file_path: 文件路径
            params_dict: 参数字典
            
        Returns:
            int: 压缩后文件大小
            
        Raises:
            ParameterValidationError: 参数验证失败时抛出
            Exception: 工具调用失败时抛出
        """
        # 1. 获取工具的参数定义
        if tool_name not in TOOL_PARAMETER_DEFINITIONS:
            self.logger.warning(f"工具 '{tool_name}' 没有参数定义，使用默认参数")
            param_definitions = {}
        else:
            param_definitions = TOOL_PARAMETER_DEFINITIONS[tool_name]
        
        # 2. 创建参数集合
        param_set = ToolParameterSet.from_dict(
            tool_name=tool_name,
            param_dict=params_dict or {},
            param_definitions=param_definitions
        )
        
        # 3. 验证参数
        self.logger.debug(f"验证工具 '{tool_name}' 的参数: {param_set.to_dict()}")
        param_set.validate()
        
        # 4. 获取工具实例
        tool = self.tools_manager.get_tool(tool_type, tool_name)
        
        # 5. 调用工具
        try:
            self.logger.debug(f"调用工具 '{tool_name}' 压缩文件: {file_path}")
            self.logger.debug(f"工具参数: {param_set.to_dict()}")
            
            # 将参数集合转换为字典传递给工具
            result = tool.compress(file_path, **param_set.to_dict())
            
            self.logger.debug(f"工具 '{tool_name}' 调用成功，返回结果: {result}")
            return result
        except Exception as e:
            self.logger.error(f"工具 '{tool_name}' 调用失败: {str(e)}")
            raise
    
    def invoke_by_strategy(self, strategy, file_path):
        """根据策略配置调用工具
        
        Args:
            strategy: 策略实例
            file_path: 文件路径
            
        Returns:
            tuple: (原始大小, 压缩后大小)
        """
        # 1. 调用策略的compress方法，策略内部会使用ToolInvoker调用具体工具
        return strategy.compress(file_path)
    
    def get_tool_parameter_set(self, tool_name, params_dict=None):
        """获取指定工具的参数集合
        
        Args:
            tool_name: 工具名称
            params_dict: 参数字典
            
        Returns:
            ToolParameterSet: 参数集合对象
        """
        param_definitions = TOOL_PARAMETER_DEFINITIONS.get(tool_name, {})
        return ToolParameterSet.from_dict(
            tool_name=tool_name,
            param_dict=params_dict or {},
            param_definitions=param_definitions
        )
    
    def validate_tool_parameters(self, tool_name, params_dict):
        """验证指定工具的参数
        
        Args:
            tool_name: 工具名称
            params_dict: 参数字典
            
        Raises:
            ParameterValidationError: 参数验证失败时抛出
        """
        param_set = self.get_tool_parameter_set(tool_name, params_dict)
        param_set.validate()
    
    def get_tool_parameter_definitions(self, tool_name):
        """获取指定工具的参数定义
        
        Args:
            tool_name: 工具名称
            
        Returns:
            dict: 参数定义字典
        """
        return TOOL_PARAMETER_DEFINITIONS.get(tool_name, {})
