import os
from pathlib import Path

class ConfigMeta(type):
    """Config元类，支持动态属性"""
    
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls._settings_manager = None
    
    def _get_settings_manager(cls):
        """获取设置管理器实例"""
        if cls._settings_manager is None:
            try:
                from config.settings_manager import SettingsManager
                cls._settings_manager = SettingsManager()
            except ImportError:
                # 如果设置管理器不可用，使用默认值
                pass
        return cls._settings_manager
    
    def _get_dynamic_value(cls, category: str, param_name: str, default_value):
        """获取动态配置值"""
        settings_manager = cls._get_settings_manager()
        if settings_manager:
            try:
                value = settings_manager.get_value(category, param_name)
                return value if value is not None else default_value
            except Exception:
                pass
        return default_value
    
    # 动态属性定义
    @property
    def BASE_URL(cls):
        return cls._get_dynamic_value('basic', 'base_url', "http://120.55.57.58:3510/")
    
    @property
    def DEFAULT_PASSWORD(cls):
        return cls._get_dynamic_value('basic', 'default_password', "123456")
    
    @property
    def BROWSER_WIDTH(cls):
        return cls._get_dynamic_value('browser', 'browser_width', 350)
    
    @property
    def BROWSER_HEIGHT(cls):
        return cls._get_dynamic_value('browser', 'browser_height', 400)
    
    @property
    def WINDOW_COLS(cls):
        return cls._get_dynamic_value('browser', 'window_cols', 4)
    
    @property
    def WINDOW_ROWS(cls):
        return cls._get_dynamic_value('browser', 'window_rows', 3)
    
    @property
    def HEADLESS_MODE(cls):
        return cls._get_dynamic_value('browser', 'headless_mode', False)
    
    @property
    def LOGIN_WAIT_TIME(cls):
        return cls._get_dynamic_value('timing', 'login_wait_time', 10)
    
    @property
    def UPLOAD_WAIT_TIME(cls):
        return cls._get_dynamic_value('timing', 'upload_wait_time', 2)
    
    @property
    def SUBMIT_WAIT_TIME(cls):
        return cls._get_dynamic_value('timing', 'submit_wait_time', 5)
    
    @property
    def STATUS_CHECK_WAIT_TIME(cls):
        return cls._get_dynamic_value('timing', 'status_check_wait_time', 2)
    
    @property
    def DEFAULT_MAX_WORKERS(cls):
        return cls._get_dynamic_value('basic', 'max_workers', min(12, os.cpu_count() * 2))

class Config(metaclass=ConfigMeta):
    """配置类 - 集成动态设置管理"""
    
    # 屏幕配置（固定值）
    SCREEN_WIDTH = 2560
    SCREEN_HEIGHT = 1440
    
    # 线程配置（固定值）
    MIN_WORKERS = 1
    MAX_WORKERS = 20
    
    # 文件配置
    SUPPORTED_IMAGE_EXTENSIONS = ['*.jpg', '*.jpeg', '*.png']
    EXCEL_EXTENSIONS = ['.xlsx', '.xls']
    
    # 报告配置
    REPORT_TIMESTAMP_FORMAT = '%Y%m%d_%H%M%S'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    @classmethod
    def get_current_dir(cls):
        """获取项目根目录"""
        # 获取config文件夹的父目录（项目根目录）
        config_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(config_dir)
    
    @classmethod
    def validate_max_workers(cls, workers):
        """验证线程数配置"""
        return max(cls.MIN_WORKERS, min(workers, cls.MAX_WORKERS))
    
    @classmethod
    def reload_settings(cls):
        """重新加载设置"""
        cls._settings_manager = None
        cls._get_settings_manager() 