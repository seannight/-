import os
import sys
import unittest
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入测试模块
from tests_real.data_processing.test_extract_tables import TestTableExtractor

if __name__ == '__main__':
    # 创建测试套件
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTableExtractor))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果统计
    print("\n测试结果统计:")
    print(f"运行测试: {result.testsRun}")
    print(f"通过测试: {result.testsRun - len(result.errors) - len(result.failures)}")
    print(f"失败测试: {len(result.failures)}")
    print(f"错误测试: {len(result.errors)}")
    
    # 如果有失败或错误，显示详细信息
    if result.failures:
        print("\n失败测试详情:")
        for test, error in result.failures:
            print(f"\n{test}")
            print(error)
            
    if result.errors:
        print("\n错误测试详情:")
        for test, error in result.errors:
            print(f"\n{test}")
            print(error)
