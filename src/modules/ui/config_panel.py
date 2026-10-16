from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QGroupBox, QRadioButton, QCheckBox, 
    QGridLayout, QFrame, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QMimeData

from modules.strategies import STRATEGY_CONFIGS

class ConfigPanel(QWidget):
    # 定义信号
    start_compression = Signal(str, str, bool)
    stop_compression = Signal()
    
    def __init__(self, logger, config, compressor):
        super().__init__()
        self.logger = logger
        self.config = config
        self.compressor = compressor
        
        # 设置接受拖放
        self.setAcceptDrops(True)
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 配置标题
        config_title = QLabel("配置")
        config_title.setObjectName("panelTitle")
        layout.addWidget(config_title)
        
        # 拖放提示
        drop_hint = QLabel("💡 提示：您可以直接拖放图片文件或文件夹到窗口中")
        drop_hint.setObjectName("hintText")
        layout.addWidget(drop_hint)
        
        # 文件夹选择
        folder_group = QGroupBox("图片目录")
        folder_layout = QHBoxLayout()
        
        self.folder_edit = QLineEdit()
        self.folder_edit.setText(self.config.default_image_dir)
        folder_layout.addWidget(self.folder_edit)
        
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(browse_btn)
        
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)
        
        # 压缩策略
        strategy_group = QGroupBox("压缩策略")
        strategy_layout = QGridLayout()
        
        # 存储当前选择的策略
        self.selected_strategy = "speed"
        
        # 创建策略按钮
        self.strategy_buttons = []
        row = 0
        col = 0
        for idx, (strategy_key, strategy_config) in enumerate(STRATEGY_CONFIGS.items()):
            # 创建策略卡片
            card = QFrame()
            card.setObjectName("strategyCard")
            card.setFrameShape(QFrame.StyledPanel)
            card.setFrameShadow(QFrame.Raised)
            
            # 设置默认样式
            default_style = """
                QFrame#strategyCard {
                    border: 2px solid #d0d0d0;
                    border-radius: 8px;
                    background-color: #e8e8e8;
                    padding: 10px;
                    margin: 5px;
                    min-width: 140px;
                }
                QFrame#strategyCard QLabel {
                    color: #333333;
                }
                QFrame#strategyCard:hover {
                    border-color: #4080ff;
                    background-color: #d0d0d0;
                }
            """
            
            # 设置选中样式
            selected_style = """
                QFrame#strategyCard {
                    border: 2px solid #4080ff;
                    border-radius: 8px;
                    background-color: #4080ff;
                    padding: 10px;
                    margin: 5px;
                    min-width: 140px;
                }
                QFrame#strategyCard QLabel {
                    color: white;
                }
            """
            
            # 设置初始样式
            if strategy_key == "speed":
                card.setStyleSheet(selected_style)
            else:
                card.setStyleSheet(default_style)
            
            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignCenter)
            
            # 策略名称和图标，移除文字说明
            name_layout = QHBoxLayout()
            name_layout.setAlignment(Qt.AlignCenter)
            
            name_label = QLabel(f"{strategy_config['icon']} {strategy_config['name']}")
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setObjectName("strategyName")
            name_layout.addWidget(name_label)
            
            # 如果是压缩率优先策略，添加设置按钮
            settings_btn = None
            if strategy_key == 'compression':
                settings_btn = QPushButton("⚙️")
                settings_btn.setObjectName("settingsButton")
                settings_btn.setToolTip("配置极致压缩策略参数")
                settings_btn.setFixedSize(24, 24)
                settings_btn.clicked.connect(self.on_settings_clicked)
                name_layout.addWidget(settings_btn)
            
            card_layout.addLayout(name_layout)
            
            # 单选按钮（隐藏，通过点击卡片来切换）
            radio_btn = QRadioButton()
            radio_btn.setChecked(strategy_key == "speed")
            radio_btn.setHidden(True)
            card_layout.addWidget(radio_btn)
            
            # 点击卡片切换单选按钮状态
            def on_card_clicked(key=strategy_key, btn=radio_btn, card=card):
                btn.setChecked(True)
                self.on_strategy_selected(True, key)
                
                # 更新所有卡片样式
                for i, (c, r) in enumerate(self.strategy_buttons):
                    if c == card:
                        # 选中状态样式
                        c.setStyleSheet("""
                            QFrame#strategyCard {
                                border: 2px solid #4080ff;
                                border-radius: 8px;
                                background-color: #4080ff;
                                padding: 10px;
                                margin: 5px;
                                min-width: 140px;
                            }
                            QFrame#strategyCard QLabel {
                                color: white;
                            }
                        """)
                    else:
                        # 默认状态样式
                        c.setStyleSheet("""
                            QFrame#strategyCard {
                                border: 2px solid #d0d0d0;
                                border-radius: 8px;
                                background-color: #e8e8e8;
                                padding: 10px;
                                margin: 5px;
                                min-width: 140px;
                            }
                            QFrame#strategyCard QLabel {
                                color: #333333;
                            }
                            QFrame#strategyCard:hover {
                                border-color: #4080ff;
                                background-color: #d0d0d0;
                            }
                        """)
            
            # 使用lambda正确绑定参数，避免闭包问题
            card.mousePressEvent = lambda event, key=strategy_key, btn=radio_btn, card=card: on_card_clicked(key=key, btn=btn, card=card)
            radio_btn.toggled.connect(lambda checked, key=strategy_key, btn=radio_btn, card=card: on_card_clicked(key=key, btn=btn, card=card) if checked else None)
            
            # 将卡片和单选按钮添加到列表
            self.strategy_buttons.append((card, radio_btn))
            
            # 添加卡片到布局
            strategy_layout.addWidget(card, row, col)
            
            # 每行显示4个策略
            col += 1
            if col == 4:
                col = 0
                row += 1
        
        strategy_group.setLayout(strategy_layout)
        layout.addWidget(strategy_group)
        
        # 音频压缩选项
        audio_layout = QHBoxLayout()
        
        self.audio_check = QCheckBox("同时压缩音频文件")
        audio_layout.addWidget(self.audio_check)
        
        audio_layout.addStretch()
        layout.addLayout(audio_layout)
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("开始压缩")
        self.start_btn.setObjectName("primaryButton")
        self.start_btn.clicked.connect(self.on_start)
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止压缩")
        self.stop_btn.setObjectName("dangerButton")
        self.stop_btn.clicked.connect(self.on_stop)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
    
    def browse_folder(self):
        """浏览文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择图片目录", 
            self.folder_edit.text()
        )
        if folder:
            self.folder_edit.setText(folder)
    
    def on_strategy_selected(self, checked, key):
        """策略选择处理"""
        if checked:
            self.selected_strategy = key
    
    def on_start(self):
        """开始压缩处理"""
        path = self.folder_edit.text()
        if not path:
            self.logger.error("请选择图片目录")
            return
        
        # 检查压缩工具
        missing_tools = self.config.validate_tools()
        if missing_tools:
            self.logger.error(f"缺少压缩工具: {', '.join(missing_tools)}")
            return
        
        # 禁用开始按钮，启用停止按钮
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # 发送开始压缩信号
        self.start_compression.emit(
            path, 
            self.selected_strategy, 
            self.audio_check.isChecked()
        )
    
    def on_stop(self):
        """停止压缩处理"""
        # 启用开始按钮，禁用停止按钮
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # 发送停止压缩信号
        self.stop_compression.emit()
    
    def show_help(self):
        """显示帮助信息"""
        print("显示帮助信息")
    
    def save_logs(self):
        """保存日志"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "compression_log.txt", "文本文件 (*.txt)"
        )
        if file_path:
            self.logger.save_logs(file_path)
    
    def dragEnterEvent(self, event):
        """处理拖放进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """处理拖放移动事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """处理拖放事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                # 获取第一个文件/文件夹的路径
                file_path = urls[0].toLocalFile()
                self.folder_edit.setText(file_path)
    
    def toggle_debug_logs(self, checked):
        """切换调试日志显示"""
        print(f"调试日志: {'开启' if checked else '关闭'}")
    
    def on_settings_clicked(self):
        """处理设置按钮点击事件"""
        # 发送信号给主窗口，打开参数配置对话框
        from ..ui.parameter_dialog import ParameterDialog
        
        # 获取当前策略的参数配置
        current_params = getattr(self.compressor, 'strategy_parameters', {}).get('compression', {})
        dialog = ParameterDialog(self.config, self.logger, current_params)
        if dialog.exec():
            # 如果用户点击了确认，获取配置的参数
            params = dialog.get_parameters()
            # 发送参数给压缩器
            self.compressor.set_strategy_parameters('compression', params)
            self.logger.info(f"已更新极致压缩策略参数: {params}")

    def _update_strategy_button_style(self, btn, key, config):
        """更新策略按钮样式"""
        # 基础样式
        icon = config.get('icon', '')
        name = config.get('name', '')
        
        # 构建按钮内容
        if key == 'speed':
            # 常规压缩特殊样式
            btn.setText(f"{icon}\n{name}\n⚡")
            btn.setStyleSheet("""
                QPushButton {
                    text-align: center;
                    font-weight: bold;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 5px;
                    background-color: #f5f5f5;
                }
                QPushButton:checked {
                    background-color: #e3f2fd;
                    border-color: #2196f3;
                    color: #1976d2;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
        else:
            # 普通样式
            btn.setText(f"{icon}\n{name}")
            btn.setStyleSheet("""
                QPushButton {
                    text-align: center;
                    font-weight: bold;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 5px;
                    background-color: #ffffff;
                }
                QPushButton:checked {
                    background-color: #e3f2fd;
                    border-color: #2196f3;
                    color: #1976d2;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                }
            """)
