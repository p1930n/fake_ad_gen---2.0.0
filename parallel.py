import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from pathlib import Path
import concurrent.futures
import threading
from datetime import datetime

print_lock = threading.Lock()
position_lock = threading.Lock()
result_lock = threading.Lock()

# 调整为2K分辨率
SCREEN_WIDTH = 2560
SCREEN_HEIGHT = 1440
BROWSER_WIDTH = 350  # 每行4个窗口
BROWSER_HEIGHT = 400  # 每列3行
positions = []

# 存储处理结果
results = {
    'pending_review': [],  # 待审核
    'completed': [],      # 已完成
    'newly_submitted': [], # 新提交
    'failed': []          # 提交失败
}

def initialize_positions():
    cols = 4
    rows = 3
    for row in range(rows):
        for col in range(cols):
            x = col * BROWSER_WIDTH
            y = row * BROWSER_HEIGHT
            positions.append((x, y))

def get_next_position():
    with position_lock:
        if not positions:
            initialize_positions()
        if positions:
            return positions.pop(0)
        return (0, 0)

def return_position(pos):
    with position_lock:
        positions.append(pos)

def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)

def add_to_results(category, student_info):
    with result_lock:
        results[category].append(student_info)

def find_student_folder(base_path: str, student_name: str) -> str:
    base_path = Path(base_path)
    for path in base_path.rglob("*"):
        if path.is_dir() and student_name in path.name:
            return str(path)
    return None

def check_submission_status(driver, wait) -> tuple:
    """
    检查提交状态
    返回: (是否完成, 状态描述)
    状态可能为: '已完成', '待审核', '未完成'
    """
    try:
        time.sleep(2)
        cards = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//div[contains(@class, 'el-card')]")))
        
        for card in cards:
            try:
                # 检查未完成状态
                status = card.find_element(By.XPATH, ".//span[contains(text(), '未完成')]")
                return False, '未完成'
            except:
                try:
                    # 检查待审核状态
                    status = card.find_element(By.XPATH, ".//span[contains(text(), '待审核')]")
                    return True, '待审核'
                except:
                    pass
        return True, '已完成'
    except Exception as e:
        safe_print(f"检查状态时发生错误: {e}")
        return False, '检查失败'

def upload_to_website(student_id, student_name, image_paths, password="123456"):
    options = webdriver.ChromeOptions()
    position = get_next_position()
    driver = None
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(BROWSER_WIDTH, BROWSER_HEIGHT)
        driver.set_window_position(position[0], position[1])
        
        wait = WebDriverWait(driver, 10)
        
        safe_print(f"正在登录账号 {student_id}...")
        driver.get("http://120.55.57.58:3510/")
        
        username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='账号']")))
        password_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='密码']")
        
        username_input.send_keys(student_id)
        password_input.send_keys(password)
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button.el-button--primary")
        login_button.click()
        
        # 检查初始状态
        is_completed, initial_status = check_submission_status(driver, wait)
        student_info = {
            '学号': student_id,
            '姓名': student_name,
            '处理时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        if initial_status == '已完成':
            safe_print(f"[学生 {student_id}] 已完成所有任务，跳过上传")
            add_to_results('completed', student_info)
            return True
        elif initial_status == '待审核':
            safe_print(f"[学生 {student_id}] 状态为待审核，跳过上传")
            add_to_results('pending_review', student_info)
            return True
        
        # 如果是未完成状态，进行上传
        incomplete_task = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class, 'el-card')]//span[text()='未完成']/ancestor::div[contains(@class, 'el-card')]")))
        incomplete_task.click()
        
        for image_path in image_paths:
            time.sleep(2)
            file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
            file_input.send_keys(os.path.abspath(image_path))
            safe_print(f"[学生 {student_id}] 已添加图片: {image_path}")
            time.sleep(2)
        
        time.sleep(5)
        
        upload_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.el-button.shangcc.el-button--success")))
        
        try:
            upload_button.click()
        except:
            driver.execute_script("arguments[0].click();", upload_button)
        
        time.sleep(5)
        
        # 检查上传后状态
        _, final_status = check_submission_status(driver, wait)
        student_info['最终状态'] = final_status
        
        if final_status == '待审核':
            add_to_results('pending_review', student_info)
        elif final_status == '已完成':
            add_to_results('newly_submitted', student_info)
        else:
            add_to_results('failed', student_info)
            
        safe_print(f"[学生 {student_id}] 的所有图片上传完成，最终状态: {final_status}")
        return True
        
    except Exception as e:
        safe_print(f"[学生 {student_id}] 上传过程中发生错误: {str(e)}")
        add_to_results('failed', {
            '学号': student_id,
            '姓名': student_name,
            '处理时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '错误信息': str(e)
        })
        return False
    finally:
        if driver:
            driver.quit()
        return_position(position)

