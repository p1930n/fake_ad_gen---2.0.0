from datetime import datetime
from config.config import Config
from core.browser_manager import BrowserManager
from core.website_handler import WebsiteHandler
from utils.file_manager import FileManager
from utils.exceptions import (
    LoginFailedException,
    StatusCheckException,
    ImageUploadException,
    StudentFolderNotFoundException,
    NoImagesFoundException
)

class StudentProcessor:
    """学生处理器"""
    
    def __init__(self, browser_manager, progress_tracker):
        self.browser_manager = browser_manager
        self.progress_tracker = progress_tracker
    
    def process_student(self, student_data):
        """处理单个学生"""
        name = student_data['name']
        student_id = student_data['student_id']
        id_number = student_data['id_number']
        
        student_info = {
            '学号': student_id,
            '姓名': name,
            '处理时间': datetime.now().strftime(Config.DATETIME_FORMAT)
        }
        
        try:
            self.progress_tracker.print_status(f"开始处理学生: {name} ({student_id})")
            
            # 查找学生文件夹
            try:
                current_dir = Config.get_current_dir()
                student_folder = FileManager.find_student_folder(current_dir, name)
                self.progress_tracker.print_status(f"[{name}] 找到学生文件夹: {student_folder}")
            except StudentFolderNotFoundException as e:
                self.progress_tracker.print_status(f"[{name}] {str(e)}")
                student_info['错误信息'] = str(e)
                self.progress_tracker.update_progress(name, 'failed', student_info)
                return
            
            # 查找图片文件
            try:
                image_files = FileManager.find_images_in_folder(student_folder)
                self.progress_tracker.print_status(f"[{name}] 找到 {len(image_files)} 张图片")
            except NoImagesFoundException as e:
                self.progress_tracker.print_status(f"[{name}] {str(e)}")
                student_info['错误信息'] = str(e)
                self.progress_tracker.update_progress(name, 'failed', student_info)
                return
            
            # 使用浏览器处理上传
            success = self._upload_to_website(id_number, name, image_files, student_info)
            
            if success:
                self.progress_tracker.print_status(f"[{name}] 处理成功")
            else:
                self.progress_tracker.print_status(f"[{name}] 处理失败")
                
        except Exception as e:
            self.progress_tracker.print_status(f"[{name}] 处理过程中发生未预期错误: {str(e)}")
            student_info['错误信息'] = f"未预期错误: {str(e)}"
            self.progress_tracker.update_progress(name, 'failed', student_info)
    
    def _upload_to_website(self, student_id, student_name, image_paths, student_info):
        """上传到网站"""
        try:
            with self.browser_manager.create_browser() as (driver, wait):
                handler = WebsiteHandler(driver, wait)
                
                # 登录
                try:
                    handler.login(student_id)
                    self.progress_tracker.print_status(f"[{student_name}] 登录成功")
                except LoginFailedException as e:
                    self.progress_tracker.print_status(f"[{student_name}] 登录失败: {str(e)}")
                    student_info['错误信息'] = f"登录失败: {str(e)}"
                    self.progress_tracker.update_progress(student_name, 'failed', student_info)
                    return False
                
                # 检查初始状态
                try:
                    is_completed, initial_status = handler.check_submission_status()
                    self.progress_tracker.print_status(f"[{student_name}] 当前状态: {initial_status}")
                    
                    if initial_status == '已完成':
                        self.progress_tracker.update_progress(student_name, 'completed', student_info)
                        return True
                    elif initial_status == '待审核':
                        self.progress_tracker.update_progress(student_name, 'pending_review', student_info)
                        return True
                        
                except StatusCheckException as e:
                    self.progress_tracker.print_status(f"[{student_name}] 状态检查失败: {str(e)}")
                    student_info['错误信息'] = f"状态检查失败: {str(e)}"
                    self.progress_tracker.update_progress(student_name, 'failed', student_info)
                    return False
                
                # 如果是未完成状态，进行上传
                if initial_status == '未完成':
                    try:
                        # 上传图片
                        handler.upload_images(image_paths)
                        self.progress_tracker.print_status(f"[{student_name}] 图片上传完成")
                        
                        # 提交
                        handler.submit_upload()
                        self.progress_tracker.print_status(f"[{student_name}] 提交完成")
                        
                        # 检查最终状态
                        try:
                            _, final_status = handler.check_submission_status()
                            student_info['最终状态'] = final_status
                            
                            if final_status == '待审核':
                                self.progress_tracker.update_progress(student_name, 'pending_review', student_info)
                            elif final_status == '已完成':
                                self.progress_tracker.update_progress(student_name, 'newly_submitted', student_info)
                            else:
                                student_info['错误信息'] = f"提交后状态异常: {final_status}"
                                self.progress_tracker.update_progress(student_name, 'failed', student_info)
                                return False
                                
                        except StatusCheckException as e:
                            self.progress_tracker.print_status(f"[{student_name}] 最终状态检查失败: {str(e)}")
                            student_info['错误信息'] = f"最终状态检查失败: {str(e)}"
                            self.progress_tracker.update_progress(student_name, 'failed', student_info)
                            return False
                            
                    except ImageUploadException as e:
                        self.progress_tracker.print_status(f"[{student_name}] 上传失败: {str(e)}")
                        student_info['错误信息'] = f"上传失败: {str(e)}"
                        self.progress_tracker.update_progress(student_name, 'failed', student_info)
                        return False
                
                return True
                
        except Exception as e:
            self.progress_tracker.print_status(f"[{student_name}] 浏览器操作失败: {str(e)}")
            student_info['错误信息'] = f"浏览器操作失败: {str(e)}"
            self.progress_tracker.update_progress(student_name, 'failed', student_info)
            return False 