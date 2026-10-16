"""企业级日志管理模块

该模块负责管理图片压缩工具的日志记录，包括：
- 支持完善的日志分级（DEBUG/INFO/WARN/ERROR/FATAL）
- JSON结构化日志格式输出
- 日志轮转策略（按大小与时间）
- 异常追踪能力，记录完整调用栈信息
- 控制台与文件双重输出
"""

import logging
import os
import datetime
import json
import traceback
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class JSONFormatter(logging.Formatter):
    """JSON结构化日志格式化器"""
    
    def format(self, record):
        """将日志记录格式化为JSON字符串"""
        log_record = {
            "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "error_code": getattr(record, "error_code", "0"),
            "process_id": record.process,
            "thread_id": record.thread,
            "logger_name": record.name
        }
        
        # 添加异常信息（如果有）
        if record.exc_info:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exc()
            }
        
        # 添加额外的上下文信息
        if hasattr(record, "extra_info"):
            log_record.update(record.extra_info)
        
        return json.dumps(log_record, ensure_ascii=False)

class Logger:
    """企业级日志类，管理日志记录和输出"""
    
    def __init__(self, log_dir=None):
        """初始化日志记录器
        
        Args:
            log_dir (str, optional): 日志文件目录，默认为None
        """
        # 创建日志记录器
        self.logger = logging.getLogger('ImageCompressor')
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        
        # 清空现有的处理器，避免重复
        self.logger.handlers.clear()
        
        # 设置日志目录
        if log_dir:
            self.log_dir = log_dir
        else:
            # 默认日志目录
            if hasattr(os, 'frozen') and os.frozen:
                # 打包环境
                self.log_dir = os.path.join(os.path.dirname(os.executable), 'logs')
            else:
                # 开发环境
                self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        
        # 确保日志目录存在
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 创建控制台处理器（仅输出INFO及以上级别）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # 创建文件处理器（按大小轮转）
        size_rotating_handler = RotatingFileHandler(
            filename=os.path.join(self.log_dir, 'compressor.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,  # 保留5个备份
            encoding='utf-8'
        )
        size_rotating_handler.setLevel(logging.DEBUG)
        size_rotating_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(size_rotating_handler)
        
        # 创建时间轮转处理器（每天轮转）
        time_rotating_handler = TimedRotatingFileHandler(
            filename=os.path.join(self.log_dir, 'compressor_daily.log'),
            when='midnight',  # 每天午夜轮转
            interval=1,  # 每天一次
            backupCount=30,  # 保留30天
            encoding='utf-8'
        )
        time_rotating_handler.setLevel(logging.INFO)
        time_rotating_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(time_rotating_handler)
        
        # 保存日志消息的列表，用于GUI显示
        self.log_messages = []
        # 移除日志数量限制，确保所有日志都能完整输出
        self.log_limit = None
        
        # 添加FATAL级别日志方法
        logging.addLevelName(logging.CRITICAL, 'FATAL')
    
    def debug(self, message, extra_info=None):
        """DEBUG级别的日志记录"""
        self._log(logging.DEBUG, message, extra_info)
    
    def info(self, message, extra_info=None):
        """INFO级别的日志记录"""
        self._log(logging.INFO, message, extra_info)
    
    def warning(self, message, extra_info=None):
        """WARN级别的日志记录"""
        self._log(logging.WARNING, message, extra_info)
    
    def error(self, message, error_code="500", exception=None, extra_info=None):
        """ERROR级别的日志记录"""
        self._log(logging.ERROR, message, extra_info, error_code, exception)
    
    def fatal(self, message, error_code="999", exception=None, extra_info=None):
        """FATAL级别的日志记录"""
        self._log(logging.CRITICAL, message, extra_info, error_code, exception)
    
    def _log(self, level, message, extra_info=None, error_code="0", exception=None):
        """内部日志记录方法"""
        # 创建日志记录
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            "",
            0,
            message,
            None,
            None,
            None,
            None
        )
        
        # 添加自定义属性
        record.error_code = error_code
        if extra_info:
            record.extra_info = extra_info
        
        # 如果有异常，添加异常信息
        if exception:
            record.exc_info = (type(exception), exception, exception.__traceback__)
        
        # 处理日志记录
        self.logger.handle(record)
        
        # 保存到GUI日志列表
        log_entry = f"{datetime.datetime.now().strftime('%H:%M:%S')} - {logging.getLevelName(level)} - {message}"
        if error_code != "0":
            log_entry += f" (错误码: {error_code})"
        if exception:
            log_entry += f" - {str(exception)}"
        self.log_messages.append(log_entry)
    
    def log_exception(self, message, error_code="500", exception=None, extra_info=None):
        """记录异常信息"""
        if not exception:
            exception = traceback.format_exc()
        self.error(message, error_code, exception, extra_info)
    
    def get_logs(self):
        """获取所有日志消息"""
        return self.log_messages
    
    def clear_logs(self):
        """清空日志消息"""
        self.log_messages.clear()
    
    def save_logs(self, file_path):
        """将日志保存到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            for message in self.log_messages:
                f.write(message + '\n')
    
    def set_log_level(self, level):
        """设置日志级别"""
        level_mapping = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARN': logging.WARNING,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'FATAL': logging.CRITICAL,
            'CRITICAL': logging.CRITICAL
        }
        log_level = level_mapping.get(level.upper(), logging.INFO)
        self.logger.setLevel(log_level)
        for handler in self.logger.handlers:
            handler.setLevel(log_level)