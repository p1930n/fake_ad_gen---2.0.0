#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rich版本设置界面
"""

from ui.rich_ui import RichUI
from config.settings_manager import SettingsManager

class RichSettingsUI:
    """Rich版本设置界面"""
    
    def __init__(self):
        self.ui = RichUI()
        self.settings_manager = SettingsManager()
        self.category_names = {
            'basic': '🔧 基础设置',
            'browser': '🌐 浏览器设置', 
            'timing': '⏱️  时间设置',
            'image': '🖼️  图片设置',
            'file': '📁 文件设置'
        }
    
    def show_settings_menu(self) -> int:
        """显示设置主菜单"""
        while True:
            self.ui.clear_screen()
            
            # 主菜单选项
            menu_items = [
                ("1", "📋 查看所有设置"),
                ("2", "🎯 按分类编辑设置"),
                ("3", "✏️  编辑单个参数"),
                ("4", "🔧 重置为默认设置"),
                ("5", "💾 备份当前设置"),
                ("6", "🔄 恢复备份设置"),
                ("7", "📄 查看配置文件信息"),
                ("0", "🔙 返回主菜单")
            ]
            
            choice = self.ui.print_submenu("设置操作菜单", menu_items)
            
            if choice == '0':
                return 0
            elif choice == '1':
                self._show_all_settings()
            elif choice == '2':
                self._show_category_settings()
            elif choice == '3':
                self._edit_single_parameter()
            elif choice == '4':
                self._reset_settings()
            elif choice == '5':
                self._backup_settings()
            elif choice == '6':
                self._restore_settings()
            elif choice == '7':
                self._show_settings_file_info()
    
    def _show_all_settings(self):
        """显示所有设置"""
        self.ui.show_info("所有设置参数")
        
        for category_key in self.settings_manager.get_all_categories():
            category_name = self.category_names.get(category_key, category_key)
            self.ui.show_info(f"\n{category_name}")
            
            params = self.settings_manager.get_category_params(category_key)
            for param_name, param_config in params.items():
                value = param_config['value']
                description = param_config['description']
                param_type = param_config.get('type', 'string')
                
                if param_type == 'bool':
                    display_value = "[启用]" if value else "[禁用]"
                elif param_type == 'list':
                    display_value = f"[{', '.join(str(v) for v in value)}]"
                else:
                    display_value = str(value)
                
                print(f"  * {description:<25} : {display_value}")
        
        self.ui.pause()
    
    def _show_category_settings(self):
        """按分类显示设置"""
        categories = self.settings_manager.get_all_categories()
        
        # 创建分类选择菜单
        category_items = []
        for i, category_key in enumerate(categories, 1):
            category_name = self.category_names.get(category_key, category_key)
            param_count = len(self.settings_manager.get_category_params(category_key))
            category_items.append((str(i), f"{category_name} ({param_count} 个参数)"))
        
        category_items.append(("0", "🔙 返回菜单"))
        
        choice = self.ui.print_submenu("选择要编辑的设置分类", category_items)
        
        if choice != "0":
            try:
                choice_num = int(choice) - 1
                if 0 <= choice_num < len(categories):
                    selected_category = categories[choice_num]
                    self._edit_category_settings(selected_category)
            except ValueError:
                pass
    
    def _edit_category_settings(self, category_key: str):
        """编辑分类设置"""
        while True:
            self.ui.clear_screen()
            category_name = self.category_names.get(category_key, category_key)
            
            params = self.settings_manager.get_category_params(category_key)
            param_list = list(params.keys())
            
            # 创建参数编辑菜单
            param_items = []
            for i, param_name in enumerate(param_list, 1):
                param_config = params[param_name]
                current_value = param_config['value']
                description = param_config['description']
                param_type = param_config.get('type', 'string')
                
                # 格式化显示值
                if param_type == 'bool':
                    display_value = "✅ 是" if current_value else "❌ 否"
                elif param_type == 'list':
                    display_value = f"[{', '.join(current_value)}]"
                else:
                    display_value = str(current_value)
                
                # 标识关键参数
                if self.settings_manager.is_critical_parameter(category_key, param_name):
                    param_label = f"🔐 {description}: {display_value}"
                else:
                    param_label = f"{description}: {display_value}"
                
                param_items.append((str(i), param_label))
            
            param_items.append(("0", "🔙 返回上级菜单"))
            
            choice = self.ui.print_submenu(f"{category_name} 参数编辑", param_items)
            
            if choice == "0":
                return
            
            try:
                choice_num = int(choice) - 1
                if 0 <= choice_num < len(param_list):
                    selected_param = param_list[choice_num]
                    self._edit_single_param(category_key, selected_param)
            except ValueError:
                pass
    
    def _edit_single_param(self, category: str, param_name: str):
        """编辑单个参数"""
        param_config = self.settings_manager.get_category_params(category)[param_name]
        current_value = param_config['value']
        description = param_config['description']
        param_type = param_config.get('type', 'string')
        
        self.ui.show_info(f"编辑参数: {description}")
        self.ui.show_info(f"当前值: {current_value}")
        self.ui.show_info(f"类型: {param_type}")
        
        # 显示范围或选项信息
        if param_type == 'int':
            min_val = param_config.get('min')
            max_val = param_config.get('max')
            if min_val is not None and max_val is not None:
                self.ui.show_info(f"范围: {min_val} - {max_val}")
        elif param_type == 'bool':
            self.ui.show_info("可选值: true/false, 1/0, yes/no")
        elif param_type == 'list':
            options = param_config.get('options', [])
            if options:
                self.ui.show_info(f"可选项: {', '.join(options)}")
        
        new_value = self.ui.input_text("请输入新值 (Enter键取消)")
        
        if new_value:
            # 检查是否为关键参数，需要二次确认
            if self.settings_manager.is_critical_parameter(category, param_name):
                warning = self.settings_manager.get_parameter_warning(category, param_name)
                if warning:
                    self.ui.show_warning(warning)
                
                self.ui.show_warning(f"您正在修改关键参数: {description}")
                self.ui.show_info(f"当前值: {current_value}")
                self.ui.show_info(f"新值: {new_value}")
                
                if not self.ui.confirm("确认要修改这个关键参数吗？"):
                    self.ui.show_info("参数修改已取消")
                    self.ui.pause()
                    return
            
            if self._update_parameter(category, param_name, new_value):
                self.ui.show_success("参数更新成功！")
                self.settings_manager.save_settings()
                
                # 对关键参数显示额外提示
                if self.settings_manager.is_critical_parameter(category, param_name):
                    self.ui.show_info("关键参数已修改，建议备份当前配置")
            else:
                self.ui.show_error("参数更新失败，请检查格式和范围")
        
        self.ui.pause()
    
    def _update_parameter(self, category: str, param_name: str, new_value: str) -> bool:
        """更新参数值"""
        try:
            param_config = self.settings_manager.get_category_params(category).get(param_name)
            if not param_config:
                self.ui.show_error(f"参数不存在: {category}.{param_name}")
                return False
                
            param_type = param_config.get('type', 'string')
            
            # 类型转换
            if param_type == 'int':
                converted_value = int(new_value)
            elif param_type == 'bool':
                converted_value = new_value.lower() in ['true', '1', 'yes', 'on', '是', 'y']
            elif param_type == 'list':
                # 简单的列表解析，支持逗号分隔
                converted_value = [item.strip() for item in new_value.split(',')]
            else:
                converted_value = new_value
            
            # 验证并设置
            return self.settings_manager.set_value(category, param_name, converted_value)
            
        except ValueError as e:
            self.ui.show_error(f"值转换错误: {str(e)}")
            return False
        except Exception as e:
            self.ui.show_error(f"更新参数时发生错误: {str(e)}")
            return False
    
    def _edit_single_parameter(self):
        """编辑单个参数（快速模式）"""
        self.ui.show_info("快速编辑单个参数")
        self.ui.show_info("格式: 分类.参数名 = 新值")
        self.ui.show_info("示例: basic.max_workers = 8")
        self.ui.show_info("输入 'list' 查看所有可用参数")
        
        while True:
            user_input = self.ui.input_text("请输入 (或输入 'back' 返回)")
            
            if user_input.lower() in ['back', 'exit', '返回']:
                return
            elif user_input.lower() == 'list':
                self._print_all_parameter_paths()
                continue
            
            try:
                if '=' in user_input:
                    param_path, new_value = user_input.split('=', 1)
                    param_path = param_path.strip()
                    new_value = new_value.strip()
                    
                    if '.' in param_path:
                        category, param_name = param_path.split('.', 1)
                        category = category.strip()
                        param_name = param_name.strip()
                        
                        # 检查是否为关键参数
                        if self.settings_manager.is_critical_parameter(category, param_name):
                            warning = self.settings_manager.get_parameter_warning(category, param_name)
                            if warning:
                                self.ui.show_warning(warning)
                            
                            param_config = self.settings_manager.get_category_params(category)[param_name]
                            current_value = param_config['value']
                            description = param_config['description']
                            
                            self.ui.show_warning(f"您正在修改关键参数: {description}")
                            self.ui.show_info(f"当前值: {current_value}")
                            self.ui.show_info(f"新值: {new_value}")
                            
                            if not self.ui.confirm("确认要修改这个关键参数吗？"):
                                self.ui.show_info("参数修改已取消")
                                continue
                        
                        if self._update_parameter(category, param_name, new_value):
                            self.ui.show_success("参数更新成功！")
                            self.settings_manager.save_settings()
                            
                            # 对关键参数显示额外提示
                            if self.settings_manager.is_critical_parameter(category, param_name):
                                self.ui.show_info("关键参数已修改，建议备份当前配置")
                        else:
                            self.ui.show_error("参数更新失败，请检查格式和范围")
                    else:
                        self.ui.show_error("格式错误，请使用 '分类.参数名 = 值' 格式")
                else:
                    self.ui.show_error("格式错误，请使用 '分类.参数名 = 值' 格式")
            except Exception as e:
                self.ui.show_error(f"输入处理错误: {str(e)}")
    
    def _print_all_parameter_paths(self):
        """打印所有参数路径"""
        self.ui.show_info("所有可用参数:")
        
        for category_key in self.settings_manager.get_all_categories():
            category_name = self.category_names.get(category_key, category_key)
            self.ui.show_info(f"\n{category_name}:")
            
            params = self.settings_manager.get_category_params(category_key)
            for param_name, param_config in params.items():
                description = param_config['description']
                param_type = param_config.get('type', 'string')
                print(f"  {category_key}.{param_name} ({param_type}) - {description}")
    
    def _reset_settings(self):
        """重置设置"""
        self.ui.show_warning("重置设置为默认值")
        self.ui.show_warning("此操作将清除所有自定义设置！")
        
        if self.ui.confirm("确认重置"):
            if self.settings_manager.reset_settings():
                self.ui.show_success("设置已重置为默认值")
            else:
                self.ui.show_error("重置失败")
        else:
            self.ui.show_info("重置已取消")
        
        self.ui.pause()
    
    def _backup_settings(self):
        """备份设置"""
        self.ui.show_info("备份当前设置")
        
        backup_file = self.ui.input_text("备份文件名 (Enter使用默认)")
        if not backup_file:
            backup_file = None
        
        if self.settings_manager.backup_settings(backup_file):
            backup_name = backup_file or f"{self.settings_manager.config_file}.backup"
            self.ui.show_success(f"设置已备份到: {backup_name}")
        else:
            self.ui.show_error("备份失败")
        
        self.ui.pause()
    
    def _restore_settings(self):
        """恢复设置"""
        self.ui.show_info("恢复备份设置")
        
        backup_file = self.ui.input_text("备份文件名 (Enter使用默认)")
        if not backup_file:
            backup_file = None
        
        if self.settings_manager.restore_settings(backup_file):
            self.ui.show_success("设置已从备份恢复")
        else:
            self.ui.show_error("恢复失败，请检查备份文件是否存在")
        
        self.ui.pause()
    
    def _show_settings_file_info(self):
        """显示配置文件信息"""
        import os
        from datetime import datetime
        
        self.ui.show_info("配置文件信息")
        
        config_file = self.settings_manager.config_file
        if os.path.exists(config_file):
            file_size = os.path.getsize(config_file)
            file_time = os.path.getmtime(config_file)
            mod_time = datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S')
            
            self.ui.show_info(f"文件路径: {os.path.abspath(config_file)}")
            self.ui.show_info(f"文件大小: {file_size} 字节")
            self.ui.show_info(f"修改时间: {mod_time}")
            self.ui.show_info(f"参数分类: {len(self.settings_manager.get_all_categories())} 个")
            
            total_params = sum(len(self.settings_manager.get_category_params(cat)) 
                             for cat in self.settings_manager.get_all_categories())
            self.ui.show_info(f"参数总数: {total_params} 个")
        else:
            self.ui.show_error("配置文件不存在")
        
        backup_file = f"{config_file}.backup"
        if os.path.exists(backup_file):
            self.ui.show_info("备份文件: 存在")
        else:
            self.ui.show_info("备份文件: 不存在")
        
        self.ui.pause() 