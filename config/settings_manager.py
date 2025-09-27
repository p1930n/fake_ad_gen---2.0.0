#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置管理器
管理用户可配置参数，支持JSON持久化存储
"""

import json
import os
from typing import Dict, Any, Tuple
from pathlib import Path

class SettingsManager:
    """设置管理器"""
    __slots__ = ['config_file', 'default_settings', 'current_settings']
    
    def __init__(self, config_file: str = "user_settings.json"):
        self.config_file = config_file
        self.default_settings = self._get_default_settings()
        self.current_settings = self.default_settings.copy()
        self.load_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """获取默认设置"""
        return {
            # 基础设置
            "basic": {
                "base_url": {
                    "value": "http://120.55.57.58:3510/",
                    "description": "网站地址",
                    "type": "string",
                    "validation": r"^https?://.+/$"
                },
                "default_password": {
                    "value": "123456",
                    "description": "默认密码",
                    "type": "string",
                    "min_length": 1,
                    "max_length": 20
                },
                "max_workers": {
                    "value": 12,
                    "description": "最大线程数",
                    "type": "int",
                    "min": 1,
                    "max": 20
                }
            },
            
            # 浏览器设置
            "browser": {
                "headless_mode": {
                    "value": False,
                    "description": "无头模式 (后台运行)",
                    "type": "bool"
                },
                "browser_width": {
                    "value": 350,
                    "description": "浏览器窗口宽度",
                    "type": "int",
                    "min": 200,
                    "max": 800
                },
                "browser_height": {
                    "value": 400,
                    "description": "浏览器窗口高度",
                    "type": "int",
                    "min": 200,
                    "max": 800
                },
                "window_cols": {
                    "value": 4,
                    "description": "窗口列数",
                    "type": "int",
                    "min": 1,
                    "max": 6
                },
                "window_rows": {
                    "value": 3,
                    "description": "窗口行数",
                    "type": "int",
                    "min": 1,
                    "max": 4
                }
            },
            
            # 时间设置 (秒)
            "timing": {
                "login_wait_time": {
                    "value": 10,
                    "description": "登录等待时间 (秒)",
                    "type": "int",
                    "min": 5,
                    "max": 30
                },
                "upload_wait_time": {
                    "value": 2,
                    "description": "上传等待时间 (秒)",
                    "type": "int",
                    "min": 1,
                    "max": 10
                },
                "submit_wait_time": {
                    "value": 5,
                    "description": "提交等待时间 (秒)",
                    "type": "int",
                    "min": 2,
                    "max": 15
                },
                "status_check_wait_time": {
                    "value": 2,
                    "description": "状态检查等待时间 (秒)",
                    "type": "int",
                    "min": 1,
                    "max": 10
                }
            },
            
            # 图片设置
            "image": {
                "output_dir": {
                    "value": "generated_images",
                    "description": "图片输出目录",
                    "type": "string",
                    "min_length": 1,
                    "max_length": 50
                },
                "image_quality": {
                    "value": 95,
                    "description": "图片质量 (1-100)",
                    "type": "int",
                    "min": 50,
                    "max": 100
                },
                "max_images_per_student": {
                    "value": 10,
                    "description": "每位学生最大图片数",
                    "type": "int",
                    "min": 1,
                    "max": 20
                },
                "font_size_large": {
                    "value": 36,
                    "description": "大字体大小",
                    "type": "int",
                    "min": 20,
                    "max": 60
                },
                "font_size_medium": {
                    "value": 24,
                    "description": "中字体大小",
                    "type": "int",
                    "min": 16,
                    "max": 40
                },
                "font_size_small": {
                    "value": 18,
                    "description": "小字体大小",
                    "type": "int",
                    "min": 12,
                    "max": 30
                }
            },
            
            # 文件设置
            "file": {
                "supported_image_extensions": {
                    "value": ["*.jpg", "*.jpeg", "*.png"],
                    "description": "支持的图片格式",
                    "type": "list",
                    "options": ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif", "*.tiff"]
                }
            }
        }
    
    def load_settings(self) -> bool:
        """加载设置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self._merge_settings(saved_settings)
                return True
            else:
                # 首次运行，创建默认配置文件
                self.save_settings()
                return False
        except Exception as e:
            print(f"⚠️  加载设置文件失败: {str(e)}，使用默认设置")
            return False
    
    def _merge_settings(self, saved_settings: Dict[str, Any]) -> None:
        """合并保存的设置到当前设置"""
        for category, params in saved_settings.items():
            if category in self.current_settings:
                for param_name, param_data in params.items():
                    if param_name in self.current_settings[category]:
                        # 只更新value字段，保持其他元数据不变
                        if isinstance(param_data, dict) and 'value' in param_data:
                            self.current_settings[category][param_name]['value'] = param_data['value']
                        else:
                            # 兼容旧格式
                            self.current_settings[category][param_name]['value'] = param_data
    
    def save_settings(self) -> bool:
        """保存设置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 保存设置文件失败: {str(e)}")
            return False
    
    def reset_settings(self) -> bool:
        """重置所有设置为默认值"""
        self.current_settings = self.default_settings.copy()
        return self.save_settings()
    
    def get_value(self, category: str, param_name: str) -> Any:
        """获取参数值"""
        try:
            return self.current_settings[category][param_name]['value']
        except KeyError:
            # 如果参数不存在，返回默认值
            try:
                return self.default_settings[category][param_name]['value']
            except KeyError:
                return None
    
    def set_value(self, category: str, param_name: str, value: Any) -> bool:
        """设置参数值"""
        try:
            if self.validate_value(category, param_name, value):
                self.current_settings[category][param_name]['value'] = value
                return True
            return False
        except KeyError:
            print(f"❌ 参数不存在: {category}.{param_name}")
            return False
    
    def is_critical_parameter(self, category: str, param_name: str) -> bool:
        """判断是否为关键参数，需要二次确认"""
        critical_params = {
            'basic': ['base_url', 'default_password', 'max_workers'],
            'browser': ['headless_mode'],
            'timing': ['login_wait_time'],
            'image': ['output_dir']
        }
        
        return param_name in critical_params.get(category, [])
    
    def get_parameter_warning(self, category: str, param_name: str) -> str:
        """获取参数修改警告信息"""
        warnings = {
            ('basic', 'base_url'): '⚠️  修改网站地址将影响所有登录和上传功能！',
            ('basic', 'default_password'): '⚠️  修改默认密码将影响所有学生的自动登录！',
            ('basic', 'max_workers'): '⚠️  修改线程数可能影响系统性能和稳定性！',
            ('browser', 'headless_mode'): '⚠️  修改无头模式将改变浏览器显示方式！',
            ('timing', 'login_wait_time'): '⚠️  修改登录等待时间可能导致登录失败！',
            ('image', 'output_dir'): '⚠️  修改输出目录将影响图片保存位置！'
        }
        
        return warnings.get((category, param_name), '')
    
    def validate_value(self, category: str, param_name: str, value: Any) -> bool:
        """验证参数值"""
        try:
            param_config = self.current_settings[category][param_name]
            param_type = param_config.get('type', 'string')
            
            # 类型检查
            if param_type == 'int' and not isinstance(value, int):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    return False
            elif param_type == 'bool' and not isinstance(value, bool):
                return False
            elif param_type == 'string' and not isinstance(value, str):
                return False
            elif param_type == 'list' and not isinstance(value, list):
                return False
            
            # 范围检查
            if param_type == 'int':
                min_val = param_config.get('min')
                max_val = param_config.get('max')
                if min_val is not None and value < min_val:
                    return False
                if max_val is not None and value > max_val:
                    return False
            
            # 字符串长度检查
            elif param_type == 'string':
                min_len = param_config.get('min_length')
                max_len = param_config.get('max_length')
                if min_len is not None and len(value) < min_len:
                    return False
                if max_len is not None and len(value) > max_len:
                    return False
            
            return True
            
        except KeyError:
            return False
    
    def get_all_categories(self) -> list:
        """获取所有设置分类"""
        return list(self.current_settings.keys())
    
    def get_category_params(self, category: str) -> Dict[str, Any]:
        """获取指定分类的所有参数"""
        return self.current_settings.get(category, {})
    
    def backup_settings(self, backup_file: str = None) -> bool:
        """备份当前设置"""
        if backup_file is None:
            backup_file = f"{self.config_file}.backup"
        
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 备份设置失败: {str(e)}")
            return False
    
    def restore_settings(self, backup_file: str = None) -> bool:
        """从备份恢复设置"""
        if backup_file is None:
            backup_file = f"{self.config_file}.backup"
        
        try:
            if os.path.exists(backup_file):
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_settings = json.load(f)
                    self._merge_settings(backup_settings)
                    return self.save_settings()
            return False
        except Exception as e:
            print(f"❌ 恢复设置失败: {str(e)}")
            return False 