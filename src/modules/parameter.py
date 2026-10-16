"""参数管理模块

该模块负责处理工具参数的封装、验证和管理，包括：
- ToolParameter类：封装单个工具参数和验证逻辑
- ParameterValidator类：参数验证器，实现双重验证机制
- ToolParameterSet类：管理一组相关的工具参数
"""

class ParameterValidationError(Exception):
    """参数验证错误异常"""
    pass

class ToolParameter:
    """单个工具参数封装类"""
    
    def __init__(self, name, value=None, param_type=str, required=False, 
                 min_value=None, max_value=None, default=None, description="", 
                 hint=""):
        """初始化工具参数
        
        Args:
            name: 参数名称
            value: 参数值
            param_type: 参数类型
            required: 是否必填
            min_value: 最小值（适用于数值类型）
            max_value: 最大值（适用于数值类型）
            default: 默认值
            description: 参数描述
            hint: 参数提示信息
        """
        self.name = name
        self.param_type = param_type
        self.required = required
        self.min_value = min_value
        self.max_value = max_value
        self.default = default
        self.description = description
        self.hint = hint
        
        # 设置参数值，如果未提供则使用默认值
        self.value = value if value is not None else default
    
    def validate(self):
        """验证参数有效性，实现双重验证机制
        
        Raises:
            ParameterValidationError: 参数验证失败时抛出
        """
        # 1. 空值校验
        if self.required and self.value is None:
            raise ParameterValidationError(f"参数 '{self.name}' 是必填项")
        
        # 2. 类型校验
        if self.value is not None and not isinstance(self.value, self.param_type):
            try:
                # 尝试类型转换
                self.value = self.param_type(self.value)
            except (ValueError, TypeError):
                raise ParameterValidationError(
                    f"参数 '{self.name}' 类型错误，期望 {self.param_type.__name__}，实际 {type(self.value).__name__}"
                )
        
        # 3. 范围校验（仅适用于数值类型）
        if isinstance(self.value, (int, float)):
            if self.min_value is not None and self.value < self.min_value:
                raise ParameterValidationError(
                    f"参数 '{self.name}' 超出最小值范围，最小值为 {self.min_value}"
                )
            if self.max_value is not None and self.value > self.max_value:
                raise ParameterValidationError(
                    f"参数 '{self.name}' 超出最大值范围，最大值为 {self.max_value}"
                )
    
    def get_value(self):
        """获取参数值"""
        return self.value
    
    def set_value(self, value):
        """设置参数值
        
        Args:
            value: 参数值
        """
        self.value = value

class ParameterValidator:
    """参数验证器，用于验证一组参数"""
    
    @staticmethod
    def validate_parameters(parameters):
        """验证一组参数
        
        Args:
            parameters: ToolParameter对象列表或字典
            
        Raises:
            ParameterValidationError: 任何参数验证失败时抛出
        """
        if isinstance(parameters, list):
            # 列表形式：遍历验证每个参数
            for param in parameters:
                if isinstance(param, ToolParameter):
                    param.validate()
        elif isinstance(parameters, dict):
            # 字典形式：遍历验证每个值
            for name, param in parameters.items():
                if isinstance(param, ToolParameter):
                    param.validate()
        else:
            raise TypeError("参数必须是ToolParameter对象列表或字典")

class ToolParameterSet:
    """工具参数集合，管理一组相关的工具参数"""
    
    def __init__(self, tool_name, parameters=None):
        """初始化参数集合
        
        Args:
            tool_name: 工具名称
            parameters: 参数字典，键为参数名，值为ToolParameter对象
        """
        self.tool_name = tool_name
        self.parameters = parameters or {}
    
    def add_parameter(self, parameter):
        """添加参数
        
        Args:
            parameter: ToolParameter对象
        """
        if isinstance(parameter, ToolParameter):
            self.parameters[parameter.name] = parameter
    
    def get_parameter(self, name):
        """获取参数
        
        Args:
            name: 参数名称
            
        Returns:
            ToolParameter: 参数对象
        """
        return self.parameters.get(name)
    
    def get_parameter_value(self, name, default=None):
        """获取参数值
        
        Args:
            name: 参数名称
            default: 默认值
            
        Returns:
            参数值
        """
        param = self.parameters.get(name)
        return param.value if param else default
    
    def set_parameter_value(self, name, value):
        """设置参数值
        
        Args:
            name: 参数名称
            value: 参数值
        """
        param = self.parameters.get(name)
        if param:
            param.set_value(value)
    
    def validate(self):
        """验证所有参数
        
        Raises:
            ParameterValidationError: 任何参数验证失败时抛出
        """
        ParameterValidator.validate_parameters(self.parameters)
    
    def to_dict(self):
        """将参数集合转换为字典
        
        Returns:
            dict: 参数名到参数值的映射
        """
        return {
            name: param.value 
            for name, param in self.parameters.items()
        }
    
    @classmethod
    def from_dict(cls, tool_name, param_dict, param_definitions):
        """从字典创建参数集合
        
        Args:
            tool_name: 工具名称
            param_dict: 参数值字典
            param_definitions: 参数定义字典，包含每个参数的元数据
            
        Returns:
            ToolParameterSet: 参数集合对象
        """
        parameters = {}
        
        for param_name, definition in param_definitions.items():
            # 从param_dict获取参数值，如果不存在则使用定义中的默认值
            value = param_dict.get(param_name, definition.get('default'))
            
            # 创建ToolParameter对象
            param = ToolParameter(
                name=param_name,
                value=value,
                param_type=definition.get('type', str),
                required=definition.get('required', False),
                min_value=definition.get('min_value'),
                max_value=definition.get('max_value'),
                default=definition.get('default'),
                description=definition.get('description', ''),
                hint=definition.get('hint', '')
            )
            parameters[param_name] = param
        
        return cls(tool_name, parameters)

