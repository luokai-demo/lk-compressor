from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QPushButton, QSplitter, QToolButton,
    QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, Signal, Slot, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QMimeData
from PySide6.QtGui import QIcon, QPixmap, QFont, QPalette, QColor
import os
import sys

from modules.ui.config_panel import ConfigPanel
from modules.ui.progress_panel import ProgressPanel
from modules.ui.log_panel import LogPanel
from modules.logger import Logger
from modules.compressor import ImageCompressor
from modules.config import Config

class MainWindow(QMainWindow):
    # 定义信号，用于在主线程中处理压缩完成事件
    compression_complete_signal = Signal(object)

    def __init__(self):
        super().__init__()

        # 初始化核心模块
        self.logger = Logger()
        self.config = Config()
        self.compressor = ImageCompressor(self.logger, self.config)

        # 设置窗口标题和大小
        self.setWindowTitle("图片压缩工具")
        self.resize(1200, 800)

        # 窗口居中显示
        self.center_window()

        # 设置窗口图标
        self.set_window_icon()

        # 设置接受拖放
        self.setAcceptDrops(True)

        # 连接信号和槽
        self.compression_complete_signal.connect(self.on_compression_complete_slot)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QHBoxLayout(central_widget)

        # 导航栏伸缩状态
        self.nav_expanded = False      # 默认为收起状态
        self.nav_width_expanded = 200 # 展开宽度
        self.nav_width_collapsed = 50

        # 直接创建并配置左侧导航栏
        self.create_left_nav()

        # 初始化导航栏伸缩动画
        self.nav_animation = None

        # 创建中间内容区
        self.center_content = QWidget()

        # 创建右侧辅助信息区
        self.right_sidebar = QFrame()
        self.right_sidebar.setFixedWidth(0)  # 隐藏右侧面板
        self.right_sidebar.setObjectName("rightSidebar")

        # 使用QSplitter实现可调整大小的布局
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.left_nav)
        splitter.addWidget(self.center_content)
        splitter.addWidget(self.right_sidebar)

        # 设置初始大小比例
        splitter.setSizes([self.nav_width_expanded, 1000, 0])

        main_layout.addWidget(splitter)

        # 创建中间内容区
        self.create_center_content()

        # 创建右侧辅助信息区
        self.create_right_sidebar()

        # 显示启动提示
        self.show_startup_warning()

    def set_window_icon(self):
        """设置窗口图标"""
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, 'image', 'icon.jpg')
            else:
                icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'image', 'icon.jpg')

            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                self.setWindowIcon(QIcon(pixmap))
        except Exception as e:
            self.logger.info(f"设置窗口图标失败: {str(e)}")

    def center_window(self):
        """将窗口居中显示在屏幕上"""
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()

        # 获取窗口尺寸
        window_rect = self.geometry()

        # 计算居中位置
        center_x = (screen_rect.width() - window_rect.width()) // 2
        center_y = (screen_rect.height() - window_rect.height()) // 2

        # 设置窗口位置
        self.move(center_x, center_y)

    def create_left_nav(self):
        """创建左侧导航栏内容"""
        # 使用QWidget作为导航栏容器，确保背景色正确应用
        self.left_nav = QWidget()
        self.left_nav.setObjectName("leftNav")
        self.left_nav.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # 根据当前状态设置初始宽度
        initial_width = self.nav_width_expanded if self.nav_expanded else self.nav_width_collapsed
        self.left_nav.setFixedWidth(initial_width)

        # 为整个导航栏设置背景色，使用更可靠的方法
        self.left_nav.setAutoFillBackground(True)
        palette = self.left_nav.palette()
        palette.setColor(self.left_nav.backgroundRole(), QColor(240, 240, 240))  # #f0f0f0
        self.left_nav.setPalette(palette)

        # 添加样式表确保所有子部件继承正确的背景色和文字颜色
        self.left_nav.setStyleSheet("""
            QWidget#leftNav {
                border-right: 1px solid #d0d0d0;
            }
            QWidget#leftNav QPushButton {
                background-color: transparent;
                color: #666666;
                border: none;
                padding: 12px 16px;
                text-align: left;
                font-size: 14px;
                border-radius: 4px;
                margin: 2px 8px;
            }
            QWidget#leftNav QPushButton:hover {
                background-color: #e0e0e0;
                color: #333333;
            }
            QWidget#leftNav QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QWidget#leftNav QLabel {
                color: #666666;
            }
        """)

        # 创建导航栏布局
        nav_layout = QVBoxLayout(self.left_nav)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)

        # 添加导航栏标题区域，包含伸缩按钮
        self.nav_title_area = QWidget()
        self.nav_title_area.setFixedHeight(30)
        title_layout = QHBoxLayout(self.nav_title_area)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)

        # 伸缩图标，放在左侧
        self.toggle_icon = QLabel("<")
        self.toggle_icon.setAlignment(Qt.AlignCenter)
        self.toggle_icon.setStyleSheet("font-size: 14px; font-weight: bold; color: #666666;")
        self.toggle_icon.setFixedWidth(30)
        title_layout.addWidget(self.toggle_icon)

        # 设置标题区域可点击进行伸缩
        self.nav_title_area.mousePressEvent = lambda event: self.toggle_navigation()
        self.nav_title_area.setCursor(Qt.PointingHandCursor)

        nav_layout.addWidget(self.nav_title_area)

        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #d0d0d0; margin: 5px 0;")
        nav_layout.addWidget(separator)

        # 导航菜单
        self.nav_buttons = []
        self.original_button_texts = []

        # 按钮配置
        nav_buttons = [
            ("📋 保存日志", self.save_logs),
            ("🔍 调试日志", self.toggle_debug_logs),
            ("💡 策略说明", self.show_strategy_help),
            ("ℹ️ 关于", self.show_about)
        ]

        # 创建所有导航按钮
        for text, callback in nav_buttons:
            # 根据初始状态决定按钮文本
            display_text = text if self.nav_expanded else text.split()[0]
            btn = QPushButton(display_text)

            # 根据初始状态决定按钮样式
            if self.nav_expanded:
                btn_style = """
                    QPushButton {
                        background-color: transparent;
                        color: #666666;
                        border: none;
                        padding: 12px 16px;
                        text-align: left;
                        font-size: 14px;
                        border-radius: 4px;
                        margin: 2px 8px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                        color: #333333;
                    }
                    QPushButton:pressed {
                        background-color: #d0d0d0;
                    }
                """
            else:
                btn_style = """
                    QPushButton {
                        background-color: transparent;
                        color: #666666;
                        border: none;
                        padding: 12px 0;
                        text-align: center;
                        font-size: 14px;
                        border-radius: 4px;
                        margin: 2px 8px;
                        width: 34px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                        color: #333333;
                    }
                    QPushButton:pressed {
                        background-color: #d0d0d0;
                    }
                """

            # 为按钮添加按下和回弹动画
            btn.setStyleSheet(btn_style)

            btn.clicked.connect(callback)
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            self.original_button_texts.append(text)

            # 特殊处理调试日志按钮
            if "调试日志" in text:
                self.debug_log_btn = btn

        # 添加拉伸
        nav_layout.addStretch()

    def toggle_navigation(self):
        """切换导航栏显示状态"""
        self.nav_expanded = not self.nav_expanded
        self.update_navigation_width()

    def update_navigation_width(self):
        """更新导航栏宽度，使用QPropertyAnimation + minimumWidth/maximumWidth实现稳定的动画"""
        # 检查是否已有动画在运行，如果有则不开始新动画
        if hasattr(self, 'nav_animation') and self.nav_animation and self.nav_animation.state() == QAbstractAnimation.Running:
            return

        # 设置导航栏宽度
        target_width = self.nav_width_expanded if self.nav_expanded else self.nav_width_collapsed

        # 更新按钮文本和样式
        for i, btn in enumerate(self.nav_buttons):
            if self.nav_expanded:
                # 展开状态：显示完整文本，左对齐，正常内边距
                btn.setText(self.original_button_texts[i])
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #666666;
                        border: none;
                        padding: 12px 16px;
                        text-align: left;
                        font-size: 14px;
                        border-radius: 4px;
                        margin: 2px 8px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                        color: #333333;
                    }
                    QPushButton:pressed {
                        background-color: #d0d0d0;
                    }
                """)
            else:
                # 收缩状态：只显示图标，居中对齐，减少内边距
                icon = self.original_button_texts[i].split()[0]
                btn.setText(icon)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #666666;
                        border: none;
                        padding: 12px 0;
                        text-align: center;
                        font-size: 14px;
                        border-radius: 4px;
                        margin: 2px 8px;
                        width: 34px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                        color: #333333;
                    }
                    QPushButton:pressed {
                        background-color: #d0d0d0;
                    }
                """)

        # 更新伸缩图标文本
        self.toggle_icon.setText(">" if not self.nav_expanded else "<")

        # 设置导航栏的sizePolicy为Preferred，以便进行动画
        self.left_nav.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # 清除固定宽度限制，让动画可以自由调整
        self.left_nav.setFixedWidth(0)

        # 使用QPropertyAnimation实现动画
        self.nav_animation = QPropertyAnimation(self.left_nav, b"maximumWidth")
        self.nav_animation.setDuration(600)  # 动画持续时间，减慢到600ms显得更高级
        self.nav_animation.setEasingCurve(QEasingCurve.InOutCubic)  # 平滑的缓动曲线
        self.nav_animation.setStartValue(self.left_nav.width())
        self.nav_animation.setEndValue(target_width)

        # 动画完成后的处理
        def animation_finished():
            # 恢复固定宽度和sizePolicy
            self.left_nav.setFixedWidth(target_width)
            self.left_nav.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # 连接动画完成信号
        self.nav_animation.finished.connect(animation_finished)

        # 启动动画
        self.nav_animation.start()

    def save_logs(self):
        """保存日志"""
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "compression_log.txt", "文本文件 (*.txt)"
        )
        if file_path:
            self.logger.save_logs(file_path)

    def toggle_debug_logs(self):
        """切换调试日志显示"""
        # 切换日志面板可见性
        is_visible = not self.log_panel.isVisible()
        self.log_panel.setVisible(is_visible)

        # 更新按钮状态，提供视觉反馈
        if hasattr(self, 'debug_log_btn'):
            if is_visible:
                # 显示日志时，按钮显示为激活状态
                if self.nav_expanded:
                    # 展开状态样式
                    self.debug_log_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #e0e0e0;
                            color: #333333;
                            border: none;
                            padding: 12px 16px;
                            text-align: left;
                            font-size: 14px;
                            border-radius: 4px;
                            margin: 2px 8px;
                        }
                        QPushButton:hover {
                            background-color: #d0d0d0;
                        }
                        QPushButton:pressed {
                            background-color: #c0c0c0;
                        }
                    """)
                else:
                    # 缩回状态样式
                    self.debug_log_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #e0e0e0;
                            color: #333333;
                            border: none;
                            padding: 12px 0;
                            text-align: center;
                            font-size: 14px;
                            border-radius: 4px;
                            margin: 2px 8px;
                            width: 34px;
                        }
                        QPushButton:hover {
                            background-color: #d0d0d0;
                        }
                        QPushButton:pressed {
                            background-color: #c0c0c0;
                        }
                    """)
            else:
                # 隐藏日志时，按钮恢复默认状态
                if self.nav_expanded:
                    # 展开状态样式
                    self.debug_log_btn.setStyleSheet("""
                        QPushButton {
                            background-color: transparent;
                            color: #666666;
                            border: none;
                            padding: 12px 16px;
                            text-align: left;
                            font-size: 14px;
                            border-radius: 4px;
                            margin: 2px 8px;
                        }
                        QPushButton:hover {
                            background-color: #e0e0e0;
                            color: #333333;
                        }
                        QPushButton:pressed {
                            background-color: #d0d0d0;
                        }
                    """)
                else:
                    # 缩回状态样式
                    self.debug_log_btn.setStyleSheet("""
                        QPushButton {
                            background-color: transparent;
                            color: #666666;
                            border: none;
                            padding: 12px 0;
                            text-align: center;
                            font-size: 14px;
                            border-radius: 4px;
                            margin: 2px 8px;
                            width: 34px;
                        }
                        QPushButton:hover {
                            background-color: #e0e0e0;
                            color: #333333;
                        }
                        QPushButton:pressed {
                            background-color: #d0d0d0;
                        }
                    """)

    def show_about(self):
        """显示关于信息"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            self, "关于图片压缩工具",
            "图片压缩工具 v2.1.0\n\n" 
            "一个高效的图片压缩工具，支持多种压缩策略\n\n" 
            "作者: 2096899568@qq.com\n"
        )

    def show_strategy_help(self):
        """显示压缩策略说明"""
        from PySide6.QtWidgets import QMessageBox
        message = "支持以下压缩策略：\n\n"

        message += "1. ⚡ 常规压缩：快速完成压缩\n"
        message += "   - 仅去除元数据，不做深度压缩\n"
        message += "   - 适合批量处理大量图片\n\n"

        message += "2. 📉 极致压缩：追求最高压缩率\n"
        message += "   - PNG: libimagequant → pngquant高压缩 → zopflipng优化\n"
        message += "   - JPG: mozjpeg高压缩 → jpegoptim深度优化\n"
        message += "   - 注意：zopflipng工具使用穷举法，迭代出最适合的压缩方式，只要使用就会明显变慢，适合极致压缩的最后一步。\n\n"

        message += "注意：\n"
        message += "- 极致压缩策略会显著增加处理时间\n"
        message += "- 建议先使用少量图片测试效果"

        QMessageBox.information(self, "压缩策略说明", message)

    def show_startup_warning(self):
        """显示启动提示弹窗"""
        from PySide6.QtWidgets import QMessageBox

        # 验证压缩工具
        missing_tools = self.config.validate_tools()
        if missing_tools:
            tools_status = f"⚠️  缺少工具: {', '.join(missing_tools)}\n"
            tools_status += "请确保所有工具都已正确安装在tools/modes目录下。"
        else:
            tools_status = "✅  所有工具已就绪，可以正常使用压缩功能。"

        # 创建消息框
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("启动提示")
        msg_box.setText("📢 图片压缩工具 v2.1.0")

        # 详细信息
        detailed_text = f"{tools_status}\n\n"
        detailed_text += "⚠️  重要提示：\n"
        detailed_text += "压缩过程将直接替换源文件，请务必先备份您的重要文件！\n\n"
        detailed_text += "💡 使用说明：\n"
        detailed_text += "1. 选择图片目录\n"
        detailed_text += "2. 选择压缩策略\n"
        detailed_text += "3. 点击开始压缩\n"
        detailed_text += "4. 查看压缩结果\n"

        msg_box.setInformativeText(detailed_text)

        # 设置按钮
        msg_box.setStandardButtons(QMessageBox.Ok)

        # 显示消息框
        msg_box.exec()

    def create_center_content(self):
        """创建中间内容区"""
        layout = QVBoxLayout(self.center_content)

        # 配置面板
        self.config_panel = ConfigPanel(self.logger, self.config, self.compressor)
        layout.addWidget(self.config_panel, stretch=1)

        # 进度面板
        self.progress_panel = ProgressPanel()
        layout.addWidget(self.progress_panel, stretch=1)

        # 日志面板，默认关闭不显示
        self.log_panel = LogPanel(self.logger)
        self.log_panel.setVisible(False)
        layout.addWidget(self.log_panel, stretch=2)

        # 连接信号槽
        self.config_panel.start_compression.connect(self.on_start_compression)
        self.config_panel.stop_compression.connect(self.on_stop_compression)

    def create_right_sidebar(self):
        """创建右侧辅助信息区（当前为空）"""
        # 右侧面板已隐藏，不创建任何内容
        pass

    def show_config(self):
        """显示配置页面"""
        print("显示配置页面")

    def show_progress(self):
        """显示进度页面"""
        print("显示进度页面")

    def show_logs(self):
        """显示日志页面"""
        print("显示日志页面")

    def show_stats(self):
        """显示统计页面"""
        print("显示统计页面")

    def show_help(self):
        """显示帮助页面"""
        print("显示帮助页面")

    def on_start_compression(self, path, strategy, compress_audio):
        """开始压缩事件处理"""
        self.progress_panel.update_progress(0, "正在扫描文件...")

        # 在新线程中执行压缩
        import threading
        compression_thread = threading.Thread(
            target=self.run_compression,
            args=(path, strategy, compress_audio)
        )
        compression_thread.daemon = True
        compression_thread.start()

    def run_compression(self, path, strategy, compress_audio):
        """执行压缩"""
        # 设置压缩策略
        self.compressor.set_strategy(strategy)

        # 定义进度回调函数
        def progress_callback(progress, current_file=""):
            """更新进度条和进度文本"""
            if progress == 0:
                text = "正在扫描文件..."
            elif progress == 100:
                text = "压缩完成"
            else:
                text = f"正在压缩文件... {progress}%"

            # 使用信号更新UI
            self.progress_panel.update_progress(progress, text, os.path.basename(current_file))

        # 执行压缩
        result = self.compressor.compress_images(path, progress_callback, compress_audio)

        # 发送压缩完成信号，在主线程中处理
        self.compression_complete_signal.emit(result)

    @Slot(object)
    def on_compression_complete_slot(self, result):
        """压缩完成处理（在主线程中执行）"""
        # 更新统计信息
        stats = self.compressor.get_statistics()

        # 显示完成消息
        from PySide6.QtWidgets import QMessageBox

        success_count = stats['success_count']
        failed_count = stats['failed_count']
        total_files = stats['total_files']

        # 计算大小信息
        total_original_size = stats['total_original_size']
        total_saved_bytes = stats['total_saved_bytes']
        final_size = total_original_size - total_saved_bytes

        # 使用compressor的bytes_to_readable方法格式化大小
        original_size = self.compressor.bytes_to_readable(total_original_size)
        final_size = self.compressor.bytes_to_readable(final_size)
        saved_space = self.compressor.bytes_to_readable(total_saved_bytes)

        saved_percent = 0
        if total_original_size > 0:
            saved_percent = int((total_saved_bytes / total_original_size) * 100)

        # 构建详细的统计信息
        message = f"压缩完成！\n\n"
        message += f"📊 详细统计信息：\n"
        message += f"\n"
        message += f"📋 文件统计：\n"
        message += f"   总文件数：{total_files}\n"
        message += f"   成功压缩：{success_count}\n"
        message += f"   压缩失败：{failed_count}\n"
        message += f"   PNG文件：{stats['png_count']}\n"
        message += f"   JPG文件：{stats['jpg_count']}\n"

        if stats['audio_count'] > 0:
            message += f"   音频文件：{stats['audio_count']}\n"

        if stats['other_count'] > 0:
            message += f"   其他文件：{stats['other_count']}\n"

        message += f"\n📈 大小统计：\n"
        message += f"   原始大小：{original_size}\n"
        message += f"   最终大小：{final_size}\n"
        message += f"   节省空间：{saved_space}\n"
        message += f"   节省比例：{saved_percent}%\n"

        message += f"\n💡 提示：\n"
        message += f"   压缩结果已直接替换源文件\n"
        message += f"   建议定期清理日志文件以节省空间\n"

        QMessageBox.information(self, "压缩完成", message)

        # 压缩完成后，重置按钮状态
        if hasattr(self, 'config_panel'):
            self.config_panel.start_btn.setEnabled(True)
            self.config_panel.stop_btn.setEnabled(False)

        # 重置进度面板
        self.progress_panel.reset()

    def on_stop_compression(self):
        """停止压缩事件处理"""
        self.compressor.stop_compression()
        self.progress_panel.update_progress(0, "压缩已停止")

        # 重置按钮状态
        if hasattr(self, 'config_panel'):
            self.config_panel.start_btn.setEnabled(True)
            self.config_panel.stop_btn.setEnabled(False)

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
                # 将路径设置到配置面板的文件夹输入框中
                if hasattr(self, 'config_panel'):
                    self.config_panel.folder_edit.setText(file_path)
