from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QSpinBox, QGroupBox,
    QPushButton, QGridLayout, QFrame, QMessageBox,
    QLineEdit, QFormLayout, QTabWidget, QWidget,
    QCheckBox
)
from PySide6.QtCore import Qt
from ..strategies.config_compression import COMPRESSION_STRATEGY_DEFAULTS

class ParameterDialog(QDialog):
    """极致压缩策略参数配置对话框"""

    def __init__(self, config, logger, params=None, parent=None):
        """初始化参数配置对话框"""
        super().__init__(parent)
        self.config = config
        self.logger = logger
        self.setWindowTitle("极致压缩策略参数配置")
        self.setMinimumWidth(600)
        self.setModal(True)

        # 默认参数设置 (从独立配置文件加载)
        self.default_params = COMPRESSION_STRATEGY_DEFAULTS.copy()

        # 当前参数
        self.current_params = self.default_params.copy()
        if params:
            self.current_params.update(params)

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 对话框标题
        title = QLabel("极致压缩策略参数配置")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        # 参数说明
        description = QLabel(
            "以下参数用于配置极致压缩策略的各项压缩工具参数。调整参数可能会影响压缩效果、速度和质量。"
        )
        description.setWordWrap(True)
        description.setObjectName("hintText")
        layout.addWidget(description)

        # 创建参数输入控件
        self.param_widgets = {}

        # 参数定义，按工具名称分组
        param_groups = {
            "libimagequant (PNG)": [
                {
                    'key': 'libimagequant_quality',
                    'name': '质量',
                    'description': '控制PNG量化质量，值越小压缩率越高',
                    'min': 0,
                    'max': 100,
                    'type': 'int',
                    'hint': '10-30（高压缩率）'
                },
                {
                    'key': 'libimagequant_dithering_level',
                    'name': '抖动率',
                    'description': '控制图像量化抖动，值越大图像越丰富但噪点越多',
                    'min': 0,
                    'max': 100,
                    'type': 'int',
                    'hint': '20-50（平衡值）'
                },
                {
                    'key': 'libimagequant_max_colors',
                    'name': '最大色彩数',
                    'description': '限制PNG最大颜色数量，值越小压缩率越高',
                    'min': 1,
                    'max': 256,
                    'type': 'int',
                    'hint': '64-128（平衡值）'
                }
            ],
            "pngquant (PNG)": [
                {
                    'key': 'pngquant_quality',
                    'name': '质量',
                    'description': '控制PNG压缩质量，值越小压缩率越高',
                    'min': 0,
                    'max': 100,
                    'type': 'int',
                    'hint': '10-30（高压缩率）'
                }
            ],
            "oxipng (PNG)": [
                {
                    'key': 'oxipng_level',
                    'name': '优化级别',
                    'description': '控制PNG无损优化强度，级别越高效果越好但越慢',
                    'min': 0,
                    'max': 6,
                    'type': 'int',
                    'hint': '6（最高级别）'
                }
            ],
            "zopflipng (PNG)": [
                {
                    'key': 'zopflipng_enabled',
                    'name': '启用zopflipng',
                    'description': '启用zopflipng进行极致压缩（注意：会显著增加压缩时间）',
                    'type': 'bool',
                    'hint': '耗时操作，谨慎开启'
                },
                {
                    'key': 'zopflipng_iterations',
                    'name': '迭代次数',
                    'description': '使用穷举法迭代出最适合的压缩方式，次数越多越慢',
                    'min': 0,
                    'max': 2000,
                    'type': 'int',
                    'hint': '默认15，只要使用就会明显变慢'
                }
            ],
            "mozjpeg (JPG)": [
                {
                    'key': 'mozjpeg_quality',
                    'name': '质量',
                    'description': '控制JPEG压缩质量，值越小压缩率越高',
                    'min': 0,
                    'max': 100,
                    'type': 'int',
                    'hint': '20-40（高压缩率）'
                }
            ],
            "jpegoptim (JPG)": [
                {
                    'key': 'jpegoptim_level',
                    'name': '质量',
                    'description': '控制JPEG二次优化质量，与mozjpeg配合使用',
                    'min': 0,
                    'max': 100,
                    'type': 'int',
                    'hint': '20-40（高压缩率）'
                }
            ]
        }

        # 创建标签页控件，按图片类型分组
        tab_widget = QTabWidget()

        # 按图片类型重新组织工具
        image_type_groups = {
            "PNG工具": [],
            "JPG工具": []
        }

        # 分类工具到对应的图片类型
        for tool_name, params in param_groups.items():
            if "PNG" in tool_name:
                image_type_groups["PNG工具"].append((tool_name, params))
            elif "JPG" in tool_name:
                image_type_groups["JPG工具"].append((tool_name, params))

        # 为每个图片类型创建标签页
        for image_type, tools in image_type_groups.items():
            # 创建标签页内容
            tab_content = QWidget()
            tab_layout = QVBoxLayout(tab_content)
            tab_layout.setSpacing(10)

            # 为每个工具创建分组框
            for tool_name, params in tools:
                # 创建工具分组框
                group_box = QGroupBox(tool_name)
                group_box.setObjectName("toolGroupBox")
                group_layout = QVBoxLayout(group_box)
                group_layout.setSpacing(15)
                group_layout.setContentsMargins(15, 15, 15, 15)

                # 添加该工具的所有参数
                for param in params:
                    # 获取参数值，安全地处理默认值
                    default_val = param.get('default')
                    if default_val is None:
                        # 如果没有显式默认值，尝试使用最小值，如果是布尔类型则默认为False
                        default_val = param.get('min', False) if param['type'] != 'bool' else False

                    param_value = self.current_params.get(param['key'], default_val)

                    # 创建参数行布局
                    param_row = QGridLayout()
                    param_row.setSpacing(10)
                    param_row.setContentsMargins(0, 0, 0, 0)

                    # 参数名称
                    param_label = QLabel(f"{param['name']}:")
                    param_label.setObjectName("paramLabel")
                    param_label.setToolTip(f"{param['description']} 💡 {param['hint']}")
                    param_row.addWidget(param_label, 0, 0, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)

                    # 参数范围和提示
                    range_text = f"范围: {param['min']}-{param['max']}" if param['type'] == 'int' else "类型: 开关"
                    param_info = QLabel(f"{range_text} | 💡 {param['hint']}")
                    param_info.setObjectName("hintText")
                    param_row.addWidget(param_info, 1, 0, 1, 1)

                    # 参数控件区域
                    control_container = QWidget()
                    control_layout = QHBoxLayout(control_container)
                    control_layout.setContentsMargins(0, 0, 0, 0)
                    control_layout.setSpacing(15)

                    if param['type'] == 'int':
                        # 滑块
                        slider = QSlider(Qt.Horizontal)
                        slider.setMinimum(param['min'])
                        slider.setMaximum(param['max'])
                        slider.setValue(param_value)
                        slider.setMinimumWidth(250)
                        slider.valueChanged.connect(lambda value, key=param['key']: self.on_param_changed(key, value))

                        # 数值输入框
                        spinbox = QSpinBox()
                        spinbox.setMinimum(param['min'])
                        spinbox.setMaximum(param['max'])
                        spinbox.setValue(param_value)
                        spinbox.setFixedWidth(80)
                        spinbox.valueChanged.connect(lambda value, key=param['key']: self.on_param_changed(key, value))

                        # 当前值显示
                        value_label = QLabel(f"当前值: {param_value}")
                        value_label.setObjectName("valueLabel")
                        value_label.setFixedWidth(100)

                        control_layout.addWidget(slider, 1)
                        control_layout.addWidget(spinbox)
                        control_layout.addWidget(value_label, 0, Qt.AlignRight)

                        # 保存控件引用
                        self.param_widgets[param['key']] = {
                            'slider': slider,
                            'spinbox': spinbox,
                            'value_label': value_label,
                            'type': 'int'
                        }

                    elif param['type'] == 'bool':
                        # 复选框
                        checkbox = QCheckBox(param['name'])
                        checkbox.setChecked(bool(param_value))
                        checkbox.stateChanged.connect(lambda state, key=param['key']: self.on_param_changed(key, bool(state)))

                        # 当前值显示
                        value_label = QLabel(f"当前状态: {'已启用' if param_value else '未启用'}")
                        value_label.setObjectName("valueLabel")
                        value_label.setFixedWidth(100)

                        control_layout.addWidget(checkbox)
                        control_layout.addStretch()
                        control_layout.addWidget(value_label, 0, Qt.AlignRight)

                        # 保存控件引用
                        self.param_widgets[param['key']] = {
                            'checkbox': checkbox,
                            'value_label': value_label,
                            'type': 'bool'
                        }

                    param_row.addWidget(control_container, 0, 1, 2, 1)

                    # 添加到工具分组布局
                    group_layout.addLayout(param_row)

                # 添加工具分组框到标签页
                tab_layout.addWidget(group_box)

            tab_layout.addStretch()

            # 添加标签页
            tab_widget.addTab(tab_content, image_type)

        # 将标签页添加到主布局
        layout.addWidget(tab_widget)

        # 按钮区域
        btn_layout = QHBoxLayout()

        # 恢复默认按钮
        reset_btn = QPushButton("恢复默认")
        reset_btn.clicked.connect(self.on_reset)
        btn_layout.addWidget(reset_btn)

        btn_layout.addStretch()

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        # 确认按钮
        ok_btn = QPushButton("确认")
        ok_btn.setObjectName("primaryButton")
        ok_btn.clicked.connect(self.on_ok)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    def on_param_changed(self, key, value):
        """参数值变化处理"""
        # 更新当前参数
        self.current_params[key] = value

        # 同步滑块和数值输入框
        widgets = self.param_widgets[key]
        if 'slider' in widgets and 'spinbox' in widgets:
            if widgets['slider'].value() != value:
                widgets['slider'].setValue(value)
            if widgets['spinbox'].value() != value:
                widgets['spinbox'].setValue(value)

        # 更新当前值显示
        if 'value_label' in widgets:
            widgets['value_label'].setText(f"当前值: {value}")

    def on_ok(self):
        """确认按钮点击处理"""
        # 验证参数
        if self.validate_params():
            self.accept()

    def validate_params(self):
        """验证参数有效性"""
        # 这里可以添加更复杂的参数验证逻辑
        # 目前参数范围已经通过控件限制，基本无需额外验证
        return True

    def on_reset(self):
        """恢复默认参数"""
        # 确认对话框
        reply = QMessageBox.question(
            self, "恢复默认", "确定要恢复所有参数到默认值吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 恢复默认值
            self.current_params = self.default_params.copy()

            # 更新所有控件
            for key, widgets in self.param_widgets.items():
                value = self.current_params[key]
                param_type = widgets.get('type', 'int')

                if param_type == 'int':
                    if 'slider' in widgets:
                        widgets['slider'].setValue(value)
                    if 'spinbox' in widgets:
                        widgets['spinbox'].setValue(value)
                    if 'value_label' in widgets:
                        widgets['value_label'].setText(f"当前值: {value}")

                elif param_type == 'bool':
                    if 'checkbox' in widgets:
                        widgets['checkbox'].setChecked(bool(value))
                    if 'value_label' in widgets:
                        widgets['value_label'].setText(f"当前状态: {'已启用' if value else '未启用'}")

    def get_parameters(self):
        """获取配置的参数"""
        return self.current_params.copy()
