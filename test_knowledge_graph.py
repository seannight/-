"""
知识图谱测试模块

测试知识图谱构建、实体提取和图谱查询功能
作为C成员第五周任务的测试支持

作者: A成员
创建日期: 2025-04-14
更新日期: 2025-04-14
"""

import os
import sys
import json
import pytest
import logging
import datetime
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入测试目标
from app.models.knowledge_graph import KnowledgeGraph
from app.models.entity_extractor import EntityExtractor

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("knowledge_graph_test")

# 测试数据路径
TEST_DIR = Path(__file__).parent
TEST_DATA_DIR = TEST_DIR / "knowledge" / "graph_test"
RESULTS_DIR = TEST_DIR / "results" / "knowledge_graph"

# 确保结果目录存在
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def setup_module(module):
    """模块初始化"""
    logger.info("初始化知识图谱测试模块")
    
    # 确保测试数据目录存在
    if not TEST_DATA_DIR.exists():
        TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 创建测试文件
    create_test_files()

def create_test_files():
    """创建测试文件"""
    # 测试文件1
    test_file1 = TEST_DATA_DIR / "competition1.txt"
    if not test_file1.exists():
        with open(test_file1, "w", encoding="utf-8") as f:
            f.write("""
            2024年（第12届）"泰迪杯"数据挖掘挑战赛将于2024年4月28日正式启动。
            本次竞赛由泰迪科技主办，中国人工智能学会协办，地点位于北京市海淀区。
            参赛对象：全国高校大学生、研究生均可参赛。
            """)
    
    # 测试文件2
    test_file2 = TEST_DATA_DIR / "competition2.txt"
    if not test_file2.exists():
        with open(test_file2, "w", encoding="utf-8") as f:
            f.write("""
            人工智能综合创新专项赛将于2024年5月15日在上海市举行。
            由中国人工智能学会主办，上海交通大学协办。
            本次比赛主题为人工智能应用创新，欢迎各高校学生参与。
            """)