def process_student(student_data):
    name, student_id, id_number, current_dir = student_data
    
    try:
        safe_print(f"\n正在处理学生: {name}")
        
        student_folder = find_student_folder(current_dir, name)
        
        if student_folder:
            safe_print(f"[学生 {name}] 找到学生文件夹: {student_folder}")
            image_files = []
            for ext in ['*.jpg', '*.jpeg', '*.png']:
                image_files.extend([str(p) for p in Path(student_folder).rglob(ext)])
            
            if image_files:
                safe_print(f"[学生 {name}] 找到 {len(image_files)} 张图片")
                success = upload_to_website(id_number, name, image_files)
                if success:
                    safe_print(f"[学生 {name}] 处理成功")
                else:
                    safe_print(f"[学生 {name}] 处理失败")
            else:
                safe_print(f"[学生 {name}] 在文件夹中未找到图片文件: {student_folder}")
                add_to_results('failed', {
                    '学号': student_id,
                    '姓名': name,
                    '处理时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    '错误信息': '未找到图片文件'
                })
        else:
            safe_print(f"[学生 {name}] 未找到包含学生姓名的文件夹")
            add_to_results('failed', {
                '学号': student_id,
                '姓名': name,
                '处理时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '错误信息': '未找到学生文件夹'
            })
            
    except Exception as e:
        safe_print(f"[学生 {name}] 处理过程中发生错误: {e}")
        add_to_results('failed', {
            '学号': student_id,
            '姓名': name,
            '处理时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '错误信息': str(e)
        })

def generate_report():
    """生成处理报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f'处理报告_{timestamp}.xlsx'
    
    with pd.ExcelWriter(report_filename) as writer:
        # 创建各个状态的DataFrame并写入不同的sheet
        for status, data in results.items():
            if data:  # 只处理有数据的状态
                df = pd.DataFrame(data)
                sheet_name = {
                    'pending_review': '待审核',
                    'completed': '已完成',
                    'newly_submitted': '新提交',
                    'failed': '提交失败'
                }[status]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    safe_print(f"\n处理报告已生成: {report_filename}")
    # 打印统计信息
    safe_print("\n处理统计:")
    safe_print(f"待审核: {len(results['pending_review'])} 人")
    safe_print(f"已完成: {len(results['completed'])} 人")
    safe_print(f"新提交: {len(results['newly_submitted'])} 人")
    safe_print(f"提交失败: {len(results['failed'])} 人")

def main():
    initialize_positions()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    excel_file = None
    for file in os.listdir(current_dir):
        if file.endswith(('.xlsx', '.xls')):
            excel_file = os.path.join(current_dir, file)
            break
    
    if not excel_file:
        safe_print("未找到Excel文件！")
        return
    
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        safe_print(f"读取Excel文件失败: {e}")
        return
    
    if '姓名' not in df.columns or '学号' not in df.columns or '身份证号' not in df.columns:
        safe_print("Excel文件必须包含'姓名'、'学号'和'身份证号'列！")
        return
    
    students_data = []
    for _, row in df.iterrows():
        name = str(row['姓名']).strip()
        student_id = str(row['学号']).strip()
        id_number = str(row['身份证号']).strip()
        students_data.append((name, student_id, id_number, current_dir))
    
    max_workers = 10
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_student, student_data) for student_data in students_data]
        concurrent.futures.wait(futures)
    
    # 生成报告
    generate_report()
    safe_print("\n所有学生处理完成！")

if __name__ == "__main__":
    main()