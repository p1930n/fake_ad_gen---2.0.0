#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主菜单系统
提供用户友好的功能选择界面
"""

import os
import sys
from typing import List, Dict, Any
from utils.file_manager import FileManager
from config.config import Config
from ui.rich_ui import RichUI

class MenuSystem:
    """主菜单系统"""
    
    def __init__(self):
        self.students_data = []
        self.excel_file = None
        self.ui = RichUI()
        
    def print_banner(self):
        """打印程序横幅"""
        self.ui.print_banner(os.cpu_count(), Config.DEFAULT_MAX_WORKERS)
    
    def load_student_data(self):
        """加载学生数据"""
        try:
            current_dir = Config.get_current_dir()
            data_dir = os.path.join(current_dir, "data")
            self.excel_file = FileManager.find_excel_file(data_dir)
            
            if not self.excel_file:
                self.ui.show_error("未找到Excel文件！请确保data目录下有Excel文件。")
                return False
            
            self.ui.show_info(f"找到Excel文件: {os.path.basename(self.excel_file)}")
            
            df = FileManager.read_excel_file(self.excel_file)
            self.students_data = FileManager.prepare_student_data(df)
            
            self.ui.show_success(f"成功加载 {len(self.students_data)} 名学生数据")
            return True
            
        except Exception as e:
            self.ui.show_error(f"加载学生数据失败: {str(e)}")
            return False
    
    def display_main_menu(self) -> str:
        """显示主菜单并返回用户选择"""
        return self.ui.print_main_menu()
    
    def get_user_choice(self, prompt: str, valid_choices: List[str]) -> str:
        """获取用户选择"""
        while True:
            try:
                choice = input(f"\n{prompt}").strip()
                if choice in valid_choices:
                    return choice
                else:
                    print(f"⚠️  请输入有效选项: {', '.join(valid_choices)}")
            except KeyboardInterrupt:
                print("\n👋 程序已退出")
                sys.exit(0)
    
    def select_students(self, mode: str = "single") -> List[Dict[str, Any]]:
        """选择学生"""
        if not self.students_data:
            self.ui.show_error("没有可用的学生数据")
            return []
        
        return self.ui.show_student_list(self.students_data, mode)
    
    def run(self):
        """运行主菜单系统"""
        self.print_banner()
        
        # 加载学生数据
        if not self.load_student_data():
            return 1
        
        while True:
            choice = self.display_main_menu()
            
            if choice == '0':
                self.ui.show_success("感谢使用，程序已退出！")
                return 0
            
            elif choice == '1':
                self.handle_upload_function()
            
            elif choice == '2':
                self.handle_image_generation()
            
            elif choice == '3':
                self.handle_image_center()
            
            elif choice == '4':
                self.handle_upload_center()
            
            elif choice == '5':
                self.handle_system_settings()
    
    def handle_upload_function(self):
        """处理上传功能"""
        self.ui.show_info("上传指定学生文件")
        
        # 选择学生
        mode_choice = self.ui.input_text("选择模式", "1").strip()
        if mode_choice not in ['1', '2']:
            mode_choice = '1'
        
        selected_students = self.select_students('single' if mode_choice == '1' else 'multiple')
        
        if not selected_students:
            return
        
        # 调用上传功能
        from core.upload_manager import UploadManager
        upload_manager = UploadManager()
        upload_manager.upload_students(selected_students)
    
    def handle_image_generation(self):
        """处理图片生成功能"""
        self.ui.show_info("为指定学生生成图片")
        
        # 选择学生
        mode_choice = self.ui.input_text("选择模式 (1:单个学生 2:多个学生)", "1").strip()
        if mode_choice not in ['1', '2']:
            mode_choice = '1'
        
        selected_students = self.select_students('single' if mode_choice == '1' else 'multiple')
        
        if not selected_students:
            return
        
        # 调用图片生成功能
        from core.image_generator import ImageGenerator
        generator = ImageGenerator()
        generator.generate_for_students(selected_students)
    
    def handle_image_center(self):
        """处理图片生成中心"""
        submenu_items = [
            ("1", "为指定学生生成图片"),
            ("2", "批量图片生成"),
            ("3", "自定义图片模板"),
            ("4", "图片生成设置"),
            ("0", "返回主菜单")
        ]
        
        choice = self.ui.print_submenu("图片生成中心", submenu_items)
        
        if choice == '0':
            return
        elif choice == '1':
            self.handle_image_generation()  # 包含功能2
        elif choice == '2':
            self.handle_batch_image_generation()
        elif choice == '3':
            self.handle_custom_template()
        elif choice == '4':
            self.handle_image_settings()
    
    def handle_upload_center(self):
        """处理文件上传中心"""
        submenu_items = [
            ("1", "上传指定学生文件"),
            ("2", "批量文件上传"),
            ("3", "上传状态监控"),
            ("4", "上传设置"),
            ("0", "返回主菜单")
        ]
        
        choice = self.ui.print_submenu("文件上传中心", submenu_items)
        
        if choice == '0':
            return
        elif choice == '1':
            self.handle_upload_function()  # 包含功能1
        elif choice == '2':
            self.handle_batch_upload()
        elif choice == '3':
            self.handle_upload_monitoring()
        elif choice == '4':
            self.handle_upload_settings()
    
    def handle_batch_image_generation(self):
        """批量图片生成"""
        self.ui.show_warning("批量图片生成功能正在开发中...")
        self.ui.pause()
    
    def handle_custom_template(self):
        """自定义图片模板"""
        self.ui.show_warning("自定义图片模板功能正在开发中...")
        self.ui.pause()
    
    def handle_image_settings(self):
        """图片生成设置"""
        self.ui.show_warning("图片生成设置功能正在开发中...")
        self.ui.pause()
    
    def handle_batch_upload(self):
        """批量文件上传"""
        self.ui.show_warning("批量文件上传功能正在开发中...")
        self.ui.pause()
    
    def handle_upload_monitoring(self):
        """上传状态监控"""
        self.ui.show_warning("上传状态监控功能正在开发中...")
        self.ui.pause()
    
    def handle_upload_settings(self):
        """上传设置"""
        self.ui.show_warning("上传设置功能正在开发中...")
        self.ui.pause()
    
    def handle_system_settings(self):
        """处理系统设置"""
        try:
            from ui.rich_settings_ui import RichSettingsUI
            settings_ui = RichSettingsUI()
            settings_ui.show_settings_menu()
        except ImportError as e:
            self.ui.show_error(f"设置模块导入失败: {str(e)}")
            self.ui.show_info("请确保 settings_ui.py 和 settings_manager.py 文件存在")
            self.ui.pause()
        except Exception as e:
            self.ui.show_error(f"设置界面运行时发生错误: {str(e)}")
            self.ui.pause() 