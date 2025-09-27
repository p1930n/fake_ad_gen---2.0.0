import os
import pandas as pd
from pathlib import Path
from config.config import Config
from utils.exceptions import (
    ExcelReadException, 
    StudentFolderNotFoundException, 
    NoImagesFoundException
)

class FileManager:
    """文件管理器"""
    
    @staticmethod
    def find_excel_file(directory):
        """在指定目录中查找Excel文件"""
        for file in os.listdir(directory):
            if any(file.endswith(ext) for ext in Config.EXCEL_EXTENSIONS):
                return os.path.join(directory, file)
        return None
    
    @staticmethod
    def read_excel_file(file_path):
        """读取Excel文件"""
        try:
            df = pd.read_excel(file_path)
            
            # 验证必需的列是否存在
            required_columns = ['姓名', '学号', '身份证号']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ExcelReadException(f"Excel文件缺少必需的列: {', '.join(missing_columns)}")
            
            return df
            
        except FileNotFoundError:
            raise ExcelReadException(f"Excel文件不存在: {file_path}")
        except pd.errors.EmptyDataError:
            raise ExcelReadException(f"Excel文件为空: {file_path}")
        except Exception as e:
            raise ExcelReadException(f"读取Excel文件失败: {str(e)}")
    
    @staticmethod
    def find_student_folder(base_path, student_name):
        """查找学生文件夹"""
        base_path = Path(base_path)
        
        for path in base_path.rglob("*"):
            if path.is_dir() and student_name in path.name:
                return str(path)
        
        raise StudentFolderNotFoundException(f"未找到学生 {student_name} 的文件夹")
    
    @staticmethod
    def find_images_in_folder(folder_path):
        """在文件夹中查找图片文件"""
        image_files = []
        folder_path = Path(folder_path)
        
        for ext in Config.SUPPORTED_IMAGE_EXTENSIONS:
            image_files.extend([str(p) for p in folder_path.rglob(ext)])
        
        if not image_files:
            raise NoImagesFoundException(f"在文件夹 {folder_path} 中未找到图片文件")
        
        return image_files
    
    @staticmethod
    def prepare_student_data(df):
        """准备学生数据"""
        students_data = []
        
        for _, row in df.iterrows():
            name = str(row['姓名']).strip()
            student_id = str(row['学号']).strip()
            id_number = str(row['身份证号']).strip()
            
            # 验证数据完整性
            if not all([name, student_id, id_number]):
                continue  # 跳过不完整的数据
            
            students_data.append({
                'name': name,
                'student_id': student_id,
                'id_number': id_number
            })
        
        return students_data 