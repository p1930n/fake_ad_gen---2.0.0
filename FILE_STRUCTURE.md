# 📁 项目文件结构说明

## 🎯 重组后的文件夹结构

```
fake_ad_generator/
├── 📂 core/                    # 核心业务模块
│   ├── __init__.py
│   ├── browser_manager.py      # 浏览器管理
│   ├── image_generator.py      # 图片生成
│   ├── student_processor.py    # 学生处理逻辑
│   ├── upload_manager.py       # 上传管理
│   └── website_handler.py      # 网站操作处理
│
├── 📂 ui/                      # 用户界面模块
│   ├── __init__.py
│   ├── menu_system.py          # 菜单系统
│   ├── rich_settings_ui.py     # Rich设置界面
│   ├── rich_ui.py              # Rich用户界面
│   └── settings_ui.py          # 设置界面
│
├── 📂 utils/                   # 工具和支持模块
│   ├── __init__.py
│   ├── exceptions.py           # 自定义异常
│   ├── file_manager.py         # 文件管理
│   ├── progress_tracker.py     # 进度跟踪
│   └── report_generator.py     # 报告生成
│
├── 📂 config/                  # 配置管理
│   ├── __init__.py
│   ├── config.py               # 系统配置
│   ├── settings_manager.py     # 设置管理器
│   └── user_settings.json      # 用户配置文件
│
├── 📂 data/                    # 数据文件
│   ├── class_info.xlsx         # 学生信息文件
│   └── 处理报告_*.xlsx         # 处理报告
│
├── 📂 docs/                    # 文档
│   ├── ENV_GUIDE.md            # 环境指南
│   ├── README.md               # 项目说明
│   ├── SETTINGS_GUIDE.md       # 设置指南
│   └── SYSTEM_SUMMARY.md       # 系统总结
│
├── 📂 scripts/                 # 脚本文件
│   ├── run_app.bat             # 运行脚本
│   └── setup_env.bat           # 环境设置脚本
│
├── 📄 main_menu.py             # 主程序入口 ⭐
├── 📄 main_improved.py         # 改进版主程序 ⭐
├── 📄 parallel.py              # 原始程序（保留）
├── 📄 requirements.txt         # 依赖文件
└── 📂 fake_ad_env/             # 虚拟环境

```

## 🚀 使用方法

### 启动程序
```bash
python main_menu.py        # 推荐：菜单版本
python main_improved.py    # 直接运行改进版
```

### 文件说明

#### 🏗️ 核心模块 (core/)
- **browser_manager.py**: 浏览器窗口管理和定位
- **image_generator.py**: 虚假广告图片生成
- **student_processor.py**: 学生数据处理逻辑
- **upload_manager.py**: 文件上传管理
- **website_handler.py**: 网站操作处理

#### 🎨 界面模块 (ui/)
- **menu_system.py**: 主菜单系统
- **rich_ui.py**: Rich库美化界面
- **rich_settings_ui.py**: Rich设置界面
- **settings_ui.py**: 基础设置界面

#### 🔧 工具模块 (utils/)
- **exceptions.py**: 自定义异常类
- **file_manager.py**: 文件操作工具
- **progress_tracker.py**: 进度跟踪器
- **report_generator.py**: Excel报告生成

#### ⚙️ 配置模块 (config/)
- **config.py**: 系统配置类
- **settings_manager.py**: 动态设置管理
- **user_settings.json**: 用户个性化配置

## 📋 主要改进

1. **🏗️ 模块化结构**: 按功能分类，便于维护和扩展
2. **📍 清晰定位**: 每个文件都有明确的职责
3. **🔄 向后兼容**: 保留所有原有功能
4. **📁 数据分离**: 数据文件独立存放
5. **📚 文档集中**: 所有文档统一管理

## 🎯 重组优势

- ✅ **更好的可维护性**: 模块化设计便于代码维护
- ✅ **清晰的职责分离**: 每个模块职责明确
- ✅ **易于扩展**: 新功能可以轻松添加到对应模块
- ✅ **统一的配置管理**: 所有配置集中在config文件夹
- ✅ **完整的功能保留**: 所有原有功能都正常工作

---
*文件重组完成日期：2025年9月27日* 