# 工具参数定义字典，集中管理所有工具的参数规则
TOOL_PARAMETER_DEFINITIONS = {
    # PNG工具参数定义
    'libimagequant': {
        'quality': {
            'type': int,
            'required': True,
            'min_value': 0,
            'max_value': 100,
            'default': 15,
            'description': '压缩质量',
            'hint': '0-100，值越小压缩率越高，质量越低'
        },
        'min_quality': {
            'type': int,
            'required': False,
            'min_value': 0,
            'max_value': 100,
            'default': 10,
            'description': '最小质量',
            'hint': '0-100，通常比quality小5'
        },
        'max_quality': {
            'type': int,
            'required': False,
            'min_value': 0,
            'max_value': 100,
            'default': 20,
            'description': '最大质量',
            'hint': '0-100，通常比quality大5'
        },
        'dithering_level': {
            'type': float,
            'required': False,
            'min_value': 0.0,
            'max_value': 1.0,
            'default': 0.3,
            'description': '抖动级别',
            'hint': '0.0-1.0，值越小抖动越少'
        },
        'max_colors': {
            'type': int,
            'required': False,
            'min_value': 1,
            'max_value': 256,
            'default': 128,
            'description': '最大颜色数',
            'hint': '1-256，值越小压缩率越高'
        }
    },
    'pngquant': {
        'quality': {
            'type': int,
            'required': True,
            'min_value': 0,
            'max_value': 100,
            'default': 15,
            'description': '压缩质量',
            'hint': '0-100，值越小压缩率越高，质量越低'
        }
    },
    'oxipng': {
        'level': {
            'type': int,
            'required': True,
            'min_value': 0,
            'max_value': 6,
            'default': 6,
            'description': '优化级别',
            'hint': '0-6，值越大优化效果越好，速度越慢'
        }
    },
    'zopflipng': {
            'iterations': {
                'type': int,
                'required': True,
                'min_value': 0,
                'max_value': 2000,
                'default': 200,
                'description': '迭代次数',
                'hint': '0-2000，值越大压缩效果越好，速度越慢'
            },
        'lossy': {
            'type': bool,
            'required': False,
            'default': True,
            'description': '是否使用有损压缩',
            'hint': 'True表示使用有损压缩，False表示无损压缩'
        },
        'lossy_8bit': {
            'type': bool,
            'required': False,
            'default': True,
            'description': '是否使用8位有损压缩',
            'hint': 'True表示使用8位有损压缩'
        },
        'lossy_transparent': {
            'type': bool,
            'required': False,
            'default': True,
            'description': '是否对透明通道使用有损压缩',
            'hint': 'True表示对透明通道使用有损压缩'
        },
        'filters': {
            'type': str,
            'required': False,
            'default': '--filters=0123456',
            'description': '滤镜选项',
            'hint': '指定使用的PNG滤镜'
        }
    },
    # JPG工具参数定义
    'mozjpeg': {
        'quality': {
            'type': int,
            'required': True,
            'min_value': 0,
            'max_value': 100,
            'default': 25,
            'description': '压缩质量',
            'hint': '0-100，值越小压缩率越高，质量越低'
        }
    },
    'jpegoptim': {
        'quality': {
            'type': int,
            'required': True,
            'min_value': 0,
            'max_value': 100,
            'default': 10,
            'description': '压缩质量',
            'hint': '0-100，值越小压缩率越高，质量越低'
        }
    },
    # 音频工具参数定义
    'ffmpeg': {
        'bitrate': {
            'type': int,
            'required': True,
            'min_value': 8,
            'max_value': 320,
            'default': 32,
            'description': '音频比特率',
            'hint': '8-320kbps，值越小压缩率越高，质量越低'
        }
    }
}
