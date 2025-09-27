import threading
import time
from datetime import datetime
from tqdm import tqdm
from config.config import Config

class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self, total_students):
        self.total_students = total_students
        self.completed = 0
        self.failed = 0
        self.pending_review = 0
        self.already_completed = 0
        self.newly_submitted = 0
        
        self.lock = threading.Lock()
        self.start_time = datetime.now()
        
        # 创建进度条
        self.pbar = tqdm(
            total=total_students,
            desc="处理进度",
            unit="学生",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )
        
        # 结果存储
        self.results = {
            'pending_review': [],
            'completed': [],
            'newly_submitted': [],
            'failed': []
        }
    
    def update_progress(self, student_name, status, student_info=None):
        """更新进度"""
        with self.lock:
            if status == 'completed':
                self.completed += 1
                self.already_completed += 1
                if student_info:
                    self.results['completed'].append(student_info)
            elif status == 'pending_review':
                self.completed += 1
                self.pending_review += 1
                if student_info:
                    self.results['pending_review'].append(student_info)
            elif status == 'newly_submitted':
                self.completed += 1
                self.newly_submitted += 1
                if student_info:
                    self.results['newly_submitted'].append(student_info)
            elif status == 'failed':
                self.completed += 1
                self.failed += 1
                if student_info:
                    self.results['failed'].append(student_info)
            
            # 更新进度条
            self.pbar.update(1)
            
            # 更新进度条描述
            elapsed_time = datetime.now() - self.start_time
            elapsed_seconds = elapsed_time.total_seconds()
            
            if self.completed > 0:
                avg_time_per_student = elapsed_seconds / self.completed
                remaining_students = self.total_students - self.completed
                estimated_remaining = avg_time_per_student * remaining_students
                
                self.pbar.set_postfix({
                    '已完成': self.already_completed,
                    '待审核': self.pending_review,
                    '新提交': self.newly_submitted,
                    '失败': self.failed,
                    '预计剩余': f"{estimated_remaining/60:.1f}分钟"
                })
    
    def print_status(self, message):
        """打印状态信息（不影响进度条）"""
        self.pbar.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def close(self):
        """关闭进度条"""
        self.pbar.close()
        
        # 打印最终统计
        elapsed_time = datetime.now() - self.start_time
        print(f"\n{'='*60}")
        print(f"处理完成！总耗时: {elapsed_time}")
        print(f"{'='*60}")
        print(f"总学生数: {self.total_students}")
        print(f"已完成: {self.already_completed} 人")
        print(f"待审核: {self.pending_review} 人")
        print(f"新提交: {self.newly_submitted} 人")
        print(f"失败: {self.failed} 人")
        print(f"成功率: {((self.completed - self.failed) / self.total_students * 100):.1f}%")
        print(f"{'='*60}")
    
    def get_results(self):
        """获取处理结果"""
        return self.results

class ThreadMonitor:
    """线程监控器"""
    
    def __init__(self, max_workers):
        self.max_workers = max_workers
        self.active_threads = 0
        self.lock = threading.Lock()
    
    def thread_started(self):
        """线程开始"""
        with self.lock:
            self.active_threads += 1
    
    def thread_finished(self):
        """线程结束"""
        with self.lock:
            self.active_threads -= 1
    
    def get_active_count(self):
        """获取活跃线程数"""
        with self.lock:
            return self.active_threads
    
    def print_thread_info(self):
        """打印线程信息"""
        return f"活跃线程: {self.get_active_count()}/{self.max_workers}" 