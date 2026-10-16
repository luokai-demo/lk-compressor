from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QFrame
)
from PySide6.QtCore import Qt, Signal, Slot

class ProgressPanel(QWidget):
    # 定义信号，用于在主线程中更新进度
    update_progress_signal = Signal(int, str, str)

    def __init__(self):
        super().__init__()
        self.init_ui()
        # 连接信号和槽
        self.update_progress_signal.connect(self.update_progress_slot)

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 进度标题
        progress_title = QLabel("进度")
        progress_title.setObjectName("panelTitle")
        layout.addWidget(progress_title)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("mainProgress")
        layout.addWidget(self.progress_bar)

        # 进度信息
        info_layout = QVBoxLayout()

        self.progress_text = QLabel("准备就绪")
        self.progress_text.setObjectName("progressText")
        info_layout.addWidget(self.progress_text)

        self.current_file = QLabel("")
        self.current_file.setObjectName("currentFile")
        self.current_file.setWordWrap(True)
        info_layout.addWidget(self.current_file)

        layout.addLayout(info_layout)

    def update_progress(self, value, text="", current_file=""):
        """更新进度（可以从子线程调用）
        
        Args:
            value: 进度值 (0-100)
            text: 进度文本
            current_file: 当前处理的文件
        """
        # 发送信号，在主线程中更新UI
        self.update_progress_signal.emit(value, text, current_file)

    @Slot(int, str, str)
    def update_progress_slot(self, value, text="", current_file=""):
        """更新进度的槽函数（在主线程中执行）
        
        Args:
            value: 进度值 (0-100)
            text: 进度文本
            current_file: 当前处理的文件
        """
        self.progress_bar.setValue(value)

        if text:
            self.progress_text.setText(text)

        if current_file:
            self.current_file.setText(f"当前处理: {current_file}")
        else:
            self.current_file.setText("")

    def reset(self):
        """重置进度"""
        # 直接调用槽函数，因为reset方法通常在主线程中调用
        self.progress_bar.setValue(0)
        self.progress_text.setText("准备就绪")
        self.current_file.setText("")
