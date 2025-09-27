#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进版批量上传程序
功能：批量处理学生文件上传到指定网站
改进：模块化、异常处理、进度显示、自动线程优化
"""

import os
import sys
import argparse
import concurrent.futures
from config.config import Config
from core.browser_manager import BrowserPositionManager, BrowserManager
from utils.file_manager import FileManager
from utils.progress_tracker import ProgressTracker, ThreadMonitor
from core.student_processor import StudentProcessor
from utils.report_generator import ReportGenerator
from utils.exceptions import ExcelReadException

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='批量学生文件上传程序')
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=Config.DEFAULT_MAX_WORKERS,
        help=f'线程数 (默认: {Config.DEFAULT_MAX_WORKERS}, 范围: {Config.MIN_WORKERS}-{Config.MAX_WORKERS})'
    )
    parser.add_argument(
        '--excel-file', '-e',
        type=str,
        help='指定Excel文件路径 (默认: 自动查找当前目录下的Excel文件)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细输出'
    )
    
    return parser.parse_args()

def print_system_info():
    """打印系统信息"""
    print(f"🖥️  系统信息:")
    print(f"   Python版本: {sys.version.split()[0]}")
    print(f"   CPU核心数: {os.cpu_count()}")
    print(f"   默认线程数: {Config.DEFAULT_MAX_WORKERS}")
    print(f"   屏幕分辨率: {Config.SCREEN_WIDTH}x{Config.SCREEN_HEIGHT}")
    print(f"   浏览器窗口: {Config.BROWSER_WIDTH}x{Config.BROWSER_HEIGHT}")
    print(f"   窗口布局: {Config.WINDOW_COLS}列 x {Config.WINDOW_ROWS}行")
    print(f"{'='*60}")

def main():
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 验证线程数
        max_workers = Config.validate_max_workers(args.workers)
        if max_workers != args.workers:
            print(f"⚠️  线程数已调整为: {max_workers} (原设置: {args.workers})")
        
        # 打印系统信息
        print_system_info()
        
        # 查找Excel文件
        current_dir = Config.get_current_dir()
        if args.excel_file:
            excel_file = args.excel_file
            if not os.path.exists(excel_file):
                print(f"❌ 指定的Excel文件不存在: {excel_file}")
                return 1
        else:
            data_dir = os.path.join(current_dir, "data")
            excel_file = FileManager.find_excel_file(data_dir)
            if not excel_file:
                print("❌ 未找到Excel文件！请确保当前目录下有Excel文件。")
                return 1
        
        print(f"📋 使用Excel文件: {excel_file}")
        
        # 读取Excel文件
        try:
            df = FileManager.read_excel_file(excel_file)
            students_data = FileManager.prepare_student_data(df)
            print(f"📊 共找到 {len(students_data)} 名学生")
            
            if len(students_data) == 0:
                print("⚠️  没有有效的学生数据，程序退出")
                return 1
                
        except ExcelReadException as e:
            print(f"❌ {str(e)}")
            return 1
        
        # 初始化组件
        print(f"🚀 开始处理，使用 {max_workers} 个线程...")
        
        position_manager = BrowserPositionManager()
        browser_manager = BrowserManager(position_manager)
        progress_tracker = ProgressTracker(len(students_data))
        thread_monitor = ThreadMonitor(max_workers)
        student_processor = StudentProcessor(browser_manager, progress_tracker)
        
        # 处理学生数据
        def process_with_monitoring(student_data):
            """带监控的学生处理函数"""
            thread_monitor.thread_started()
            try:
                student_processor.process_student(student_data)
            finally:
                thread_monitor.thread_finished()
        
        # 使用线程池处理
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = [
                executor.submit(process_with_monitoring, student_data) 
                for student_data in students_data
            ]
            
            # 等待所有任务完成
            try:
                concurrent.futures.wait(futures)
            except KeyboardInterrupt:
                print("\n\n⚠️  收到中断信号，正在安全停止...")
                executor.shutdown(wait=True)
                progress_tracker.close()
                return 1
        
        # 关闭进度跟踪
        progress_tracker.close()
        
        # 生成报告
        results = progress_tracker.get_results()
        ReportGenerator.print_summary(results)
        report_file = ReportGenerator.generate_report(results)
        
        if report_file:
            print(f"📄 详细报告: {report_file}")
        
        print("🎉 所有学生处理完成！")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  程序被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 程序运行时发生未预期错误: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 