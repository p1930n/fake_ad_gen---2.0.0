import threading
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from config.config import Config

class BrowserPositionManager:
    """浏览器窗口位置管理器"""
    
    def __init__(self):
        self.positions = []
        self.position_lock = threading.Lock()
        self._initialize_positions()
    
    def _initialize_positions(self):
        """初始化窗口位置"""
        for row in range(Config.WINDOW_ROWS):
            for col in range(Config.WINDOW_COLS):
                x = col * Config.BROWSER_WIDTH
                y = row * Config.BROWSER_HEIGHT
                self.positions.append((x, y))
    
    def get_position(self):
        """获取下一个可用位置"""
        with self.position_lock:
            if not self.positions:
                self._initialize_positions()
            return self.positions.pop(0) if self.positions else (0, 0)
    
    def return_position(self, position):
        """归还位置"""
        with self.position_lock:
            self.positions.append(position)

class BrowserManager:
    """浏览器管理器"""
    
    def __init__(self, position_manager):
        self.position_manager = position_manager
    
    @contextmanager
    def create_browser(self):
        """创建浏览器上下文管理器"""
        position = self.position_manager.get_position()
        driver = None
        
        try:
            options = webdriver.ChromeOptions()
            # 添加一些优化选项
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            
            # 添加无头模式支持
            if Config.HEADLESS_MODE:
                options.add_argument('--headless')
            
            driver = webdriver.Chrome(options=options)
            driver.set_window_size(Config.BROWSER_WIDTH, Config.BROWSER_HEIGHT)
            driver.set_window_position(position[0], position[1])
            
            wait = WebDriverWait(driver, Config.LOGIN_WAIT_TIME)
            
            yield driver, wait
            
        except Exception as e:
            raise e
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass  # 忽略关闭时的错误
            self.position_manager.return_position(position) 