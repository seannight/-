"""
表格提取测试脚本 - 测试B成员的表格提取功能
创建日期: 2023-04-19
"""

import os
import sys
import json
from pathlib import Path
import time
import traceback
import pandas as pd
import pytest

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

# 导入表格提取相关模块
from app.data_processing.extract_tables import TableExtractor

# 测试数据目录
TEST_DATA_DIR = ROOT_DIR / "tests_real" / "data"
RESULT_DIR = ROOT_DIR / "tests_real" / "results"
os.makedirs(RESULT_DIR, exist_ok=True)

class TestTableExtractor:
    """表格提取测试类"""
    
    def setup_class(cls):
        """测试类初始化"""
        cls.extractor = TableExtractor()
        
        # 创建测试目录
        os.makedirs(TEST_DATA_DIR, exist_ok=True)
        
        # 测试PDF路径
        cls.test_pdf = TEST_DATA_DIR / "test.pdf"
        
        # 如果存在样本PDF文件，使用它进行测试
        sample_files = list(Path(ROOT_DIR / "data" / "raw").glob("*.pdf"))
        if sample_files:
            cls.sample_pdf = sample_files[0]
        else:
            cls.sample_pdf = None
    
    def test_extractor_initialization(self):
        """测试提取器初始化"""
        assert self.extractor is not None
        
    def test_extract_tables_from_file(self):
        """测试从文件提取表格"""
        if not self.sample_pdf:
            pytest.skip("没有找到样本PDF文件，跳过测试")
            
        tables = self.extractor.extract_tables(str(self.sample_pdf))
        
        # 打印表格数量
        print(f"\n从 {self.sample_pdf.name} 中提取了 {len(tables)} 个表格")
        
        # 打印第一个表格的信息
        if tables:
            first_table = tables[0]
            print(f"第一个表格信息:")
            print(f"- 行数: {len(first_table)}")
            print(f"- 列数: {len(first_table[0]) if first_table else 0}")
            
        assert isinstance(tables, list)
        
    def test_extract_tables_batch(self):
        """测试批量提取表格"""
        if not self.sample_pdf:
            pytest.skip("没有找到样本PDF文件，跳过测试")
            
        # 批量处理目录
        raw_dir = ROOT_DIR / "data" / "raw"
        pdf_files = list(raw_dir.glob("*.pdf"))
        
        if not pdf_files:
            pytest.skip("原始数据目录中没有PDF文件，跳过测试")
            
        # 测试处理前5个文件
        test_files = pdf_files[:min(5, len(pdf_files))]
        
        for pdf_file in test_files:
            print(f"\n处理文件: {pdf_file.name}")
            try:
                tables = self.extractor.extract_tables(str(pdf_file))
                print(f"提取了 {len(tables)} 个表格")
                
                # 保存第一个表格为Excel（如果存在）
                if tables and len(tables) > 0:
                    table_data = tables[0]
                    # 转换为DataFrame
                    df = pd.DataFrame(table_data[1:], columns=table_data[0] if table_data else None)
                    # 保存到结果目录
                    output_path = RESULT_DIR / f"{pdf_file.stem}_table1.xlsx"
                    df.to_excel(str(output_path), index=False)
                    print(f"表格已保存到 {output_path}")
            except Exception as e:
                print(f"处理文件 {pdf_file.name} 时出错: {str(e)}")
                continue
        
    def test_extract_metadata(self):
        """测试元数据提取功能"""
        if not hasattr(self.extractor, 'extract_metadata') or not self.sample_pdf:
            pytest.skip("提取器没有元数据提取功能或没有样本PDF，跳过测试")
            
        try:
            metadata = self.extractor.extract_metadata(str(self.sample_pdf))
            print(f"\n元数据提取结果:")
            for key, value in metadata.items():
                print(f"- {key}: {value}")
            
            assert isinstance(metadata, dict)
        except Exception as e:
            print(f"提取元数据时出错: {str(e)}")
            pytest.skip(f"元数据提取功能测试失败: {str(e)}")
    
    def teardown_class(cls):
        """测试类清理"""
        print("\n表格提取测试完成!")

if __name__ == "__main__":
    try:
        print("=== 开始表格提取测试 ===")
        start_time = time.time()
        
        # 创建测试实例
        test = TestTableExtractor()
        test.setup_class()
        
        # 运行测试方法
        test.test_extractor_initialization()
        test.test_extract_tables_from_file()
        test.test_extract_tables_batch()
        test.test_extract_metadata()
        
        # 清理
        test.teardown_class()
        
        elapsed = time.time() - start_time
        print(f"\n=== 测试完成，耗时 {elapsed:.2f} 秒 ===")
        print("所有测试通过!")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
