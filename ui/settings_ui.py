#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置界面
提供美化的参数配置界面
"""

import sys
import os
from typing import Dict, Any, List
from config.settings_manager import SettingsManager

class SettingsUI:
    """设置界面"""
    __slots__ = ['settings_manager', 'category_names']
    
    def __init__(self):
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
            self._print_header()
            self._print_main_menu()
            
            choice = input("\n请选择操作 (0-7): ").strip()
            
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
            else:
                print("请输入有效选项 (0-7)")
                input("按Enter键继续...")
    
    def _print_header(self):
        """打印界面头部"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("+" + "=" * 68 + "+")
        print("|" + " " * 23 + "系统参数设置中心" + " " * 23 + "|")
        print("|" + " " * 68 + "|")
        print("|" + " " * 18 + "美化界面 | 实时验证 | 持久保存" + " " * 18 + "|")
        print("+" + "=" * 68 + "+")
    
    def _print_main_menu(self):
        """打印主菜单"""
        menu = """
+----------------------------------------------------------------------+
|                           设置操作菜单                               |
+----------------------------------------------------------------------+
|  1. 查看所有设置                 |  5. 备份当前设置                  |
|  2. 按分类编辑设置               |  6. 恢复备份设置                  |
|  3. 编辑单个参数                 |  7. 查看配置文件信息              |
|  4. 重置为默认设置               |  0. 返回主菜单                    |
+----------------------------------------------------------------------+"""
        print(menu)
    
    def _show_all_settings(self):
        """显示所有设置"""
        self._print_header()
        print("\n📋 当前所有设置参数")
        print("=" * 70)
        
        for category_key in self.settings_manager.get_all_categories():
            self._print_category_settings(category_key, show_header=True)
        
        input("\n按Enter键返回菜单...")
    
    def _show_category_settings(self):
        """按分类显示设置"""
        self._print_header()
        print("\n🎯 选择要编辑的设置分类")
        print("=" * 40)
        
        categories = self.settings_manager.get_all_categories()
        
        for i, category_key in enumerate(categories, 1):
            category_name = self.category_names.get(category_key, category_key)
            param_count = len(self.settings_manager.get_category_params(category_key))
            print(f"  {i}. {category_name} ({param_count} 个参数)")
        
        print(f"  0. 🔙 返回菜单")
        
        while True:
            try:
                choice = input(f"\n请选择分类 (0-{len(categories)}): ").strip()
                choice_num = int(choice)
                
                if choice_num == 0:
                    return
                elif 1 <= choice_num <= len(categories):
                    selected_category = categories[choice_num - 1]
                    self._edit_category_settings(selected_category)
                    return
                else:
                    print(f"⚠️  请输入 0-{len(categories)} 之间的数字")
            except ValueError:
                print("⚠️  请输入有效数字")
    
    def _edit_category_settings(self, category_key: str):
        """编辑分类设置"""
        while True:
            self._print_header()
            category_name = self.category_names.get(category_key, category_key)
            print(f"\n{category_name} 参数编辑")
            print("=" * 50)
            
            params = self.settings_manager.get_category_params(category_key)
            param_list = list(params.keys())
            
            for i, param_name in enumerate(param_list, 1):
                param_config = params[param_name]
                current_value = param_config['value']
                description = param_config['description']
                param_type = param_config.get('type', 'string')
                
                # 格式化显示值
                if param_type == 'bool':
                    display_value = "[是]" if current_value else "[否]"
                elif param_type == 'list':
                    display_value = f"[{', '.join(current_value)}]"
                else:
                    display_value = str(current_value)
                
                # 标识关键参数
                if self.settings_manager.is_critical_parameter(category_key, param_name):
                    print(f"  {i:2d}. [关键] {description:<20} : {display_value}")
                else:
                    print(f"  {i:2d}. {description:<25} : {display_value}")
                
                # 显示范围信息
                if param_type == 'int':
                    min_val = param_config.get('min')
                    max_val = param_config.get('max')
                    if min_val is not None and max_val is not None:
                        print(f"      └─ 范围: {min_val}-{max_val}")
            
            print(f"   0. 🔙 返回上级菜单")
            
            try:
                choice = input(f"\n请选择要编辑的参数 (0-{len(param_list)}): ").strip()
                choice_num = int(choice)
                
                if choice_num == 0:
                    return
                elif 1 <= choice_num <= len(param_list):
                    selected_param = param_list[choice_num - 1]
                    self._edit_single_param(category_key, selected_param)
                else:
                    print(f"⚠️  请输入 0-{len(param_list)} 之间的数字")
                    input("按Enter键继续...")
            except ValueError:
                print("⚠️  请输入有效数字")
                input("按Enter键继续...")
    
    def _edit_single_parameter(self):
        """编辑单个参数（快速模式）"""
        self._print_header()
        print("\n✏️  快速编辑单个参数")
        print("=" * 30)
        print("💡 格式: 分类.参数名 = 新值")
        print("💡 示例: basic.max_workers = 8")
        print("💡 输入 'list' 查看所有可用参数")
        print()
        
        while True:
            user_input = input("请输入 (或输入 'back' 返回): ").strip()
            
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
                                print(f"\n{warning}")
                            
                            param_config = self.settings_manager.get_category_params(category)[param_name]
                            current_value = param_config['value']
                            description = param_config['description']
                            
                            print(f"\n⚠️  您正在修改关键参数: {description}")
                            print(f"当前值: {current_value}")
                            print(f"新值: {new_value}")
                            
                            confirm = input("\n确认要修改这个关键参数吗？(输入 'YES' 确认): ").strip()
                            if confirm != 'YES':
                                print("❌ 参数修改已取消")
                                continue
                        
                        if self._update_parameter(category, param_name, new_value):
                            print("✅ 参数更新成功！")
                            
                            # 对关键参数显示额外提示
                            if self.settings_manager.is_critical_parameter(category, param_name):
                                print("💡 关键参数已修改，建议备份当前配置")
                        else:
                            print("❌ 参数更新失败，请检查格式和范围")
                    else:
                        print("⚠️  格式错误，请使用 '分类.参数名 = 值' 格式")
                else:
                    print("⚠️  格式错误，请使用 '分类.参数名 = 值' 格式")
            except Exception as e:
                print(f"❌ 输入处理错误: {str(e)}")
    
    def _edit_single_param(self, category: str, param_name: str):
        """编辑单个参数"""
        param_config = self.settings_manager.get_category_params(category)[param_name]
        current_value = param_config['value']
        description = param_config['description']
        param_type = param_config.get('type', 'string')
        
        print(f"\n📝 编辑参数: {description}")
        print("-" * 40)
        print(f"当前值: {current_value}")
        print(f"类型: {param_type}")
        
        # 显示范围或选项信息
        if param_type == 'int':
            min_val = param_config.get('min')
            max_val = param_config.get('max')
            if min_val is not None and max_val is not None:
                print(f"范围: {min_val} - {max_val}")
        elif param_type == 'bool':
            print("可选值: true/false, 1/0, yes/no")
        elif param_type == 'list':
            options = param_config.get('options', [])
            if options:
                print(f"可选项: {', '.join(options)}")
        
        new_value = input(f"\n请输入新值 (Enter键取消): ").strip()
        
        if new_value:
            # 检查是否为关键参数，需要二次确认
            if self.settings_manager.is_critical_parameter(category, param_name):
                warning = self.settings_manager.get_parameter_warning(category, param_name)
                if warning:
                    print(f"\n{warning}")
                
                print(f"\n⚠️  您正在修改关键参数: {description}")
                print(f"当前值: {current_value}")
                print(f"新值: {new_value}")
                
                confirm = input("\n确认要修改这个关键参数吗？(输入 'YES' 确认): ").strip()
                if confirm != 'YES':
                    print("❌ 参数修改已取消")
                    input("按Enter键继续...")
                    return
            
            if self._update_parameter(category, param_name, new_value):
                print("✅ 参数更新成功！")
                self.settings_manager.save_settings()
                
                # 对关键参数显示额外提示
                if self.settings_manager.is_critical_parameter(category, param_name):
                    print("💡 关键参数已修改，建议备份当前配置")
            else:
                print("❌ 参数更新失败，请检查格式和范围")
        
        input("按Enter键继续...")
    
    def _update_parameter(self, category: str, param_name: str, new_value: str) -> bool:
        """更新参数值"""
        try:
            param_config = self.settings_manager.get_category_params(category).get(param_name)
            if not param_config:
                print(f"❌ 参数不存在: {category}.{param_name}")
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
            print(f"❌ 值转换错误: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ 更新参数时发生错误: {str(e)}")
            return False
    
    def _print_category_settings(self, category_key: str, show_header: bool = False):
        """打印分类设置"""
        category_name = self.category_names.get(category_key, category_key)
        params = self.settings_manager.get_category_params(category_key)
        
        if show_header:
            print(f"\n{category_name}")
            print("-" * 50)
        
        for param_name, param_config in params.items():
            value = param_config['value']
            description = param_config['description']
            param_type = param_config.get('type', 'string')
            
            # 格式化显示
            if param_type == 'bool':
                display_value = "[启用]" if value else "[禁用]"
            elif param_type == 'list':
                display_value = f"[{', '.join(str(v) for v in value)}]"
            else:
                display_value = str(value)
            
            # 标识关键参数
            if self.settings_manager.is_critical_parameter(category_key, param_name):
                print(f"  🔐 [关键] {description:<20} : {display_value}")
            else:
                print(f"  * {description:<25} : {display_value}")
    
    def _print_all_parameter_paths(self):
        """打印所有参数路径"""
        print("\n📋 所有可用参数:")
        print("-" * 40)
        
        for category_key in self.settings_manager.get_all_categories():
            category_name = self.category_names.get(category_key, category_key)
            print(f"\n{category_name}:")
            
            params = self.settings_manager.get_category_params(category_key)
            for param_name, param_config in params.items():
                description = param_config['description']
                param_type = param_config.get('type', 'string')
                print(f"  {category_key}.{param_name} ({param_type}) - {description}")
    
    def _reset_settings(self):
        """重置设置"""
        print("\n🔧 重置设置为默认值")
        print("=" * 30)
        print("⚠️  此操作将清除所有自定义设置！")
        
        choice = input("确认重置？(输入 'YES' 确认): ").strip()
        if choice == 'YES':
            if self.settings_manager.reset_settings():
                print("✅ 设置已重置为默认值")
            else:
                print("❌ 重置失败")
        else:
            print("❌ 重置已取消")
        
        input("按Enter键继续...")
    
    def _backup_settings(self):
        """备份设置"""
        print("\n💾 备份当前设置")
        print("=" * 20)
        
        backup_file = input("备份文件名 (Enter使用默认): ").strip()
        if not backup_file:
            backup_file = None
        
        if self.settings_manager.backup_settings(backup_file):
            backup_name = backup_file or f"{self.settings_manager.config_file}.backup"
            print(f"✅ 设置已备份到: {backup_name}")
        else:
            print("❌ 备份失败")
        
        input("按Enter键继续...")
    
    def _restore_settings(self):
        """恢复设置"""
        print("\n🔄 恢复备份设置")
        print("=" * 20)
        
        backup_file = input("备份文件名 (Enter使用默认): ").strip()
        if not backup_file:
            backup_file = None
        
        if self.settings_manager.restore_settings(backup_file):
            print("✅ 设置已从备份恢复")
        else:
            print("❌ 恢复失败，请检查备份文件是否存在")
        
        input("按Enter键继续...")
    
    def _show_settings_file_info(self):
        """显示配置文件信息"""
        print("\n📄 配置文件信息")
        print("=" * 25)
        
        config_file = self.settings_manager.config_file
        if os.path.exists(config_file):
            file_size = os.path.getsize(config_file)
            file_time = os.path.getmtime(config_file)
            
            from datetime import datetime
            mod_time = datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"📁 文件路径: {os.path.abspath(config_file)}")
            print(f"📏 文件大小: {file_size} 字节")
            print(f"🕒 修改时间: {mod_time}")
            print(f"📊 参数分类: {len(self.settings_manager.get_all_categories())} 个")
            
            total_params = sum(len(self.settings_manager.get_category_params(cat)) 
                             for cat in self.settings_manager.get_all_categories())
            print(f"🔢 参数总数: {total_params} 个")
        else:
            print("❌ 配置文件不存在")
        
        backup_file = f"{config_file}.backup"
        if os.path.exists(backup_file):
            print(f"💾 备份文件: 存在")
        else:
            print(f"💾 备份文件: 不存在")
        
        input("按Enter键继续...") 