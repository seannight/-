"""
数据可视化演示脚本 - 展示竞赛数据分析与可视化功能
作者: B成员
日期: 2023-04-08
更新: 2023-04-10 - 修改为直接使用竞赛信息提取结果.xlsx文件
更新: 2023-04-12 - 添加命令行参数支持和示例数据使用功能
更新: 2023-04-22 - 改进中文字体支持
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import argparse

# 添加父目录到系统路径，以便导入自定义模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.data_processing.data_analyzer import DataAnalyzer

# 忽略警告信息
warnings.filterwarnings("ignore")

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def main():
    """主函数：运行数据可视化演示"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='竞赛数据可视化演示')
    parser.add_argument('--sample', action='store_true', help='使用示例数据而非实际数据')
    args = parser.parse_args()
    
    # 确定使用的数据文件
    data_file = "data/processed/竞赛信息提取结果.xlsx"
    if args.sample:
        sample_file = "data/processed/竞赛信息提取结果_示例.xlsx"
        if os.path.exists(sample_file):
            data_file = sample_file
            print(f"使用示例数据: {sample_file}")
    elif os.path.exists("temp_config.txt"):
        with open("temp_config.txt", "r") as f:
            for line in f:
                if line.startswith("data_file="):
                    custom_file = line.strip().split("=")[1]
                    if os.path.exists(custom_file):
                        data_file = custom_file
                        print(f"使用配置指定的数据文件: {data_file}")
    
    # 打印欢迎信息
    print_welcome()
    
    # 检查数据目录
    if not check_data_paths(data_file):
        print("❌ 初始化失败，请确认数据目录存在")
        return
    
    # 创建分析器
    analyzer = DataAnalyzer(metadata_file=data_file)
    
    # 加载数据
    print("⏳ 正在加载数据...")
    if not analyzer.load_data():
        print("❌ 数据加载失败")
        return
    
    print("✅ 数据加载成功")
    
    # 选择演示模块
    while True:
        choice = show_menu()
        
        if choice == "1":
            # 元数据分析
            print("\n🔍 元数据分析...\n")
            metadata_analysis = analyzer.analyze_metadata()
            print_metadata_analysis(metadata_analysis)
            
        elif choice == "2":
            # 表格分析
            print("\n🔍 表格数据分析...\n")
            table_analysis = analyzer.analyze_tables()
            print_table_analysis(table_analysis)
            
        elif choice == "3":
            # 元数据可视化
            print("\n📊 生成元数据可视化图表...\n")
            analyzer.generate_metadata_visualizations()
            print_visualization_paths("元数据")
            
        elif choice == "4":
            # 表格可视化
            print("\n📊 生成表格数据可视化图表...\n")
            analyzer.generate_tables_visualizations()
            print_visualization_paths("表格数据")
            
        elif choice == "5":
            # 生成综合报告
            print("\n📝 生成综合分析报告...\n")
            report = analyzer.generate_comprehensive_report()
            print_report_summary(report)
            
        elif choice == "6":
            # 运行全部分析
            print("\n🚀 运行完整数据分析流程...\n")
            analyzer.run_full_analysis()
            print("\n✅ 完整分析流程已完成")
            print_all_output_paths()
            
        elif choice == "0":
            print("\n👋 感谢使用数据可视化演示系统，再见！")
            break
            
        else:
            print("\n❌ 无效的选择，请重新输入")
        
        input("\n按回车键继续...")

def print_welcome():
    """打印欢迎信息"""
    print("\n" + "="*60)
    print("🏆 竞赛数据分析与可视化演示系统 🏆".center(58))
    print("="*60)
    print("本系统展示从竞赛PDF文件中提取的数据分析与可视化功能")
    print("可以生成统计分析、图表可视化和综合报告")
    print("-"*60)

def check_data_paths(data_file="data/processed/竞赛信息提取结果.xlsx"):
    """
    检查必要的数据路径是否存在
    
    参数:
        data_file: 要检查的数据文件路径
    """
    # 确保所有必要的目录都存在
    required_paths = [
        "data/processed",
        "data/analysis",
        "data/analysis/plots",
        "data/analysis/reports",
        "logs"
    ]
    
    for path in required_paths:
        if not os.path.exists(path):
            print(f"创建目录: {path}")
            os.makedirs(path, exist_ok=True)
    
    # 检查元数据文件是否存在
    if not os.path.exists(data_file):
        print(f"⚠️ 警告: 元数据文件不存在: {data_file}")
        return False
    
    print(f"✅ 找到元数据文件: {data_file}")
    return True

def show_menu():
    """显示菜单并获取用户选择"""
    print("\n" + "-"*60)
    print("📋 功能菜单:".center(58))
    print("-"*60)
    print("1. 元数据分析 - 分析竞赛基本信息")
    print("2. 表格数据分析 - 分析提取的表格结构")
    print("3. 元数据可视化 - 生成元数据图表")
    print("4. 表格数据可视化 - 生成表格分析图表")
    print("5. 生成综合报告 - 创建完整分析报告")
    print("6. 运行全部分析 - 执行所有分析步骤")
    print("0. 退出系统")
    print("-"*60)
    
    return input("请输入选项 [0-6]: ")

