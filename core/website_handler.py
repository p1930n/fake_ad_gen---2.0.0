import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    ElementClickInterceptedException
)
from config.config import Config
from utils.exceptions import (
    LoginFailedException, 
    StatusCheckException, 
    ImageUploadException
)

class WebsiteHandler:
    """网站操作处理器"""
    
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
    
    def login(self, student_id, password=None):
        """登录网站"""
        if password is None:
            password = Config.DEFAULT_PASSWORD
            
        try:
            self.driver.get(Config.BASE_URL)
            
            username_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='账号']"))
            )
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder='密码']")
            
            username_input.clear()
            username_input.send_keys(student_id)
            password_input.clear()
            password_input.send_keys(password)
            
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button.el-button--primary")
            login_button.click()
            
            # 等待登录完成，检查是否跳转到主页面
            time.sleep(Config.STATUS_CHECK_WAIT_TIME)
            
        except TimeoutException as e:
            raise LoginFailedException(f"登录超时: {str(e)}")
        except NoSuchElementException as e:
            raise LoginFailedException(f"登录页面元素未找到: {str(e)}")
        except WebDriverException as e:
            raise LoginFailedException(f"登录过程中发生WebDriver错误: {str(e)}")
    
    def check_submission_status(self):
        """检查提交状态"""
        try:
            time.sleep(Config.STATUS_CHECK_WAIT_TIME)
            cards = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[contains(@class, 'el-card')]")
                )
            )
            
            for card in cards:
                try:
                    # 检查未完成状态
                    card.find_element(By.XPATH, ".//span[contains(text(), '未完成')]")
                    return False, '未完成'
                except NoSuchElementException:
                    try:
                        # 检查待审核状态
                        card.find_element(By.XPATH, ".//span[contains(text(), '待审核')]")
                        return True, '待审核'
                    except NoSuchElementException:
                        continue
            
            return True, '已完成'
            
        except TimeoutException as e:
            raise StatusCheckException(f"检查状态超时: {str(e)}")
        except WebDriverException as e:
            raise StatusCheckException(f"检查状态时发生WebDriver错误: {str(e)}")
    
    def upload_images(self, image_paths):
        """上传图片"""
        try:
            # 点击未完成任务
            incomplete_task = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class, 'el-card')]//span[text()='未完成']/ancestor::div[contains(@class, 'el-card')]")
                )
            )
            incomplete_task.click()
            
            # 上传每张图片
            for image_path in image_paths:
                if not os.path.exists(image_path):
                    raise ImageUploadException(f"图片文件不存在: {image_path}")
                
                time.sleep(Config.UPLOAD_WAIT_TIME)
                
                try:
                    file_input = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                    )
                    file_input.send_keys(os.path.abspath(image_path))
                    time.sleep(Config.UPLOAD_WAIT_TIME)
                except TimeoutException:
                    raise ImageUploadException(f"文件输入框未找到，无法上传: {image_path}")
            
            # 等待所有图片加载完成
            time.sleep(Config.SUBMIT_WAIT_TIME)
            
        except TimeoutException as e:
            raise ImageUploadException(f"上传图片超时: {str(e)}")
        except WebDriverException as e:
            raise ImageUploadException(f"上传图片时发生WebDriver错误: {str(e)}")
    
    def submit_upload(self):
        """提交上传"""
        try:
            upload_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.el-button.shangcc.el-button--success")
                )
            )
            
            try:
                upload_button.click()
            except ElementClickInterceptedException:
                # 如果普通点击被拦截，使用JavaScript点击
                self.driver.execute_script("arguments[0].click();", upload_button)
            
            time.sleep(Config.SUBMIT_WAIT_TIME)
            
        except TimeoutException as e:
            raise ImageUploadException(f"提交按钮未找到或不可点击: {str(e)}")
        except WebDriverException as e:
            raise ImageUploadException(f"提交时发生WebDriver错误: {str(e)}") 