#!/usr/bin/env python3
"""
泰迪杯项目清理工具
用于清理临时文件、Excel锁文件等
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

# 获取项目根目录
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

# 添加项目根目录到Python路径
sys.path.insert(0, str(project_root))

def clean_excel_locks(directory=None, verbose=True):
    """清理Excel锁定文件"""
    if directory is None:
        directory = project_root / "data" / "processed"
    else:
        directory = Path(directory)
    
    if not directory.exists():
        if verbose:
            print(f"目录不存在: {directory}")
        return 0
    
    if verbose:
        print(f"正在清理Excel锁定文件: {directory}")
    
    # 查找所有以~$开头的文件（Excel锁定文件）
    lock_files = list(directory.glob("~$*"))
    
    if not lock_files:
        if verbose:
            print("未找到Excel锁定文件")
        return 0
    
    count = 0
    for file in lock_files:
        try:
            file.unlink()
            count += 1
            if verbose:
                print(f"已删除: {file.name}")
        except Exception as e:
            if verbose:
                print(f"无法删除 {file.name}: {str(e)}")
    
    if verbose:
        print(f"清理完成! 共删除 {count}/{len(lock_files)} 个锁定文件")
    
    return count

def clean_pycache(directory=None, verbose=True):
    """清理Python缓存文件"""
    if directory is None:
        directory = project_root
    else:
        directory = Path(directory)
    
    if not directory.exists():
        if verbose:
            print(f"目录不存在: {directory}")
        return 0
    
    if verbose:
        print(f"正在清理Python缓存文件...")
    
    # 查找所有__pycache__目录和.pyc文件
    pycache_dirs = list(directory.glob("**/__pycache__"))
    pyc_files = list(directory.glob("**/*.pyc"))
    
    # 删除__pycache__目录
    count_dirs = 0
    for dir_path in pycache_dirs:
        try:
            shutil.rmtree(dir_path)
            count_dirs += 1
            if verbose:
                print(f"已删除目录: {dir_path.relative_to(project_root)}")
        except Exception as e:
            if verbose:
                print(f"无法删除目录 {dir_path.relative_to(project_root)}: {str(e)}")
    
    # 删除.pyc文件
    count_files = 0
    for file in pyc_files:
        try:
            file.unlink()
            count_files += 1
            if verbose:
                print(f"已删除文件: {file.relative_to(project_root)}")
        except Exception as e:
            if verbose:
                print(f"无法删除文件 {file.relative_to(project_root)}: {str(e)}")
    
    if verbose:
        print(f"清理完成! 共删除 {count_dirs} 个__pycache__目录和 {count_files} 个.pyc文件")
    
    return count_dirs + count_files

def clean_temp_files(directory=None, verbose=True):
    """清理临时文件"""
    if directory is None:
        directory = project_root / "data" / "temp"
    else:
        directory = Path(directory)
    
    if not directory.exists():
        if verbose:
            print(f"目录不存在: {directory}")
        return 0
    
    if verbose:
        print(f"正在清理临时文件: {directory}")
    
    # 保留.gitkeep文件
    count = 0
    for file in directory.iterdir():
        if file.name != ".gitkeep" and file.is_file():
            try:
                file.unlink()
                count += 1
                if verbose:
                    print(f"已删除: {file.name}")
            except Exception as e:
                if verbose:
                    print(f"无法删除 {file.name}: {str(e)}")
    
    if verbose:
        print(f"清理完成! 共删除 {count} 个临时文件")
    
    return count

def main():
    parser = argparse.ArgumentParser(description="泰迪杯项目清理工具")
    parser.add_argument("--excel-locks", action="store_true", help="清理Excel锁定文件")
    parser.add_argument("--pycache", action="store_true", help="清理Python缓存文件")
    parser.add_argument("--temp", action="store_true", help="清理临时文件")
    parser.add_argument("--all", action="store_true", help="清理所有类型的文件")
    parser.add_argument("--directory", "-d", help="指定目录")
    parser.add_argument("--quiet", "-q", action="store_true", help="安静模式，不输出详细信息")
    
    args = parser.parse_args()
    
    # 如果没有指定任何选项，显示帮助
    if not (args.excel_locks or args.pycache or args.temp or args.all):
        parser.print_help()
        return
    
    verbose = not args.quiet
    
    # 清理所有类型的文件
    if args.all:
        clean_excel_locks(args.directory, verbose)
        clean_pycache(args.directory, verbose)
        clean_temp_files(args.directory, verbose)
        return
    
    # 根据选项清理特定类型的文件
    if args.excel_locks:
        clean_excel_locks(args.directory, verbose)
    
    if args.pycache:
        clean_pycache(args.directory, verbose)
    
    if args.temp:
        clean_temp_files(args.directory, verbose)

if __name__ == "__main__":
    main() 