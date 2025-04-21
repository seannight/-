#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
泰迪杯智能客服系统 - 依赖安装工具 (纯ASCII修复版)
用于按需安装requirements.txt中的依赖
支持分组安装、检查已安装依赖和快速修复
"""
import os
import sys
import subprocess
import re
import platform
import time
from pathlib import Path
import argparse

# 彩色输出支持
if platform.system() == 'Windows':
    os.system('color')
    
# 彩色输出
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def get_requirements_path():
    """获取requirements.txt的路径"""
    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parent
    return root_dir / "requirements.txt"

def parse_requirements():
    """解析requirements.txt文件，提取分组信息"""
    req_path = get_requirements_path()
    if not req_path.exists():
        print(f"{RED}错误: 找不到requirements.txt文件{RESET}")
        return None
    
    with open(req_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析分组
    groups = {}
    current_group = "core"
    group_pkgs = []
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            # 检查是否是分组标记
            if '# 分组:' in line or '# 组:' in line or '# Group:' in line:
                match = re.search(r'#\s*(?:分组|组|Group):\s*(\w+)', line)
                if match:
                    # 保存当前分组
                    if group_pkgs:
                        groups[current_group] = group_pkgs
                    
                    # 开始新分组
                    current_group = match.group(1)
                    group_pkgs = []
            continue
            
        # 移除注释和版本信息
        pkg = line.split('#')[0].strip()
        pkg = re.sub(r'[<>=].*$', '', pkg).strip()
        if pkg:
            group_pkgs.append(pkg)
    
    # 保存最后一个分组
    if group_pkgs:
        groups[current_group] = group_pkgs
    
    return groups

def check_installed(packages):
    """检查哪些包已经安装"""
    installed = []
    missing = []
    
    for pkg in packages:
        try:
            # 尝试导入包
            __import__(pkg.replace('-', '_'))
            installed.append(pkg)
        except ImportError:
            # 尝试使用pip检查
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'show', pkg],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                if result.returncode == 0:
                    installed.append(pkg)
                else:
                    missing.append(pkg)
            except:
                missing.append(pkg)
    
    return installed, missing

def install_package(pkg, mirror=False):
    """安装单个包"""
    print(f"\n{BLUE}安装包: {pkg}{RESET}")
    
    # 构建基本命令
    cmd = [sys.executable, '-m', 'pip', 'install']
    
    # 添加镜像源
    if mirror:
        cmd.extend(['-i', 'https://pypi.tuna.tsinghua.edu.cn/simple'])
    
    # 特殊处理psutil包，避免空字符问题
    if pkg.lower() == 'psutil':
        print(f"{YELLOW}使用特殊处理安装psutil{RESET}")
        cmd.append('psutil')
    else:
        cmd.append(pkg)
    
    # 执行安装命令
    try:
        # 使用文本模式运行命令，避免二进制输出导致问题
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            errors='replace'  # 替换无法解码的字符
        )
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print(f"{GREEN}安装成功: {pkg}{RESET}")
            return True
        else:
            print(f"{RED}安装失败: {pkg}{RESET}")
            print(f"{YELLOW}错误信息: {stderr}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}安装出错: {str(e)}{RESET}")
        return False

def install_group(group_name, packages, mirror=False):
    """安装一组包"""
    print(f"\n{GREEN}{BOLD}安装分组: {group_name} ({len(packages)}个包){RESET}")
    
    success = []
    failed = []
    
    for pkg in packages:
        if install_package(pkg, mirror):
            success.append(pkg)
        else:
            failed.append(pkg)
    
    # 显示安装结果
    print(f"\n{BOLD}安装结果 - {group_name}:{RESET}")
    success_rate = len(success) / len(packages) * 100 if packages else 0
    print(f"总计: {len(packages)}个包")
    print(f"成功: {len(success)}个包 ({success_rate:.1f}%)")
    print(f"失败: {len(failed)}个包")
    
    if failed:
        print(f"\n{YELLOW}以下包安装失败:{RESET}")
        for pkg in failed:
            print(f"  - {pkg}")
    
    return success, failed

def display_menu(groups):
    """显示用户菜单"""
    print(f"\n{CYAN}{BOLD}泰迪杯智能客服系统 - 依赖安装工具{RESET}")
    print(f"{CYAN}{'=' * 50}{RESET}")
    print(f"检测到以下依赖分组:")
    
    for i, (group_name, packages) in enumerate(groups.items(), 1):
        installed, missing = check_installed(packages)
        installed_percent = len(installed) / len(packages) * 100 if packages else 0
        
        if not missing:
            status = f"{GREEN}已完成{RESET}"
        elif installed:
            status = f"{YELLOW}部分安装 ({installed_percent:.1f}%){RESET}"
        else:
            status = f"{RED}未安装{RESET}"
        
        print(f"{i}. {BOLD}{group_name}{RESET} - {len(packages)}个包 - {status}")
    
    print(f"\n{BOLD}操作选项:{RESET}")
    print(f"a. 安装所有依赖")
    print(f"c. 检查安装状态")
    print(f"u. 更新已安装的包")
    print(f"m. 使用镜像源安装(更快)")
    print(f"q. 退出程序")
    
    choice = input(f"\n{BOLD}请输入选项 (1-{len(groups)}, a, c, u, m, q): {RESET}")
    return choice

def install_all_dependencies(groups, mirror=False):
    """安装所有依赖"""
    all_success = []
    all_failed = []
    
    print(f"\n{MAGENTA}{BOLD}开始安装所有依赖 ({sum(len(pkgs) for pkgs in groups.values())}个包){RESET}")
    
    for group_name, packages in groups.items():
        success, failed = install_group(group_name, packages, mirror)
        all_success.extend(success)
        all_failed.extend(failed)
    
    # 显示总体结果
    print(f"\n{BOLD}{MAGENTA}总体安装结果:{RESET}")
    total = len(all_success) + len(all_failed)
    success_rate = len(all_success) / total * 100 if total else 0
    print(f"总计: {total}个包")
    print(f"成功: {len(all_success)}个包 ({success_rate:.1f}%)")
    print(f"失败: {len(all_failed)}个包")
    
    if all_failed:
        print(f"\n{YELLOW}以下包安装失败，可能需要手动安装:{RESET}")
        for pkg in all_failed:
            print(f"  - {pkg}")
    
    return len(all_failed) == 0

def check_all_dependencies(groups):
    """检查所有依赖的安装状态"""
    print(f"\n{CYAN}{BOLD}依赖安装状态检查{RESET}")
    print(f"{CYAN}{'=' * 50}{RESET}")
    
    all_packages = sum(len(pkgs) for pkgs in groups.values())
    all_installed = 0
    all_missing = 0
    
    for group_name, packages in groups.items():
        installed, missing = check_installed(packages)
        all_installed += len(installed)
        all_missing += len(missing)
        
        installed_percent = len(installed) / len(packages) * 100 if packages else 0
        
        if not missing:
            status = f"{GREEN}已完成{RESET}"
        elif installed:
            status = f"{YELLOW}部分安装 ({installed_percent:.1f}%){RESET}"
        else:
            status = f"{RED}未安装{RESET}"
        
        print(f"\n{BOLD}分组: {group_name}{RESET} - {status}")
        print(f"总计: {len(packages)}个包")
        print(f"已安装: {len(installed)}个包")
        print(f"未安装: {len(missing)}个包")
        
        if missing:
            print(f"\n{YELLOW}未安装的包:{RESET}")
            for pkg in missing:
                print(f"  - {pkg}")
    
    # 显示总体结果
    print(f"\n{BOLD}{MAGENTA}总体安装状态:{RESET}")
    install_rate = all_installed / all_packages * 100 if all_packages else 0
    print(f"总计: {all_packages}个包")
    print(f"已安装: {all_installed}个包 ({install_rate:.1f}%)")
    print(f"未安装: {all_missing}个包")

def update_installed_packages(groups):
    """更新已安装的包"""
    print(f"\n{CYAN}{BOLD}更新已安装的包{RESET}")
    print(f"{CYAN}{'=' * 50}{RESET}")
    
    all_installed = []
    for packages in groups.values():
        installed, _ = check_installed(packages)
        all_installed.extend(installed)
    
    if not all_installed:
        print(f"{YELLOW}没有找到已安装的包{RESET}")
        return
    
    print(f"将更新 {len(all_installed)} 个已安装的包")
    confirm = input(f"{YELLOW}确定要更新吗? (y/n): {RESET}")
    
    if confirm.lower() != 'y':
        print("已取消更新")
        return
    
    # 更新包
    updated = []
    failed = []
    
    for pkg in all_installed:
        print(f"\n{BLUE}更新包: {pkg}{RESET}")
        try:
            cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', pkg]
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                errors='replace'
            )
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                updated.append(pkg)
            else:
                failed.append(pkg)
                print(f"{YELLOW}错误信息: {stderr}{RESET}")
        except Exception as e:
            failed.append(pkg)
            print(f"{RED}更新出错: {str(e)}{RESET}")
    
    # 显示结果
    print(f"\n{BOLD}{MAGENTA}更新结果:{RESET}")
    success_rate = len(updated) / len(all_installed) * 100 if all_installed else 0
    print(f"总计: {len(all_installed)}个包")
    print(f"成功: {len(updated)}个包 ({success_rate:.1f}%)")
    print(f"失败: {len(failed)}个包")
    
    if failed:
        print(f"\n{YELLOW}以下包更新失败:{RESET}")
        for pkg in failed:
            print(f"  - {pkg}")

def main():
    parser = argparse.ArgumentParser(description='泰迪杯智能客服系统依赖安装工具')
    parser.add_argument('--all', action='store_true', help='安装所有依赖')
    parser.add_argument('--check', action='store_true', help='检查依赖安装状态')
    parser.add_argument('--update', action='store_true', help='更新已安装的包')
    parser.add_argument('--group', type=str, help='安装指定分组的依赖')
    parser.add_argument('--mirror', action='store_true', help='使用镜像源安装')
    parser.add_argument('--psutil', action='store_true', help='单独安装psutil包')
    args = parser.parse_args()
    
    # 单独安装psutil
    if args.psutil:
        print(f"{CYAN}{BOLD}单独安装psutil包{RESET}")
        return 0 if install_package('psutil', args.mirror) else 1
    
    # 解析requirements.txt
    groups = parse_requirements()
    if not groups:
        return 1
    
    # 命令行模式
    if args.all:
        return 0 if install_all_dependencies(groups, args.mirror) else 1
    elif args.check:
        check_all_dependencies(groups)
        return 0
    elif args.update:
        update_installed_packages(groups)
        return 0
    elif args.group:
        if args.group in groups:
            success, failed = install_group(args.group, groups[args.group], args.mirror)
            return 0 if not failed else 1
        else:
            print(f"{RED}错误: 找不到分组 '{args.group}'{RESET}")
            print(f"可用的分组: {', '.join(groups.keys())}")
            return 1
    
    # 交互式模式
    while True:
        choice = display_menu(groups)
        
        if choice.lower() == 'q':
            break
        elif choice.lower() == 'a':
            install_all_dependencies(groups, False)
        elif choice.lower() == 'c':
            check_all_dependencies(groups)
        elif choice.lower() == 'u':
            update_installed_packages(groups)
        elif choice.lower() == 'm':
            install_all_dependencies(groups, True)
        elif choice.isdigit() and 1 <= int(choice) <= len(groups):
            # 选择特定分组
            group_name = list(groups.keys())[int(choice) - 1]
            install_group(group_name, groups[group_name], False)
        else:
            print(f"{RED}无效的选择，请重试{RESET}")
        
        # 暂停让用户阅读结果
        input(f"\n{BOLD}按Enter键继续...{RESET}")
    
    print(f"\n{GREEN}感谢使用依赖安装工具！{RESET}")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}用户中断安装{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}发生错误: {str(e)}{RESET}")
        sys.exit(1) 