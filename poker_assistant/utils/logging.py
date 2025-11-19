"""
统一的错误处理和日志记录模块

提供整个项目的标准化错误处理和日志记录功能
"""

import logging
import sys
import traceback
from typing import Any, Optional, Dict
from datetime import datetime
import os


class PokerLogger:
    """扑克游戏日志记录器"""
    
    def __init__(self, name: str, log_level: str = "INFO", log_file: Optional[str] = None):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: 日志文件路径，如果为None则只输出到控制台
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # 避免重复添加处理器
        if self.logger.handlers:
            return
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（如果指定了文件）
        if log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs):
        """记录调试信息"""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """记录一般信息"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """记录警告信息"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, exc_info: bool = True, **kwargs):
        """记录错误信息"""
        self.logger.error(message, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, exc_info: bool = True, **kwargs):
        """记录严重错误信息"""
        self.logger.critical(message, exc_info=exc_info, **kwargs)
    
    def log_exception(self, message: str, exception: Exception):
        """记录异常信息"""
        self.logger.error(f"{message}: {str(exception)}", exc_info=True)


class PokerError(Exception):
    """扑克游戏基础异常类"""
    
    def __init__(self, message: str, error_code: str = "GENERIC_ERROR", 
                 details: Optional[Dict[str, Any]] = None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 额外的错误详情
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


class GTOError(PokerError):
    """GTO策略相关异常"""
    
    def __init__(self, message: str, gto_component: str = "unknown", **details):
        super().__init__(message, "GTO_ERROR", {
            'gto_component': gto_component,
            **details
        })


class AIError(PokerError):
    """AI决策相关异常"""
    
    def __init__(self, message: str, ai_component: str = "unknown", **details):
        super().__init__(message, "AI_ERROR", {
            'ai_component': ai_component,
            **details
        })


class GameError(PokerError):
    """游戏逻辑相关异常"""
    
    def __init__(self, message: str, game_component: str = "unknown", **details):
        super().__init__(message, "GAME_ERROR", {
            'game_component': game_component,
            **details
        })


class ValidationError(PokerError):
    """数据验证相关异常"""
    
    def __init__(self, message: str, field: str = "unknown", **details):
        super().__init__(message, "VALIDATION_ERROR", {
            'field': field,
            **details
        })


class ErrorHandler:
    """统一错误处理器"""
    
    def __init__(self, logger: Optional[PokerLogger] = None):
        """
        初始化错误处理器
        
        Args:
            logger: 日志记录器实例
        """
        self.logger = logger or PokerLogger("ErrorHandler")
        self.error_handlers = {
            "GTO_ERROR": self._handle_gto_error,
            "AI_ERROR": self._handle_ai_error,
            "GAME_ERROR": self._handle_game_error,
            "VALIDATION_ERROR": self._handle_validation_error,
            "GENERIC_ERROR": self._handle_generic_error
        }
    
    def handle_error(self, error: Exception, context: Optional[str] = None) -> Dict[str, Any]:
        """
        统一错误处理
        
        Args:
            error: 异常实例
            context: 错误发生上下文
            
        Returns:
            标准化的错误响应
        """
        error_info = {
            'context': context or "unknown",
            'timestamp': datetime.now().isoformat(),
            'traceback': traceback.format_exc()
        }
        
        if isinstance(error, PokerError):
            error_type = error.error_code
            error_info.update(error.to_dict())
            self.logger.error(f"PokerError [{error_type}]: {error.message}", extra=error_info)
        else:
            error_type = "GENERIC_ERROR"
            error_info.update({
                'error_code': error_type,
                'message': str(error),
                'details': {}
            })
            self.logger.error(f"GenericError: {str(error)}", extra=error_info)
        
        # 调用特定的错误处理器
        handler = self.error_handlers.get(error_type, self._handle_generic_error)
        return handler(error, error_info)
    
    def _handle_gto_error(self, error: GTOError, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理GTO错误"""
        self.logger.error(f"GTO组件错误: {error.message}")
        return {
            'success': False,
            'error_type': 'gto_error',
            'message': 'GTO策略计算失败，使用回退策略',
            'fallback_action': 'call',
            'details': error_info
        }
    
    def _handle_ai_error(self, error: AIError, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理AI错误"""
        self.logger.error(f"AI组件错误: {error.message}")
        return {
            'success': False,
            'error_type': 'ai_error',
            'message': 'AI决策失败，使用基础策略',
            'fallback_action': 'fold',
            'details': error_info
        }
    
    def _handle_game_error(self, error: GameError, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理游戏错误"""
        self.logger.error(f"游戏逻辑错误: {error.message}")
        return {
            'success': False,
            'error_type': 'game_error',
            'message': '游戏状态异常，请重新开始',
            'details': error_info
        }
    
    def _handle_validation_error(self, error: ValidationError, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理验证错误"""
        self.logger.warning(f"数据验证错误: {error.message}")
        return {
            'success': False,
            'error_type': 'validation_error',
            'message': f'参数验证失败: {error.message}',
            'field': error.details.get('field', 'unknown'),
            'details': error_info
        }
    
    def _handle_generic_error(self, error: Exception, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理通用错误"""
        self.logger.error(f"未预期的错误: {str(error)}")
        return {
            'success': False,
            'error_type': 'generic_error',
            'message': '系统错误，请稍后重试',
            'details': error_info
        }


# 全局日志记录器实例
main_logger = PokerLogger("PokerAssistant")
gto_logger = PokerLogger("GTOEngine", log_file="logs/gto_engine.log")
ai_logger = PokerLogger("AIEngine", log_file="logs/ai_engine.log")
game_logger = PokerLogger("GameEngine", log_file="logs/game_engine.log")
error_handler = ErrorHandler(main_logger)


def log_function_call(logger: PokerLogger):
    """函数调用日志装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"调用函数: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"函数 {func.__name__} 执行成功")
                return result
            except Exception as e:
                logger.error(f"函数 {func.__name__} 执行失败: {str(e)}")
                raise
        return wrapper
    return decorator


def safe_gto_operation(logger: PokerLogger = gto_logger):
    """安全的GTO操作装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"GTO操作失败: {str(e)}")
                error_handler.handle_error(GTOError(str(e), func.__name__), context=func.__name__)
                # 返回安全的默认值
                return {
                    'action': 'call',
                    'amount': 0,
                    'confidence': 0.5,
                    'reasoning': 'GTO计算失败，使用保守策略'
                }
        return wrapper
    return decorator