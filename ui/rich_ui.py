#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rich UI模块
提供美化的终端界面，支持自适应边框大小
"""

import os
import shutil
from typing import Dict, Any, List, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.tree import Tree
    from rich.layout import Layout
    from rich.align import Align
    from rich.columns import Columns
    from rich.rule import Rule
    from rich.padding import Padding
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class RichUI:
    """Rich界面管理器"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.terminal_size = self._get_terminal_size()
        
    def _get_terminal_size(self) -> tuple:
        """获取终端大小"""
        try:
            size = shutil.get_terminal_size()
            return size.columns, size.lines
        except:
            return 80, 24  # 默认大小
    
    def _get_adaptive_width(self, min_width: int = 60, max_width: int = 120) -> int:
        """获取自适应宽度"""
        width, _ = self.terminal_size
        # 留出边距
        content_width = width - 4
        return max(min_width, min(content_width, max_width))
    
    def clear_screen(self):
        """清屏"""
        if self.console:
            self.console.clear()
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self, cpu_count: int, max_workers: int):
        """打印程序横幅"""
        if not self.console:
            # 降级到ASCII
            self._print_ascii_banner(cpu_count, max_workers)
            return
        
        # Rich版本横幅
        # 自适应宽度的标题面板
        width = self._get_adaptive_width(50, 80)
        title_content = "[bold blue]批量文件处理系统 v2.0[/bold blue]\n[dim italic]Batch File Processing System[/dim italic]"
        title_panel = Panel(
            Align.center(title_content),
            style="bold white on blue",
            width=width,
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(Align.center(title_panel))
        
        # 系统信息
        info_table = Table(show_header=False, box=None, padding=(0, 1))
        info_table.add_column("项目", style="bold cyan")
        info_table.add_column("值", style="bold green")
        
        info_table.add_row("🖥️  CPU核心数", str(cpu_count))
        info_table.add_row("⚡ 默认线程数", str(max_workers))
        
        info_panel = Panel(
            info_table,
            title="[bold]系统信息[/bold]",
            style="green",
            width=width//2
        )
        
        self.console.print()
        self.console.print(Align.center(info_panel))
        self.console.print()
    
    def _print_ascii_banner(self, cpu_count: int, max_workers: int):
        """ASCII版本横幅（降级方案）"""
        width = self._get_adaptive_width()
        border = "+" + "=" * (width - 2) + "+"
        
        print()
        print(border)
        print(f"|{'批量文件处理系统 v2.0'.center(width - 2)}|")
        print(f"|{'Batch File Processing System'.center(width - 2)}|")
        print(border)
        print()
        print(f"系统信息: CPU核心数 {cpu_count}, 默认线程数 {max_workers}")
        print("=" * width)
    
    def print_main_menu(self) -> str:
        """显示主菜单并获取用户选择"""
        if not self.console:
            return self._print_ascii_main_menu()
        
        # Rich版本主菜单
        width = self._get_adaptive_width(60, 100)
        
        # 创建菜单表格
        menu_table = Table(
            show_header=False, 
            box=box.ROUNDED, 
            style="cyan",
            width=width-4
        )
        menu_table.add_column("选项", style="bold magenta", width=6)
        menu_table.add_column("功能", style="bold white", width=25)
        menu_table.add_column("描述", style="dim white")
        
        # 基础功能组 (1,2)
        basic_items = [
            ("1", "📤 上传指定学生文件", "为选定的学生上传已有文件到网站"),
            ("2", "🎨 为指定学生生成图片", "为选定的学生生成所需图片文件")
        ]
        
        # 高级功能组 (3,4,5)
        advanced_items = [
            ("3", "🖼️  图片生成中心", "批量图片生成、自定义模板等"),
            ("4", "📁 文件上传中心", "批量上传、状态监控等"),
            ("5", "⚙️  系统设置", "参数配置、备份恢复等")
        ]
        
        # 退出组 (0)
        exit_items = [
            ("0", "🚪 退出程序", "安全退出系统")
        ]
        
        # 添加基础功能组
        menu_table.add_row("", "[bold cyan]● 基础功能[/bold cyan]", "[dim]日常使用功能[/dim]")
        for option, title, desc in basic_items:
            menu_table.add_row(option, title, desc)
        
        # 添加分隔行
        menu_table.add_row("", "[dim]─" * 20 + "[/dim]", "")
        
        # 添加高级功能组
        menu_table.add_row("", "[bold magenta]● 高级功能[/bold magenta]", "[dim]批量处理和配置[/dim]")
        for option, title, desc in advanced_items:
            menu_table.add_row(option, title, desc)
        
        # 添加分隔行
        menu_table.add_row("", "[dim]─" * 20 + "[/dim]", "")
        
        # 添加退出组
        menu_table.add_row("", "[bold red]● 系统控制[/bold red]", "[dim]程序控制[/dim]")
        for option, title, desc in exit_items:
            menu_table.add_row(option, title, desc)
        
        menu_panel = Panel(
            menu_table,
            title="[bold blue]主功能菜单[/bold blue]",
            style="blue",
            width=width
        )
        
        self.console.print(Align.center(menu_panel))
        
        # 获取用户输入
        choice = Prompt.ask(
            "\n[bold cyan]请选择功能[/bold cyan]",
            choices=["0", "1", "2", "3", "4", "5"],
            default="0"
        )
        
        return choice
    
    def _print_ascii_main_menu(self) -> str:
        """ASCII版本主菜单（降级方案）"""
        width = self._get_adaptive_width()
        border = "+" + "-" * (width - 2) + "+"
        
        print(border)
        print(f"|{'主功能菜单'.center(width - 2)}|")
        print(border)
        
        # 基础功能组
        basic_items = [
            "1. 上传指定学生文件",
            "2. 为指定学生生成图片"
        ]
        
        # 高级功能组
        advanced_items = [
            "3. 图片生成中心",
            "4. 文件上传中心", 
            "5. 系统设置"
        ]
        
        # 退出组
        exit_items = ["0. 退出程序"]
        
        # 显示基础功能组
        print(f"|  {'● 基础功能 - 日常使用':<{width-4}}|")
        for item in basic_items:
            print(f"|  {item:<{width-4}}|")
        
        # 分隔行
        print(f"|  {('-' * 40):<{width-4}}|")
        
        # 显示高级功能组
        print(f"|  {'● 高级功能 - 批量处理和配置':<{width-4}}|")
        for item in advanced_items:
            print(f"|  {item:<{width-4}}|")
        
        # 分隔行
        print(f"|  {('-' * 40):<{width-4}}|")
        
        # 显示退出组
        print(f"|  {'● 系统控制 - 程序控制':<{width-4}}|")
        for item in exit_items:
            print(f"|  {item:<{width-4}}|")
        
        print(border)
        
        while True:
            choice = input("\n请选择功能 (0-5): ").strip()
            if choice in ["0", "1", "2", "3", "4", "5"]:
                return choice
            print("请输入有效选项 (0-5)")
    
    def print_submenu(self, title: str, items: List[tuple]) -> str:
        """显示子菜单"""
        if not self.console:
            return self._print_ascii_submenu(title, items)
        
        width = self._get_adaptive_width(50, 80)
        
        # 创建子菜单表格
        submenu_table = Table(
            show_header=False,
            box=box.ROUNDED,
            style="cyan",
            width=width-4
        )
        submenu_table.add_column("选项", style="bold magenta", width=6)
        submenu_table.add_column("功能", style="bold white")
        
        for option, desc in items:
            submenu_table.add_row(option, desc)
        
        submenu_panel = Panel(
            submenu_table,
            title=f"[bold green]{title}[/bold green]",
            style="green",
            width=width
        )
        
        self.console.print()
        self.console.print(Align.center(submenu_panel))
        
        valid_choices = [item[0] for item in items]
        choice = Prompt.ask(
            f"\n[bold cyan]请选择操作[/bold cyan]",
            choices=valid_choices
        )
        
        return choice
    
    def _print_ascii_submenu(self, title: str, items: List[tuple]) -> str:
        """ASCII版本子菜单（降级方案）"""
        width = self._get_adaptive_width()
        border = "+" + "-" * (width - 2) + "+"
        
        print()
        print(border)
        print(f"|{title.center(width - 2)}|")
        print(border)
        
        for option, desc in items:
            print(f"|  {option}. {desc:<{width-6}}|")
        
        print(border)
        
        valid_choices = [item[0] for item in items]
        while True:
            choice = input(f"\n请选择操作 ({'/'.join(valid_choices)}): ").strip()
            if choice in valid_choices:
                return choice
            print(f"请输入有效选项 ({'/'.join(valid_choices)})")
    
    def show_student_list(self, students: List[Dict[str, Any]], mode: str = "single") -> List[Dict[str, Any]]:
        """显示学生列表并获取选择"""
        if not self.console:
            return self._show_ascii_student_list(students, mode)
        
        width = self._get_adaptive_width(60, 100)
        
        # 创建学生列表表格
        student_table = Table(
            show_header=True,
            box=box.ROUNDED,
            style="cyan",
            width=width-4
        )
        student_table.add_column("编号", style="bold magenta", width=6)
        student_table.add_column("姓名", style="bold white", width=15)
        student_table.add_column("学号", style="bold yellow")
        
        for i, student in enumerate(students, 1):
            student_table.add_row(
                str(i),
                student['name'],
                student['student_id']
            )
        
        title = f"学生列表 (共 {len(students)} 名)"
        if mode == "multiple":
            title += " - 多选模式"
        
        student_panel = Panel(
            student_table,
            title=f"[bold blue]{title}[/bold blue]",
            style="blue",
            width=width
        )
        
        self.console.print()
        self.console.print(Align.center(student_panel))
        
        if mode == "single":
            choices = [str(i) for i in range(1, len(students) + 1)]
            choice_str = Prompt.ask(
                f"\n[bold cyan]请选择学生编号[/bold cyan]",
                choices=choices
            )
            choice = int(choice_str)
            return [students[choice - 1]]
        else:
            return self._handle_multiple_selection(students)
    
    def _show_ascii_student_list(self, students: List[Dict[str, Any]], mode: str) -> List[Dict[str, Any]]:
        """ASCII版本学生列表（降级方案）"""
        width = self._get_adaptive_width()
        
        print(f"\n学生列表 (共 {len(students)} 名):")
        print("-" * width)
        
        for i, student in enumerate(students, 1):
            print(f"  {i:2d}. {student['name']:10} (学号: {student['student_id']})")
        
        print("-" * width)
        
        if mode == "single":
            while True:
                try:
                    choice = int(input(f"请选择学生编号 (1-{len(students)}): "))
                    if 1 <= choice <= len(students):
                        return [students[choice - 1]]
                    print(f"请输入1-{len(students)}之间的数字")
                except ValueError:
                    print("请输入有效数字")
        else:
            return self._handle_ascii_multiple_selection(students)
    
    def _handle_multiple_selection(self, students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理多选（Rich版本）"""
        self.console.print("\n[bold yellow]多选模式说明:[/bold yellow]")
        self.console.print("• 输入单个数字: 5")
        self.console.print("• 输入范围: 1-5") 
        self.console.print("• 输入多个: 1,3,5")
        self.console.print("• 全选: all")
        
        while True:
            choice = Prompt.ask("\n[bold cyan]请输入选择[/bold cyan]").strip().lower()
            
            try:
                if choice == "all":
                    self.console.print(f"[green]✅ 已选择全部 {len(students)} 名学生[/green]")
                    return students.copy()
                
                selected_indices = self._parse_selection(choice, len(students))
                if selected_indices:
                    selected_students = [students[i] for i in sorted(selected_indices)]
                    self.console.print(f"[green]✅ 已选择 {len(selected_students)} 名学生[/green]")
                    return selected_students
                else:
                    self.console.print("[red]⚠️  请至少选择一名学生[/red]")
                    
            except ValueError as e:
                self.console.print(f"[red]⚠️  输入格式错误: {str(e)}[/red]")
    
    def _handle_ascii_multiple_selection(self, students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理多选（ASCII版本）"""
        print("\n多选模式:")
        print("• 输入单个数字: 5")
        print("• 输入范围: 1-5")
        print("• 输入多个: 1,3,5") 
        print("• 全选: all")
        
        while True:
            choice = input("\n请输入选择: ").strip().lower()
            
            try:
                if choice == "all":
                    print(f"✅ 已选择全部 {len(students)} 名学生")
                    return students.copy()
                
                selected_indices = self._parse_selection(choice, len(students))
                if selected_indices:
                    selected_students = [students[i] for i in sorted(selected_indices)]
                    print(f"✅ 已选择 {len(selected_students)} 名学生")
                    return selected_students
                else:
                    print("⚠️  请至少选择一名学生")
                    
            except ValueError as e:
                print(f"⚠️  输入格式错误: {str(e)}")
    
    def _parse_selection(self, choice: str, total_count: int) -> set:
        """解析选择字符串"""
        selected_indices = set()
        
        parts = choice.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                # 处理范围选择
                start, end = part.split('-', 1)
                start_idx = int(start.strip()) - 1
                end_idx = int(end.strip()) - 1
                if 0 <= start_idx < total_count and 0 <= end_idx < total_count:
                    for i in range(min(start_idx, end_idx), max(start_idx, end_idx) + 1):
                        selected_indices.add(i)
                else:
                    raise ValueError("范围超出有效值")
            else:
                # 处理单个选择
                idx = int(part) - 1
                if 0 <= idx < total_count:
                    selected_indices.add(idx)
                else:
                    raise ValueError("编号超出范围")
        
        return selected_indices
    
    def show_progress(self, total: int, description: str = "处理中"):
        """显示进度条"""
        if not self.console:
            # ASCII版本使用tqdm
            from tqdm import tqdm
            return tqdm(total=total, desc=description, unit="项")
        
        # Rich版本进度条
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        )
    
    def show_success(self, message: str):
        """显示成功消息"""
        if self.console:
            self.console.print(f"[bold green]✅ {message}[/bold green]")
        else:
            print(f"✅ {message}")
    
    def show_error(self, message: str):
        """显示错误消息"""
        if self.console:
            self.console.print(f"[bold red]❌ {message}[/bold red]")
        else:
            print(f"❌ {message}")
    
    def show_warning(self, message: str):
        """显示警告消息"""
        if self.console:
            self.console.print(f"[bold yellow]⚠️  {message}[/bold yellow]")
        else:
            print(f"⚠️  {message}")
    
    def show_info(self, message: str):
        """显示信息消息"""
        if self.console:
            self.console.print(f"[bold blue]ℹ️  {message}[/bold blue]")
        else:
            print(f"ℹ️  {message}")
    
    def confirm(self, message: str) -> bool:
        """确认对话框"""
        if self.console:
            return Confirm.ask(f"[bold cyan]{message}[/bold cyan]")
        else:
            choice = input(f"{message} (y/N): ").strip().lower()
            return choice in ['y', 'yes']
    
    def input_text(self, prompt: str, default: str = None) -> str:
        """文本输入"""
        if self.console:
            return Prompt.ask(f"[bold cyan]{prompt}[/bold cyan]", default=default)
        else:
            if default:
                return input(f"{prompt} [{default}]: ") or default
            else:
                return input(f"{prompt}: ")
    
    def input_int(self, prompt: str, min_val: int = None, max_val: int = None) -> int:
        """整数输入"""
        while True:
            try:
                if self.console:
                    value_str = Prompt.ask(f"[bold cyan]{prompt}[/bold cyan]")
                    value = int(value_str)
                else:
                    value = int(input(f"{prompt}: "))
                
                if min_val is not None and value < min_val:
                    self.show_error(f"值必须大于等于 {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    self.show_error(f"值必须小于等于 {max_val}")
                    continue
                
                return value
            except ValueError:
                self.show_error("请输入有效的整数")
    
    def pause(self, message: str = "按Enter键继续..."):
        """暂停等待用户输入"""
        if self.console:
            Prompt.ask(f"[dim]{message}[/dim]", default="")
        else:
            input(message) 