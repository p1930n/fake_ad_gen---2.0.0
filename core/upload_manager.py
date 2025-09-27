#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传管理模块
管理学生文件的上传功能
"""

import os
import concurrent.futures
from typing import List, Dict, Any
from datetime import datetime
from tqdm import tqdm

from config.config import Config
from core.browser_manager import BrowserPositionManager, BrowserManager
from core.student_processor import StudentProcessor
from utils.progress_tracker import ProgressTracker
from utils.report_generator import ReportGenerator
from utils.file_manager import FileManager
from utils.exceptions import StudentFolderNotFoundException, NoImagesFoundException

class UploadManager:
    """上传管理器"""
    
    def __init__(self):
        self.position_manager = BrowserPositionManager()
        self.browser_manager = BrowserManager(self.position_manager)
    
    def upload_students(self, students: List[Dict[str, Any]], max_workers: int = None):
        """为选定的学生上传文件"""
        if not students:
            print("❌ 没有选定的学生")
            return
        
        # 设置线程数
        if max_workers is None:
            max_workers = min(Config.DEFAULT_MAX_WORKERS, len(students))
        else:
            max_workers = Config.validate_max_workers(max_workers)
        
        print(f"\n📤 开始为 {len(students)} 名学生上传文件...")
        print(f"🔧 使用线程数: {max_workers}")
        
        # 检查学生文件
        valid_students = []
        print("\n🔍 检查学生文件...")
        
        check_progress = tqdm(students, desc="文件检查", unit="学生")
        for student in check_progress:
            check_progress.set_postfix_str(f"检查: {student['name']}")
            
            try:
                # 查找学生文件夹
                current_dir = Config.get_current_dir()
                student_folder = FileManager.find_student_folder(current_dir, student['name'])
                
                # 查找图片文件
                image_files = FileManager.find_images_in_folder(student_folder)
                
                student['folder_path'] = student_folder
                student['image_files'] = image_files
                valid_students.append(student)
                
                check_progress.write(f"✅ {student['name']}: 找到 {len(image_files)} 张图片")
                
            except (StudentFolderNotFoundException, NoImagesFoundException) as e:
                check_progress.write(f"❌ {student['name']}: {str(e)}")
                continue
        
        check_progress.close()
        
        if not valid_students:
            print("❌ 没有找到有效的学生文件，上传终止")
            return
        
        print(f"\n✅ 找到 {len(valid_students)} 名学生的有效文件")
        
        # 询问是否继续
        if len(valid_students) < len(students):
            choice = input(f"⚠️  只有 {len(valid_students)}/{len(students)} 名学生有有效文件，是否继续？(y/N): ").strip().lower()
            if choice not in ['y', 'yes']:
                print("❌ 上传已取消")
                return
        
        # 开始上传
        progress_tracker = ProgressTracker(len(valid_students))
        student_processor = StudentProcessor(self.browser_manager, progress_tracker)
        
        print(f"\n🚀 开始上传处理...")
        
        # 使用线程池处理
        def process_with_monitoring(student_data):
            """带监控的学生处理函数"""
            try:
                student_processor.process_student(student_data)
            except Exception as e:
                progress_tracker.print_status(f"❌ 处理 {student_data['name']} 时发生错误: {str(e)}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = [
                executor.submit(process_with_monitoring, student_data) 
                for student_data in valid_students
            ]
            
            # 等待所有任务完成
            try:
                concurrent.futures.wait(futures)
            except KeyboardInterrupt:
                print("\n\n⚠️  收到中断信号，正在安全停止...")
                executor.shutdown(wait=True)
                progress_tracker.close()
                return
        
        # 关闭进度跟踪
        progress_tracker.close()
        
        # 生成报告
        results = progress_tracker.get_results()
        ReportGenerator.print_summary(results)
        report_file = ReportGenerator.generate_report(results)
        
        if report_file:
            print(f"📄 详细报告: {report_file}")
        
        print("🎉 上传处理完成！")
        input("按Enter键返回主菜单...")
    
    def upload_all_students(self, excel_file: str = None, max_workers: int = None):
        """上传所有学生的文件"""
        try:
            # 读取学生数据
            if excel_file is None:
                current_dir = Config.get_current_dir()
                data_dir = os.path.join(current_dir, "data")
                excel_file = FileManager.find_excel_file(data_dir)
                
                if not excel_file:
                    print("❌ 未找到Excel文件")
                    return
            
            df = FileManager.read_excel_file(excel_file)
            students_data = FileManager.prepare_student_data(df)
            
            if not students_data:
                print("❌ 没有有效的学生数据")
                return
            
            print(f"📊 找到 {len(students_data)} 名学生")
            
            # 确认上传
            choice = input(f"确认为所有 {len(students_data)} 名学生上传文件？(y/N): ").strip().lower()
            if choice not in ['y', 'yes']:
                print("❌ 上传已取消")
                return
            
            # 开始上传
            self.upload_students(students_data, max_workers)
            
        except Exception as e:
            print(f"❌ 批量上传失败: {str(e)}")
    
    def check_upload_status(self, students: List[Dict[str, Any]]):
        """检查学生的上传状态"""
        print(f"\n🔍 检查 {len(students)} 名学生的上传状态...")
        
        # 这里可以实现状态检查逻辑
        # 例如：连接到网站检查每个学生的提交状态
        
        status_results = []
        
        with tqdm(students, desc="状态检查", unit="学生") as pbar:
            for student in students:
                pbar.set_postfix_str(f"检查: {student['name']}")
                
                # 模拟状态检查
                # 实际实现时需要连接到网站查询状态
                import random
                import time
                
                time.sleep(0.5)  # 模拟网络延迟
                
                # 随机生成状态（实际应该从网站获取）
                statuses = ['已完成', '待审核', '未完成', '检查失败']
                status = random.choice(statuses)
                
                status_results.append({
                    '学号': student['student_id'],
                    '姓名': student['name'],
                    '状态': status,
                    '检查时间': datetime.now().strftime(Config.DATETIME_FORMAT)
                })
                
                pbar.update(1)
        
        # 显示结果
        print(f"\n📊 状态检查结果:")
        print("=" * 60)
        
        status_counts = {}
        for result in status_results:
            status = result['状态']
            status_counts[status] = status_counts.get(status, 0) + 1
            print(f"  {result['姓名']:10} ({result['学号']:10}) - {result['状态']}")
        
        print("=" * 60)
        print("📈 统计信息:")
        for status, count in status_counts.items():
            print(f"  {status}: {count} 人")
        
        input("\n按Enter键继续...")
    
    def get_upload_settings(self):
        """获取上传设置"""
        settings = {
            'max_workers': Config.DEFAULT_MAX_WORKERS,
            'browser_width': Config.BROWSER_WIDTH,
            'browser_height': Config.BROWSER_HEIGHT,
            'upload_timeout': Config.LOGIN_WAIT_TIME,
            'retry_count': 3
        }
        return settings
    
    def update_upload_settings(self, **kwargs):
        """更新上传设置"""
        # 这里可以实现设置更新逻辑
        print("⚙️  设置更新功能开发中...")
        pass 