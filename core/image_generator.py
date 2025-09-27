#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片生成模块
为学生生成各种类型的图片文件
"""

import os
import time
from typing import List, Dict, Any
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import random
from tqdm import tqdm
from pathlib import Path

class ImageGenerator:
    """图片生成器"""
    
    def __init__(self):
        # 使用动态配置获取输出目录
        try:
            from config.settings_manager import SettingsManager
            settings_manager = SettingsManager()
            self.output_dir = settings_manager.get_value('image', 'output_dir') or "generated_images"
        except ImportError:
            self.output_dir = "generated_images"
        self.templates = {
            'fake_ad': {
                'name': '虚假广告图片',
                'size': (800, 600),
                'background_colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
                'text_colors': ['#FFFFFF', '#2D3436', '#636E72']
            },
            'certificate': {
                'name': '证书模板',
                'size': (1200, 800),
                'background_colors': ['#F8F9FA', '#E9ECEF', '#DEE2E6'],
                'text_colors': ['#212529', '#495057', '#6C757D']
            },
            'poster': {
                'name': '海报模板',
                'size': (600, 900),
                'background_colors': ['#FF7675', '#74B9FF', '#00B894', '#FDCB6E', '#E17055'],
                'text_colors': ['#FFFFFF', '#2D3436']
            }
        }
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_for_students(self, students: List[Dict[str, Any]]):
        """为选定的学生生成图片"""
        print(f"\n🎨 开始为 {len(students)} 名学生生成图片...")
        
        # 选择图片类型
        print("\n📋 可用图片模板:")
        template_list = list(self.templates.keys())
        for i, (key, template) in enumerate(self.templates.items(), 1):
            print(f"  {i}. {template['name']} ({template['size'][0]}x{template['size'][1]})")
        
        while True:
            try:
                choice = input(f"\n请选择模板 (1-{len(template_list)}): ").strip()
                template_index = int(choice) - 1
                if 0 <= template_index < len(template_list):
                    selected_template = template_list[template_index]
                    break
                else:
                    print("⚠️  请输入有效的模板编号")
            except ValueError:
                print("⚠️  请输入数字")
        
        # 选择生成数量
        # 获取动态配置的最大图片数
        try:
            from config.settings_manager import SettingsManager
            settings_manager = SettingsManager()
            max_images = settings_manager.get_value('image', 'max_images_per_student') or 10
        except ImportError:
            max_images = 10
        
        while True:
            try:
                count = int(input(f"每位学生生成图片数量 (1-{max_images}): ").strip())
                if 1 <= count <= max_images:
                    break
                else:
                    print(f"⚠️  请输入1-{max_images}之间的数字")
            except ValueError:
                print("⚠️  请输入有效数字")
        
        # 开始生成
        total_images = len(students) * count
        
        with tqdm(total=total_images, desc="生成进度", unit="张") as pbar:
            for student in students:
                student_name = student['name']
                student_id = student['student_id']
                
                # 为每个学生创建文件夹
                student_dir = os.path.join(self.output_dir, f"{student_name}_{student_id}")
                os.makedirs(student_dir, exist_ok=True)
                
                # 生成指定数量的图片
                for i in range(count):
                    image_path = os.path.join(
                        student_dir, 
                        f"{selected_template}_{i+1:02d}.png"
                    )
                    
                    try:
                        self._generate_single_image(
                            selected_template, 
                            student_name, 
                            student_id, 
                            image_path
                        )
                        pbar.set_postfix_str(f"正在处理: {student_name}")
                        
                    except Exception as e:
                        pbar.write(f"❌ 为 {student_name} 生成图片失败: {str(e)}")
                    
                    pbar.update(1)
                    time.sleep(0.1)  # 模拟处理时间
        
        print(f"\n✅ 图片生成完成！")
        print(f"📁 输出目录: {os.path.abspath(self.output_dir)}")
        self._show_generation_summary(students, count, selected_template)
    
    def _generate_single_image(self, template_key: str, student_name: str, student_id: str, output_path: str):
        """生成单张图片"""
        template = self.templates[template_key]
        
        # 创建图片
        image = Image.new('RGB', template['size'], 
                         random.choice(template['background_colors']))
        draw = ImageDraw.Draw(image)
        
        # 获取动态配置的字体大小
        try:
            from config.settings_manager import SettingsManager
            settings_manager = SettingsManager()
            font_size_large = settings_manager.get_value('image', 'font_size_large') or 36
            font_size_medium = settings_manager.get_value('image', 'font_size_medium') or 24
            font_size_small = settings_manager.get_value('image', 'font_size_small') or 18
        except ImportError:
            font_size_large, font_size_medium, font_size_small = 36, 24, 18
        
        # 尝试加载字体
        try:
            # 尝试使用系统字体
            font_large = ImageFont.truetype("arial.ttf", font_size_large)
            font_medium = ImageFont.truetype("arial.ttf", font_size_medium)
            font_small = ImageFont.truetype("arial.ttf", font_size_small)
        except:
            try:
                # 尝试使用默认字体
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            except:
                font_large = font_medium = font_small = None
        
        # 获取图片尺寸
        width, height = template['size']
        text_color = random.choice(template['text_colors'])
        
        # 根据模板类型生成不同内容
        if template_key == 'fake_ad':
            self._draw_fake_ad(draw, width, height, student_name, student_id, 
                             text_color, font_large, font_medium, font_small)
        elif template_key == 'certificate':
            self._draw_certificate(draw, width, height, student_name, student_id, 
                                 text_color, font_large, font_medium, font_small)
        elif template_key == 'poster':
            self._draw_poster(draw, width, height, student_name, student_id, 
                            text_color, font_large, font_medium, font_small)
        
        # 获取动态配置的图片质量
        try:
            from config.settings_manager import SettingsManager
            settings_manager = SettingsManager()
            image_quality = settings_manager.get_value('image', 'image_quality') or 95
        except ImportError:
            image_quality = 95
        
        # 保存图片
        image.save(output_path, 'PNG', quality=image_quality)
    
    def _draw_fake_ad(self, draw, width, height, name, student_id, color, font_l, font_m, font_s):
        """绘制虚假广告"""
        # 标题
        title = "🎉 特别优惠 🎉"
        if font_l:
            bbox = draw.textbbox((0, 0), title, font=font_l)
            title_width = bbox[2] - bbox[0]
            draw.text(((width - title_width) // 2, 50), title, fill=color, font=font_l)
        
        # 主要内容
        content = [
            f"恭喜 {name} 同学",
            f"学号: {student_id}",
            "",
            "🎯 限时优惠活动",
            "💰 超值优惠券",
            "🚀 立即参与",
            "",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d')}"
        ]
        
        y_offset = 150
        for line in content:
            if font_m and line:
                bbox = draw.textbbox((0, 0), line, font=font_m)
                line_width = bbox[2] - bbox[0]
                draw.text(((width - line_width) // 2, y_offset), line, fill=color, font=font_m)
            y_offset += 40
        
        # 装饰边框
        draw.rectangle([20, 20, width-20, height-20], outline=color, width=3)
    
    def _draw_certificate(self, draw, width, height, name, student_id, color, font_l, font_m, font_s):
        """绘制证书"""
        # 证书标题
        title = "📜 荣誉证书"
        if font_l:
            bbox = draw.textbbox((0, 0), title, font=font_l)
            title_width = bbox[2] - bbox[0]
            draw.text(((width - title_width) // 2, 80), title, fill=color, font=font_l)
        
        # 证书内容
        content = [
            "",
            f"兹证明 {name} 同学",
            f"学号: {student_id}",
            "",
            "在学习期间表现优秀",
            "特发此证，以资鼓励",
            "",
            f"颁发日期: {datetime.now().strftime('%Y年%m月%d日')}"
        ]
        
        y_offset = 200
        for line in content:
            if font_m and line:
                bbox = draw.textbbox((0, 0), line, font=font_m)
                line_width = bbox[2] - bbox[0]
                draw.text(((width - line_width) // 2, y_offset), line, fill=color, font=font_m)
            y_offset += 50
        
        # 装饰边框
        draw.rectangle([50, 50, width-50, height-50], outline=color, width=5)
        draw.rectangle([70, 70, width-70, height-70], outline=color, width=2)
    
    def _draw_poster(self, draw, width, height, name, student_id, color, font_l, font_m, font_s):
        """绘制海报"""
        # 海报标题
        title = "🌟 学生风采"
        if font_l:
            bbox = draw.textbbox((0, 0), title, font=font_l)
            title_width = bbox[2] - bbox[0]
            draw.text(((width - title_width) // 2, 60), title, fill=color, font=font_l)
        
        # 海报内容
        content = [
            "",
            f"姓名: {name}",
            f"学号: {student_id}",
            "",
            "🎓 优秀学生",
            "💪 积极向上",
            "🌈 未来可期",
            "",
            "加油！💪",
            "",
            f"{datetime.now().strftime('%Y.%m.%d')}"
        ]
        
        y_offset = 180
        for line in content:
            if font_m and line:
                bbox = draw.textbbox((0, 0), line, font=font_m)
                line_width = bbox[2] - bbox[0]
                draw.text(((width - line_width) // 2, y_offset), line, fill=color, font=font_m)
            y_offset += 45
        
        # 装饰元素
        draw.rectangle([30, 30, width-30, height-30], outline=color, width=4)
        # 圆角装饰
        for i in range(0, width, 100):
            draw.ellipse([i, 10, i+20, 30], fill=color)
            draw.ellipse([i, height-30, i+20, height-10], fill=color)
    
    def _show_generation_summary(self, students: List[Dict], count: int, template: str):
        """显示生成摘要"""
        print("\n" + "="*60)
        print("📊 图片生成摘要")
        print("="*60)
        print(f"👥 处理学生数: {len(students)}")
        print(f"🖼️  每人图片数: {count}")
        print(f"📋 使用模板: {self.templates[template]['name']}")
        print(f"📁 总图片数: {len(students) * count}")
        print(f"💾 输出目录: {os.path.abspath(self.output_dir)}")
        print("="*60)
        
        # 显示每个学生的文件夹
        print("\n📁 生成的文件夹:")
        for student in students:
            folder_name = f"{student['name']}_{student['student_id']}"
            folder_path = os.path.join(self.output_dir, folder_name)
            if os.path.exists(folder_path):
                file_count = len([f for f in os.listdir(folder_path) if f.endswith('.png')])
                print(f"  📂 {folder_name} ({file_count} 张图片)")
        
        input("\n按Enter键继续...")
    
    def get_available_templates(self):
        """获取可用模板列表"""
        return list(self.templates.keys())
    
    def get_template_info(self, template_key: str):
        """获取模板信息"""
        return self.templates.get(template_key, {}) 