class TestEntityExtractor:
    """实体提取器测试类"""
    
    def setup_method(self):
        """每个测试方法前运行"""
        self.extractor = EntityExtractor()
    
    def test_extract_entities(self):
        """测试实体提取功能"""
        # 读取测试文件
        with open(TEST_DATA_DIR / "competition1.txt", "r", encoding="utf-8") as f:
            text = f.read()
        
        # 提取实体
        entities = self.extractor.extract_entities(text)
        
        # 验证结果
        assert "competition" in entities, "应提取出竞赛实体"
        assert any("泰迪杯" in c for c in entities["competition"]), "应提取出'泰迪杯'竞赛"
        assert "time" in entities, "应提取出时间实体"
        assert "organization" in entities, "应提取出组织实体"
        assert "location" in entities, "应提取出地点实体"
        
        # 保存结果
        result = {
            "test": "extract_entities",
            "input": text[:100] + "...",  # 截断输入文本
            "entities": entities,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        with open(RESULTS_DIR / "entity_extraction_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"实体提取结果: {entities}")
    
    def test_extract_relations(self):
        """测试关系提取功能"""
        # 读取测试文件
        with open(TEST_DATA_DIR / "competition1.txt", "r", encoding="utf-8") as f:
            text = f.read()
        
        # 提取实体
        entities = self.extractor.extract_entities(text)
        
        # 提取关系
        relations = self.extractor.extract_relations(text, entities)
        
        # 验证结果
        assert len(relations) > 0, "应提取出至少一个关系"
        
        # 检查具体关系类型
        relation_types = [r[1] for r in relations]
        assert "举办时间" in relation_types or "主办方" in relation_types or "举办地点" in relation_types, "应提取出至少一种关系类型"
        
        # 保存结果
        result = {
            "test": "extract_relations",
            "input": text[:100] + "...",  # 截断输入文本
            "entities": entities,
            "relations": [(s, r, t) for s, r, t in relations],  # 转换为可序列化格式
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        with open(RESULTS_DIR / "relation_extraction_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"关系提取结果: {relations}")
    
    def test_process_text(self):
        """测试文本处理功能"""
        # 读取测试文件
        with open(TEST_DATA_DIR / "competition2.txt", "r", encoding="utf-8") as f:
            text = f.read()
        
        # 处理文本
        result = self.extractor.process_text(text)
        
        # 验证结果
        assert "entities" in result, "结果应包含实体"
        assert "relations" in result, "结果应包含关系"
        
        # 保存结果
        result_with_meta = {
            "test": "process_text",
            "input": text[:100] + "...",  # 截断输入文本
            "result": {
                "entities": result["entities"],
                "relations": [(s, r, t) for s, r, t in result["relations"]]  # 转换为可序列化格式
            },
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        with open(RESULTS_DIR / "text_processing_result.json", "w", encoding="utf-8") as f:
            json.dump(result_with_meta, f, ensure_ascii=False, indent=2)
        
        logger.info(f"文本处理结果: {result}")
    
    def test_extract_competition_info(self):
        """测试竞赛信息提取功能"""
        # 读取测试文件
        with open(TEST_DATA_DIR / "competition2.txt", "r", encoding="utf-8") as f:
            text = f.read()
        
        # 提取竞赛信息
        competition_info = self.extractor.extract_competition_info(text)
        
        # 验证结果
        assert "名称" in competition_info, "结果应包含竞赛名称"
        assert competition_info["名称"], "竞赛名称不应为空"
        
        # 保存结果
        result = {
            "test": "extract_competition_info",
            "input": text[:100] + "...",  # 截断输入文本
            "competition_info": competition_info,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        with open(RESULTS_DIR / "competition_info_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"竞赛信息提取结果: {competition_info}")

class TestKnowledgeGraph:
    """知识图谱测试类"""
    
    def setup_method(self):
        """每个测试方法前运行"""
        self.kg = KnowledgeGraph(knowledge_dir=str(TEST_DATA_DIR))
    
    def test_load_knowledge(self):
        """测试加载知识功能"""
        # 加载知识
        self.kg.load_knowledge()
        
        # 验证结果
        assert len(self.kg.entities) > 0, "应加载至少一个实体"
        assert len(self.kg.graph.nodes()) > 0, "图谱应包含至少一个节点"
        
        # 保存结果
        result = {
            "test": "load_knowledge",
            "entity_count": len(self.kg.entities),
            "node_count": len(self.kg.graph.nodes()),
            "edge_count": len(self.kg.graph.edges()),
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        with open(RESULTS_DIR / "knowledge_loading_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"知识加载结果: 实体数={len(self.kg.entities)}, 节点数={len(self.kg.graph.nodes())}, 边数={len(self.kg.graph.edges())}")
    
    def test_add_entity_and_relation(self):
        """测试添加实体和关系功能"""
        # 添加实体
        self.kg.add_entity("测试竞赛", "competition")
        self.kg.add_entity("2024年6月1日", "time")
        
        # 添加关系
        self.kg.add_relation("测试竞赛", "举办时间", "2024年6月1日")
        
        # 验证结果
        assert "测试竞赛" in self.kg.entities, "应成功添加实体"
        assert "2024年6月1日" in self.kg.entities, "应成功添加实体"
        assert self.kg.graph.has_edge("测试竞赛", "2024年6月1日"), "应成功添加关系"
        
        # 查询实体
        entity_info = self.kg.query_entity("测试竞赛")
        
        # 验证查询结果
        assert entity_info["exists"], "应能查询到实体"
        assert entity_info["type"] == "competition", "实体类型应正确"
        assert len(entity_info["relations"]) > 0, "应有关系信息"
        
        # 保存结果
        result = {
            "test": "add_entity_and_relation",
            "entity_info": entity_info,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        with open(RESULTS_DIR / "entity_relation_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"实体与关系测试结果: {entity_info}")
    
    def test_answer_graph_question(self):
        """测试图谱问答功能"""
        # 添加测试数据
        self.kg.add_entity("泰迪杯数据挖掘挑战赛", "competition")
        self.kg.add_entity("2024年4月28日", "time")
        self.kg.add_relation("泰迪杯数据挖掘挑战赛", "举办时间", "2024年4月28日")
        
        # 提问
        question = "泰迪杯的举办时间是什么？"
        answer = self.kg.answer_graph_question(question)
        
        # 验证结果
        assert "answer" in answer, "应返回答案"
        assert answer["confidence"] > 0.5, "置信度应大于0.5"
        assert "2024年4月28日" in answer["answer"], "答案应包含正确时间"
        
        # 保存结果
        result = {
            "test": "answer_graph_question",
            "question": question,
            "answer": answer,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        with open(RESULTS_DIR / "graph_qa_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"图谱问答结果: 问题='{question}', 答案={answer}")
    
    def test_save_and_load_graph(self):
        """测试图谱保存和加载功能"""
        # 添加测试数据
        self.kg.add_entity("人工智能综合创新专项赛", "competition")
        self.kg.add_entity("2024年5月15日", "time")
        self.kg.add_entity("上海市", "location")
        self.kg.add_relation("人工智能综合创新专项赛", "举办时间", "2024年5月15日")
        self.kg.add_relation("人工智能综合创新专项赛", "举办地点", "上海市")
        
        # 保存图谱
        save_path = RESULTS_DIR / "test_graph.json"
        self.kg.save_graph(str(save_path))
        
        # 创建新实例
        new_kg = KnowledgeGraph()
        
        # 加载图谱
        new_kg.load_graph(str(save_path))
        
        # 验证结果
        assert len(new_kg.entities) == len(self.kg.entities), "实体数应相同"
        assert len(new_kg.graph.nodes()) == len(self.kg.graph.nodes()), "节点数应相同"
        assert len(new_kg.graph.edges()) == len(self.kg.graph.edges()), "边数应相同"
        
        # 保存结果
        result = {
            "test": "save_and_load_graph",
            "original_entities": len(self.kg.entities),
            "loaded_entities": len(new_kg.entities),
            "original_edges": len(self.kg.graph.edges()),
            "loaded_edges": len(new_kg.graph.edges()),
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        with open(RESULTS_DIR / "graph_save_load_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"图谱保存加载结果: 原实体数={len(self.kg.entities)}, 加载后实体数={len(new_kg.entities)}")
    
    def test_get_visualization_data(self):
        """测试获取可视化数据功能"""
        # 加载测试数据
        self.kg.add_entity("泰迪杯数据挖掘挑战赛", "competition")
        self.kg.add_entity("2024年4月28日", "time")
        self.kg.add_entity("泰迪科技", "organization")
        self.kg.add_entity("北京市海淀区", "location")
        
        self.kg.add_relation("泰迪杯数据挖掘挑战赛", "举办时间", "2024年4月28日")
        self.kg.add_relation("泰迪杯数据挖掘挑战赛", "主办方", "泰迪科技")
        self.kg.add_relation("泰迪杯数据挖掘挑战赛", "举办地点", "北京市海淀区")
        
        # 获取可视化数据
        viz_data = self.kg.get_visualization_data()
        
        # 验证结果
        assert "nodes" in viz_data, "应返回节点数据"
        assert "edges" in viz_data, "应返回边数据"
        assert len(viz_data["nodes"]) >= 4, "应有至少4个节点"
        assert len(viz_data["edges"]) >= 3, "应有至少3条边"
        
        # 保存结果
        result = {
            "test": "get_visualization_data",
            "viz_data": viz_data,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        with open(RESULTS_DIR / "visualization_data_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"可视化数据结果: 节点数={len(viz_data['nodes'])}, 边数={len(viz_data['edges'])}")

def run_tests():
    """运行所有测试"""
    # 设置环境变量以区分测试环境
    os.environ["KNOWLEDGE_GRAPH_TEST_MODE"] = "True"
    
    # 运行测试
    pytest.main(["-xvs", __file__])

if __name__ == "__main__":
    run_tests() 