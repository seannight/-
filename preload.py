#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统预加载脚本
用于启动前预热缓存，提高首次响应速度
"""

import os
import sys
import time
import multiprocessing as mp
from pathlib import Path
import logging
import importlib

# 设置项目根目录
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('preload')

def preload_pdf_processor():
    """预加载PDF处理模块"""
    logger.info("正在预加载PDF处理模块...")
    start_time = time.time()
    
    try:
        # 导入相关模块
        from app.data_processing import extract_tables, extract_text
        
        # 预热表格提取器
        logger.info("初始化表格提取器...")
        extractor = extract_tables.TableExtractor()
        
        # 预热文本提取器
        logger.info("初始化文本提取器...")
        text_processor = extract_text.TextExtractor()
        
        # 尝试预处理一个小型PDF文件（如果存在）
        pdf_samples = list(Path(ROOT_DIR / "data" / "samples").glob("*.pdf"))
        if pdf_samples:
            sample_pdf = str(pdf_samples[0])
            logger.info(f"预处理样例PDF: {sample_pdf}")
            # 提取表格
            _ = extractor.extract_tables(sample_pdf)
            # 提取文本
            _ = text_processor.extract_text(sample_pdf)
        
        elapsed = time.time() - start_time
        logger.info(f"PDF处理模块预加载完成，耗时: {elapsed:.2f}秒")
        return True
    except Exception as e:
        logger.error(f"PDF处理模块预加载失败: {str(e)}")
        return False

def preload_qa_engine():
    """预加载问答引擎"""
    logger.info("正在预加载问答引擎...")
    start_time = time.time()
    
    try:
        # 导入相关模块
        from app.qa import engine
        
        # 初始化问答引擎
        logger.info("初始化问答引擎...")
        qa_engine = engine.QAEngine()
        
        # 预热引擎 - 处理一个简单问题
        logger.info("预热问答引擎...")
        _ = qa_engine.answer("比赛时间是什么时候?")
        
        elapsed = time.time() - start_time
        logger.info(f"问答引擎预加载完成，耗时: {elapsed:.2f}秒")
        return True
    except Exception as e:
        logger.error(f"问答引擎预加载失败: {str(e)}")
        return False

def preload_common_modules():
    """预加载公共模块"""
    logger.info("正在预加载公共模块...")
    start_time = time.time()
    
    modules_to_load = [
        "fastapi",
        "uvicorn",
        "pandas",
        "numpy",
        "app.core.config",
        "app.utils.performance",
        "app.core.simple_monitor"
    ]
    
    success_count = 0
    for module_name in modules_to_load:
        try:
            importlib.import_module(module_name)
            success_count += 1
        except ImportError as e:
            logger.warning(f"无法导入模块 {module_name}: {str(e)}")
    
    elapsed = time.time() - start_time
    logger.info(f"公共模块预加载完成 ({success_count}/{len(modules_to_load)})，耗时: {elapsed:.2f}秒")
    return success_count > 0

def preload_component(name):
    """预加载单个组件的包装函数"""
    if name == "pdf":
        return preload_pdf_processor()
    elif name == "qa":
        return preload_qa_engine()
    elif name == "common":
        return preload_common_modules()
    else:
        logger.error(f"未知组件: {name}")
        return False

def main():
    """主函数 - 并行预加载所有组件"""
    logger.info("=" * 50)
    logger.info("系统预加载开始")
    logger.info("=" * 50)
    
    start_time = time.time()
    
    # 确定CPU核心数，用于并行处理
    cpu_count = max(1, mp.cpu_count() - 1)  # 保留一个核心给系统
    logger.info(f"检测到 {cpu_count+1} 个CPU核心，将使用 {cpu_count} 个核心进行预加载")
    
    # 需要预加载的组件
    components = ["common", "pdf", "qa"]
    
    # 使用进程池并行预加载
    with mp.Pool(min(len(components), cpu_count)) as pool:
        results = pool.map(preload_component, components)
    
    # 汇总结果
    success_count = sum(results)
    total_time = time.time() - start_time
    
    logger.info("=" * 50)
    logger.info(f"预加载完成: {success_count}/{len(components)} 组件加载成功")
    logger.info(f"总耗时: {total_time:.2f}秒")
    logger.info("=" * 50)
    
    return success_count == len(components)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 