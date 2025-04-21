"""
元数据处理流程图生成脚本
作者：B成员
日期：2023-04-06
更新：2023-04-12 - 优化流程图排版和连接线
更新：2023-04-14 - 进一步改进文字排版和流程图布局
更新：2023-04-16 - 精细调整元素间距和标签位置，解决文字重叠问题
更新：2023-04-18 - 改进中文字体支持，确保在不同环境中正确显示
更新：2023-04-22 - 简化字体处理方式
更新：2023-04-23 - 修复箭头连接问题、文字重叠和方块间距
更新：2023-04-24 - 修复方块显示不全、线条连接错误和文字重叠问题
更新：2023-04-25 - 修复线穿过方块问题和文字位置问题，确保黄色方块完全显示
更新：2023-04-26 - 修复第三列方块未显示完全问题，完善线条连接到方块边缘
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyArrowPatch, FancyBboxPatch
import matplotlib.patheffects as path_effects
import matplotlib.font_manager as fm
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 确保输出目录存在
os.makedirs("data/analysis/plots", exist_ok=True)

def create_metadata_flow_diagram():
    """创建元数据处理流程图"""
    
    # 设置中文字体支持 - 简化方法
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    
    # 设置图形属性
    plt.figure(figsize=(16, 12), dpi=100)
    
    # 打印字体设置信息
    logger.info(f"当前字体配置: sans-serif={plt.rcParams['font.sans-serif']}")
    
    # 创建图形和子图 - 使用更大的画布提供足够空间
    fig, ax = plt.subplots(figsize=(26, 20))  # 再次增加画布大小，特别是宽度
    
    # 设置背景颜色
    ax.set_facecolor('#f9f9f9')
    
    # 移除坐标轴
    ax.set_axis_off()
    
    # 扩大绘图区域以提供更多空间
    ax.set_xlim(-10, 240)  # 大幅增加水平空间
    ax.set_ylim(-10, 150)  # 保持足够的垂直空间
    
    # 定义颜色方案
    colors = {
        'pdf': '#3498db',        # 蓝色
        'extract': '#2ecc71',    # 绿色
        'process': '#e74c3c',    # 红色
        'store': '#f39c12',      # 橙色
        'arrow': '#95a5a6',      # 灰色
        'background': '#ecf0f1', # 浅灰色
        'text': '#2c3e50',       # 深蓝色
        'stage': '#34495e',      # 阶段标签颜色
        'note': '#7f8c8d'        # 注释颜色
    }
    
    # 添加标题
    title = ax.text(110, 135, '竞赛信息元数据处理流程', 
                   fontsize=32, fontweight='bold', ha='center', color=colors['text'])
    title.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
    
    # 绘制框和箭头的函数
    def add_box(x, y, width, height, label, color, alpha=0.9):
        """添加一个带阴影效果的框"""
        # 先添加阴影
        shadow = FancyBboxPatch((x+0.7, y-0.7), width, height, boxstyle="round,pad=0.6", 
                             fc='gray', alpha=0.2, lw=0)
        ax.add_patch(shadow)
        
        # 再添加主框
        box = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.6", 
                          fc=color, ec='gray', alpha=alpha, lw=1)
        ax.add_patch(box)
        
        # 添加带描边的文字
        text = ax.text(x+width/2, y+height/2, label, ha='center', va='center', 
                    fontsize=16, fontweight='bold', color='white')
        text.set_path_effects([path_effects.withStroke(linewidth=2, foreground='black')])
        return box
    
    def add_arrow(start_box, end_box, label=None, connection_style='arc3,rad=0.0', 
                 start_side='right', end_side='left', text_offset=(0, 0), color=None):
        """添加箭头连接两个框"""
        arrow_color = color if color else colors['arrow']
        
        # 更精确地计算连接点坐标，确保箭头连接到方块边缘而不是内部
        if start_side == 'right':
            start_x = start_box.get_x() + start_box.get_width() + 0.5  # 增加外部偏移
            start_y = start_box.get_y() + start_box.get_height()/2
        elif start_side == 'left':
            start_x = start_box.get_x() - 0.5  # 增加外部偏移
            start_y = start_box.get_y() + start_box.get_height()/2
        elif start_side == 'top':
            start_x = start_box.get_x() + start_box.get_width()/2
            start_y = start_box.get_y() + start_box.get_height() + 0.5  # 增加外部偏移
        else:  # bottom
            start_x = start_box.get_x() + start_box.get_width()/2
            start_y = start_box.get_y() - 0.5  # 增加外部偏移
        
        # 更精确地计算终点坐标，确保箭头连接到方块边缘而不是内部
        if end_side == 'right':
            end_x = end_box.get_x() + end_box.get_width() + 0.5  # 增加外部偏移
            end_y = end_box.get_y() + end_box.get_height()/2
        elif end_side == 'left':
            end_x = end_box.get_x() - 0.5  # 增加外部偏移
            end_y = end_box.get_y() + end_box.get_height()/2
        elif end_side == 'top':
            end_x = end_box.get_x() + end_box.get_width()/2
            end_y = end_box.get_y() + end_box.get_height() + 0.5  # 增加外部偏移
        else:  # bottom
            end_x = end_box.get_x() + end_box.get_width()/2
            end_y = end_box.get_y() - 0.5  # 增加外部偏移
        
        # 创建箭头 - 使用更大的收缩值，确保箭头不会穿过方块
        arrow = FancyArrowPatch((start_x, start_y), (end_x, end_y),
                              arrowstyle='-|>', color=arrow_color,
                              linewidth=2, connectionstyle=connection_style,
                              shrinkA=8, shrinkB=8)  # 再次增加收缩值，确保箭头不会穿过方块
        ax.add_patch(arrow)
        
        # 计算线条中点，用于放置标签
        if connection_style == 'arc3,rad=0.0':
            # 直线中点
            mid_x = (start_x + end_x) / 2 + text_offset[0]
            mid_y = (start_y + end_y) / 2 + text_offset[1]
        else:
            # 弧线中点 - 使用更准确的计算方法
            rad = float(connection_style.split('=')[1].rstrip(')'))
            mid_x = (start_x + end_x) / 2 + rad * (-(end_y - start_y)) / 2 + text_offset[0]
            mid_y = (start_y + end_y) / 2 + rad * (end_x - start_x) / 2 + text_offset[1]
        
        # 添加带背景的文本标签
        if label:
            text = ax.text(mid_x, mid_y, label, ha='center', va='center',
                        fontsize=12, fontweight='bold', color=colors['text'],
                        bbox=dict(facecolor='white', alpha=0.9, edgecolor='lightgray', 
                                 boxstyle='round,pad=0.4', linewidth=0.5))
        
        return arrow
    
    def add_note(x, y, text, label_box=None, offset=(0, -10), ha='center'):
        """添加注释文本，直接关联到特定方块下方"""
        if label_box:
            # 如果提供了方块，则计算相对于方块的位置
            x = label_box.get_x() + label_box.get_width()/2 + offset[0]
            y = label_box.get_y() + offset[1]
            
        note_props = dict(boxstyle='round', facecolor='#f8f8f8', alpha=0.9, pad=0.5, 
                    edgecolor='lightgray', linewidth=0.8)
        return ax.text(x, y, text, fontsize=10, style='italic', 
                     bbox=note_props, color=colors['note'], ha=ha)
    
    def add_stage_label(x, y, text):
        """添加阶段标签"""
        stage_props = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, 
                     edgecolor=colors['stage'], linewidth=1.5)
        return ax.text(x, y, text, fontsize=12, bbox=stage_props, ha='center', 
                     fontweight='bold', color=colors['stage'])
    
    # 重新设计布局 - 使用更大的间距，确保所有元素完全显示
    # 定义基本间距和尺寸
    box_width = 30  # 方块宽度
    box_height = 18  # 方块高度
    h_gap = 60  # 大幅增加水平间距
    v_gap = 35  # 保持足够的垂直间距
    
    # 第一行：输入和预处理
    row1_y = 105
    pdf_box = add_box(25, row1_y, box_width, box_height, "PDF文件", colors['pdf'])
    preprocess_box = add_box(25 + box_width + h_gap, row1_y, box_width, box_height, "预处理", colors['pdf'])
    
    # 第二行：提取模块
    row2_y = row1_y - v_gap
    text_extract_box = add_box(25, row2_y, box_width, box_height, "文本提取", colors['extract'])
    table_extract_box = add_box(25 + box_width + h_gap, row2_y, box_width, box_height, "表格提取", colors['extract'])
    pattern_match_box = add_box(25 + 2 * (box_width + h_gap), row2_y, box_width, box_height, "模式匹配", colors['extract'])
    
    # 第三行：处理模块
    row3_y = row2_y - v_gap
    clean_box = add_box(25, row3_y, box_width, box_height, "数据清洗", colors['process'])
    validate_box = add_box(25 + box_width + h_gap, row3_y, box_width, box_height, "数据验证", colors['process'])
    merge_box = add_box(25 + 2 * (box_width + h_gap), row3_y, box_width, box_height, "数据合并", colors['process'])
    
    # 第四行：存储模块
    row4_y = row3_y - v_gap
    save_box = add_box(25 + box_width + h_gap, row4_y, box_width, box_height, "数据存储", colors['store'])
    
    # 添加连接箭头 - 重新设计以确保正确连接到方块边缘
    # 第一行连接
    add_arrow(pdf_box, preprocess_box, "输入", connection_style='arc3,rad=0.0')
    
    # 预处理到三个提取模块的连接
    add_arrow(preprocess_box, text_extract_box, "提取文本", 
             connection_style='arc3,rad=-0.2', start_side='bottom', end_side='top', 
             text_offset=(-15, 5))
    
    add_arrow(preprocess_box, table_extract_box, "提取表格", 
             connection_style='arc3,rad=0.0', start_side='bottom', end_side='top',
             text_offset=(0, 5))
    
    add_arrow(preprocess_box, pattern_match_box, "提取模式", 
             connection_style='arc3,rad=0.2', start_side='bottom', end_side='top', 
             text_offset=(15, 5))
    
    # 第二行到第三行的垂直连接
    add_arrow(text_extract_box, clean_box, "原始文本", 
             connection_style='arc3,rad=0.0', start_side='bottom', end_side='top',
             text_offset=(0, 5))
    
    add_arrow(table_extract_box, validate_box, "表格数据", 
             connection_style='arc3,rad=0.0', start_side='bottom', end_side='top',
             text_offset=(0, 5))
    
    add_arrow(pattern_match_box, merge_box, "匹配结果", 
             connection_style='arc3,rad=0.0', start_side='bottom', end_side='top',
             text_offset=(0, 5))
    
    # 第三行之间的横向连接
    add_arrow(clean_box, validate_box, "清洗数据", 
             connection_style='arc3,rad=0.1',
             text_offset=(0, 4))
    
    add_arrow(validate_box, merge_box, "有效数据", 
             connection_style='arc3,rad=0.1',
             text_offset=(0, 4))
    
    # 第三行到第四行的连接
    add_arrow(merge_box, save_box, "合并结果", 
             connection_style='arc3,rad=-0.2', start_side='bottom', end_side='top', 
             text_offset=(7, 5))
    
    # 添加阶段标签 - 重新定位更靠右
    stage_x = 25 + 3 * (box_width + h_gap) + 10
    add_stage_label(stage_x, row1_y + 5, "输入阶段")
    add_stage_label(stage_x, row2_y + 5, "提取阶段")
    add_stage_label(stage_x, row3_y + 5, "处理阶段")
    add_stage_label(stage_x, row4_y + 5, "存储阶段")
    
    # 添加注释 - 直接关联到对应方块
    # 第二行注释
    add_note(0, 0, "使用pdfplumber提取PDF内容", text_extract_box, offset=(0, -7))
    add_note(0, 0, "使用正则表达式识别结构化数据", table_extract_box, offset=(0, -7))
    add_note(0, 0, "匹配模式", pattern_match_box, offset=(0, -7))
    
    # 第三行注释
    add_note(0, 0, "去噪声，标准化格式", clean_box, offset=(0, -7))
    add_note(0, 0, "检查完整性和一致性", validate_box, offset=(0, -7))
    add_note(0, 0, "合并多源数据", merge_box, offset=(0, -7))
    
    # 第四行注释
    add_note(0, 0, "保存为Excel格式", save_box, offset=(0, -7))
    
    # 添加水印
    watermark = ax.text(110, 15, "泰迪杯竞赛数据分析系统", ha='center', va='bottom', 
                       color='gray', alpha=0.4, fontsize=12, style='italic')
    
    # 保存图像 - 使用高DPI确保清晰度
    plt.tight_layout(pad=4.0)  # 增加边距确保所有内容可见
    output_path = "data/analysis/plots/metadata_process_flow.png"
    plt.savefig(output_path, dpi=600, bbox_inches='tight', pad_inches=1.5)  # 增加边距
    plt.close()
    
    print(f"元数据处理流程图已保存至: {output_path}")

if __name__ == "__main__":
    create_metadata_flow_diagram()
    
    # 打印可供用户使用的其他制作流程图的工具建议
    print("\n推荐的流程图制作工具:")
    print("1. draw.io (diagrams.net) - 免费的在线流程图工具，支持多种图表类型")
    print("2. Lucidchart - 专业的图表制作工具，有免费和付费版本")
    print("3. Microsoft Visio - 专业流程图软件，Office套件的一部分")
    print("4. Figma - 设计师常用工具，也适合制作流程图")
    print("5. PlantUML - 使用代码生成图表，适合程序员使用")
    print("6. Graphviz - 命令行图形可视化软件，强大但学习曲线较陡")
    print("\n调整当前流程图的方法:")
    print("1. 修改本脚本中的元素位置和大小参数")
    print("2. 调整连接线的弧度参数(connection_style和rad值)")
    print("3. 更改文本标签的偏移量(text_offset参数)")
    print("4. 可以尝试不同的颜色方案(colors字典)")
    print("5. 修改图像尺寸(figsize参数)和DPI值来调整输出图像的大小和清晰度") 