def print_metadata_analysis(analysis):
    """打印元数据分析结果"""
    if not analysis:
        print("❌ 元数据分析结果为空")
        return
    
    print(f"📊 分析了 {analysis['total_competitions']} 个竞赛数据")
    
    if 'organization_counts' in analysis:
        print("\n📋 组织单位统计 (Top 5):")
        org_counts = dict(sorted(analysis['organization_counts'].items(), 
                                key=lambda x: x[1], reverse=True)[:5])
        for org, count in org_counts.items():
            print(f"  - {org}: {count} 个竞赛")
    
    if 'year_counts' in analysis:
        print("\n📅 竞赛按年份分布:")
        year_counts = dict(sorted(analysis['year_counts'].items()))
        for year, count in year_counts.items():
            print(f"  - {year}年: {count} 个竞赛")
    
    if 'level_counts' in analysis:
        print("\n🏅 竞赛级别分布:")
        for level, count in analysis['level_counts'].items():
            print(f"  - {level}: {count} 个竞赛")
    
    print(f"\n✅ 分析结果已保存至: data/analysis/reports/metadata_analysis.json")

def print_table_analysis(analysis):
    """打印表格分析结果"""
    if not analysis:
        print("❌ 表格分析结果为空")
        return
    
    print(f"📊 总表格数: {analysis['total_tables']}")
    print(f"📏 平均行数: {analysis['avg_rows_per_table']:.2f}")
    print(f"📏 平均列数: {analysis['avg_cols_per_table']:.2f}")
    print(f"⚠️ 空表格数: {analysis['empty_tables']}")
    print(f"📈 大型表格(>20行): {analysis['large_tables']}")
    
    print("\n📋 表格数量最多的文件 (Top 5):")
    top_files = dict(sorted(analysis['tables_per_file'].items(), 
                          key=lambda x: x[1], reverse=True)[:5])
    for file, count in top_files.items():
        print(f"  - {file}: {count} 个表格")
    
    print(f"\n✅ 分析结果已保存至: data/analysis/reports/tables_analysis.json")

def print_visualization_paths(data_type):
    """打印可视化图表路径"""
    plots_dir = "data/analysis/plots"
    
    # 获取相关图表文件
    if data_type == "元数据":
        relevant_files = [
            "competition_levels_pie.png",
            "top_organizations_bar.png",
            "competitions_by_year.png",
            "correlation_heatmap.png"
        ]
    else:  # 表格数据
        relevant_files = [
            "tables_per_file.png",
            "table_dimensions_scatter.png",
            "table_rows_histogram.png"
        ]
    
    print(f"📊 {data_type}可视化图表已生成:")
    for file in relevant_files:
        path = os.path.join(plots_dir, file)
        if os.path.exists(path):
            print(f"  - {path}")
    
    # 检查交互式图表
    html_files = [f for f in os.listdir(plots_dir) if f.endswith(".html")]
    if html_files:
        print("\n🌐 交互式图表 (HTML):")
        for file in html_files:
            if (data_type == "元数据" and any(x in file for x in ["competition", "organization", "year"])) or \
               (data_type == "表格数据" and any(x in file for x in ["table", "dimension"])):
                print(f"  - {os.path.join(plots_dir, file)}")

def print_report_summary(report):
    """打印综合报告摘要"""
    if not report:
        print("❌ 综合报告生成失败")
        return
    
    print("📝 综合报告摘要:")
    print(f"  - 生成时间: {report['生成时间']}")
    print(f"  - 竞赛总数: {report['元数据统计']['竞赛总数']}")
    
    if '数据质量评估' in report:
        print(f"  - 元数据完整度: {report['数据质量评估']['元数据完整度']}")
    
    if '建议' in report and report['建议']:
        print("\n💡 改进建议:")
        for suggestion in report['建议']:
            print(f"  - {suggestion}")
    
    print(f"\n✅ 完整报告已保存至:")
    print(f"  - data/analysis/reports/comprehensive_report.json")
    print(f"  - data/analysis/reports/comprehensive_report.html")

def print_all_output_paths():
    """打印所有输出文件路径"""
    print("\n📂 分析结果文件:")
    
    # 报告文件
    reports_dir = "data/analysis/reports"
    if os.path.exists(reports_dir):
        print("\n📝 报告文件:")
        for file in os.listdir(reports_dir):
            print(f"  - {os.path.join(reports_dir, file)}")
    
    # 图表文件
    plots_dir = "data/analysis/plots"
    if os.path.exists(plots_dir):
        print("\n📊 可视化图表:")
        png_files = [f for f in os.listdir(plots_dir) if f.endswith(".png")]
        for file in png_files:
            print(f"  - {os.path.join(plots_dir, file)}")
        
        print("\n🌐 交互式图表 (HTML):")
        html_files = [f for f in os.listdir(plots_dir) if f.endswith(".html")]
        for file in html_files:
            print(f"  - {os.path.join(plots_dir, file)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 程序被用户中断")
        print("👋 感谢使用，再见！")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc() 