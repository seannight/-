"""
知识图谱测试脚本 - 集成测试B和C成员第五周任务
创建日期: 2023-04-19
"""

import os
import sys
import json
from pathlib import Path
import time
import traceback

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

# 导入知识图谱相关模块
from app.models.knowledge_graph import KnowledgeGraph
from app.models.entity_extractor import EntityExtractor
from app.models.relation_extractor import RelationExtractor
from app.models.data_processor import DataProcessor
from app.models.visualizer import KnowledgeGraphVisualizer

# 测试数据目录
TEST_DATA_DIR = ROOT_DIR / "tests_real" / "data"
RESULT_DIR = ROOT_DIR / "tests_real" / "results"
os.makedirs(RESULT_DIR, exist_ok=True)

def test_knowledge_graph_basic():
    """测试知识图谱基本功能"""
    print("\n=== 测试知识图谱基本功能 ===")
    
    # 创建知识图谱
    kg = KnowledgeGraph()
    
    # 添加实体
    kg.add_entity("泰迪杯", "竞赛", {"年份": "2023"})
    kg.add_entity("中国计算机学会", "组织", {"简称": "CCF"})
    kg.add_entity("数据挖掘", "技术", {"难度": "高"})
    
    # 添加关系
    kg.add_relation("中国计算机学会", "主办", "泰迪杯")
    kg.add_relation("泰迪杯", "涉及", "数据挖掘")
    
    # 查询实体
    competition = kg.query_entity("泰迪杯")
    print(f"查询实体 '泰迪杯': {competition}")
    
    # 导出到JSON
    output_path = RESULT_DIR / "test_kg.json"
    kg.export_to_json(str(output_path))
    print(f"图谱已导出到 {output_path}")
    
    # 测试导入
    new_kg = KnowledgeGraph()
    new_kg.import_from_json(str(output_path))
    print(f"从JSON导入的图谱实体数量: {len(new_kg.get_all_entities())}")
    print(f"从JSON导入的图谱关系数量: {len(new_kg.get_all_relations())}")
    
    return kg

def test_entity_extraction():
    """测试实体提取功能"""
    print("\n=== 测试实体提取功能 ===")
    
    # 创建实体提取器
    extractor = EntityExtractor()
    
    # 测试文本
    text = """
    中国计算机学会（CCF）主办的泰迪杯数据挖掘挑战赛将于2023年4月举行。
    本次比赛由数据科学与智能计算专业委员会承办，面向全国高校学生。
    """
    
    # 提取实体
    entities = extractor.extract_entities_with_rules(text)
    print(f"提取的实体: {entities}")
    
    return entities

def test_relation_extraction():
    """测试关系提取功能"""
    print("\n=== 测试关系提取功能 ===")
    
    # 创建关系提取器
    extractor = RelationExtractor()
    
    # 添加关系模式
    extractor.add_relation_pattern("主办", ["主办", "举办"])
    extractor.add_relation_pattern("承办", ["承办"])
    extractor.add_relation_pattern("举行时间", ["将于", "举行"])
    
    # 测试文本
    text = """
    中国计算机学会（CCF）主办的泰迪杯数据挖掘挑战赛将于2023年4月举行。
    本次比赛由数据科学与智能计算专业委员会承办，面向全国高校学生。
    """
    
    # 获取实体
    entity_extractor = EntityExtractor()
    entities = entity_extractor.extract_entities_with_rules(text)
    
    # 提取关系
    relations = extractor.extract_relations(text, entities)
    print(f"提取的关系: {relations}")
    
    return relations

def test_integrated_knowledge_graph():
    """测试集成知识图谱构建流程"""
    print("\n=== 测试集成知识图谱构建流程 ===")
    
    # 创建数据处理器、实体提取器和关系提取器
    processor = DataProcessor()
    entity_extractor = EntityExtractor()
    relation_extractor = RelationExtractor()
    
    # 添加关系模式
    relation_extractor.add_relation_pattern("主办", ["主办", "举办"])
    relation_extractor.add_relation_pattern("承办", ["承办"])
    relation_extractor.add_relation_pattern("举行时间", ["将于", "举行"])
    relation_extractor.add_relation_pattern("面向", ["面向"])
    
    # 创建知识图谱
    kg = KnowledgeGraph()
    
    # 测试文本
    text = """
    中国计算机学会（CCF）主办的泰迪杯数据挖掘挑战赛将于2023年4月举行。
    本次比赛由数据科学与智能计算专业委员会承办，面向全国高校学生。
    参赛选手需要利用提供的数据集，构建智能客服机器人系统。
    """
    
    # 处理文本
    cleaned_text = processor.clean_text(text)
    
    # 提取实体
    entities = entity_extractor.extract_entities_with_rules(cleaned_text)
    
    # 添加实体到图谱
    for entity, entity_type in entities:
        kg.add_entity(entity, entity_type)
    
    # 提取关系
    relations = relation_extractor.extract_relations(cleaned_text, entities)
    
    # 添加关系到图谱
    for head, relation, tail in relations:
        kg.add_relation(head, relation, tail)
    
    # 打印结果
    print(f"图谱实体数量: {len(kg.get_all_entities())}")
    print(f"图谱关系数量: {len(kg.get_all_relations())}")
    
    # 导出到JSON
    output_path = RESULT_DIR / "integrated_kg.json"
    kg.export_to_json(str(output_path))
    print(f"集成图谱已导出到 {output_path}")
    
    return kg

if __name__ == "__main__":
    try:
        print("=== 开始知识图谱测试 ===")
        start_time = time.time()
        
        # 运行基本测试
        kg = test_knowledge_graph_basic()
        
        # 测试实体提取
        entities = test_entity_extraction()
        
        # 测试关系提取
        relations = test_relation_extraction()
        
        # 测试集成流程
        integrated_kg = test_integrated_knowledge_graph()
        
        elapsed = time.time() - start_time
        print(f"\n=== 测试完成，耗时 {elapsed:.2f} 秒 ===")
        print(f"所有测试通过!")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        traceback.print_exc()
        sys.exit(1) 