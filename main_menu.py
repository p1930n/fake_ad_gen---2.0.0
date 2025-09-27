#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量文件处理系统 v2.0 - 主程序
功能选择菜单版本
"""

import sys
import os

def check_dependencies():
    """检查必要的依赖"""
    required_modules = [
        'pandas', 'selenium', 'tqdm', 'openpyxl', 'PIL'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            if module == 'PIL':
                import PIL
            else:
                __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ 缺少必要的依赖包:")
        for module in missing_modules:
            print(f"   • {module}")
        print("\n💡 请运行以下命令安装依赖:")
        print("   pip install -r requirements.txt")
        if 'PIL' in missing_modules:
            print("   pip install Pillow")
        return False
    
    return True

def main():
    """主函数"""
    try:
        # 检查依赖
        if not check_dependencies():
            return 1
        
        # 导入菜单系统
        from ui.menu_system import MenuSystem
        
        # 创建并运行菜单系统
        menu = MenuSystem()
        return menu.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断，再见！")
        return 0
    except ImportError as e:
        print(f"❌ 模块导入错误: {str(e)}")
        print("💡 请确保所有必要的文件都存在于当前目录")
        return 1
    except Exception as e:
        print(f"❌ 程序运行时发生错误: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 