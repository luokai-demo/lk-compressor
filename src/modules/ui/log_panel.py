from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextOption, QTextCursor

class LogPanel(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.last_log_count = 0
        self.init_ui()
        self.setup_log_timer()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 日志标题和控制
        header_layout = QHBoxLayout()

        log_title = QLabel("日志")
        log_title.setObjectName("panelTitle")
        header_layout.addWidget(log_title)

        clear_btn = QPushButton("清理日志")
        clear_btn.setObjectName("dangerButton")
        clear_btn.clicked.connect(self.clear_logs)
        header_layout.addWidget(clear_btn)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 日志内容
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setObjectName("logText")
        self.log_text.setLineWrapMode(QTextEdit.WidgetWidth)
        self.log_text.setWordWrapMode(QTextOption.WordWrap)
        layout.addWidget(self.log_text)

    def setup_log_timer(self):
        """设置日志更新定时器"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_logs)
        self.timer.start(100)  # 每100ms更新一次

    def update_logs(self):
        """更新日志内容"""
        logs = self.logger.get_logs()
        if not logs:
            return

        current_log_count = len(logs)
        new_logs_count = current_log_count - self.last_log_count

        if new_logs_count > 0:
            # 只添加新日志
            for log in logs[-new_logs_count:]:
                self.log_text.append(log)

            # 滚动到底部
            self.log_text.moveCursor(QTextCursor.End)

            # 更新日志计数
            self.last_log_count = current_log_count
        elif current_log_count < self.last_log_count:
            # 日志数量减少，重新加载所有日志
            self.log_text.clear()
            for log in logs:
                self.log_text.append(log)
            self.last_log_count = current_log_count
            self.log_text.moveCursor(QTextCursor.End)

    def clear_logs(self):
        """清理日志"""
        # 清理内存中的日志
        self.logger.clear_logs()
        # 清空文本框
        self.log_text.clear()
        # 重置日志计数
        self.last_log_count = 0
