"""
A角色用于测试C成员第三周任务,C成员智能问答引擎专项测试

验证HybridQA的核心功能，包括:
1. 知识库加载与文本分块
2. TF-IDF向量检索与余弦相似度计算
3. 规则匹配与预置回答
4. 多轮对话上下文管理
5. 优雅降级机制
6. 后续问题推荐
"""

import os
import sys
import logging
import time
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("qa_test")

def test_qa_engine():
    """测试智能问答引擎"""
    logger.info("===== 开始智能问答引擎专项测试 =====")
    
    # 导入问答引擎
    try:
        from app.models.smart_qa import HybridQA
        logger.info("成功导入HybridQA")
    except ImportError as e:
        logger.error(f"导入HybridQA失败: {e}")
        return False
    
    # 测试知识库目录
    knowledge_dirs = [
        "data/processed/excel_tables",
        "data/processed", 
        "."
    ]
    
    # 尝试不同知识库目录
    for knowledge_dir in knowledge_dirs:
        if not os.path.exists(knowledge_dir):
            logger.warning(f"知识库目录不存在: {knowledge_dir}")
            continue
            
        logger.info(f"尝试使用知识库目录: {knowledge_dir}")
        
        # 初始化问答引擎
        try:
            # 测试优雅降级 - 不使用API
            qa = HybridQA(knowledge_dir=knowledge_dir, use_api=False)
            
            # 检查知识库是否加载成功
            if not qa.documents:
                logger.warning(f"知识库加载失败，文档列表为空: {knowledge_dir}")
                continue
                
            logger.info(f"成功加载知识库，文档块数量: {len(qa.documents)}")
            
            # 测试问题列表
            test_questions = [
                "泰迪杯比赛有什么要求？",
                "数据挖掘赛题的评分标准是什么？",
                "报名流程是怎样的？",
                "什么是TF-IDF算法？"
            ]
            
            # 进行问答测试
            for question in test_questions:
                logger.info(f"测试问题: {question}")
                
                start_time = time.time()
                result = qa.ask(question)
                elapsed = time.time() - start_time
                
                # 检查结果格式
                if not isinstance(result, dict) or "answer" not in result:
                    logger.error(f"问答结果格式错误: {result}")
                    continue
                    
                # 打印结果
                logger.info(f"回答: {result['answer'][:100]}...")
                logger.info(f"方法: {result.get('method', 'unknown')}")
                logger.info(f"置信度: {result.get('confidence', 0)}")
                logger.info(f"处理时间: {elapsed:.4f}秒")
                
                if "followup_suggestions" in result:
                    logger.info(f"后续问题建议: {', '.join(result['followup_suggestions'][:3])}")
                
                logger.info("-" * 50)
            
            # 测试多轮对话
            logger.info("测试多轮对话能力...")
            conversation = [
                {"question": "泰迪杯是什么比赛？", "answer": "泰迪杯是全国性数据分析技能竞赛，面向高校学生。"}
            ]
            follow_up_question = "有哪些参赛组别？"
            result_with_history = qa.ask(follow_up_question, history=conversation)
            logger.info(f"多轮对话问题: {follow_up_question}")
            logger.info(f"多轮对话回答: {result_with_history['answer'][:100]}...")
            logger.info(f"方法: {result_with_history.get('method', 'unknown')}")
            
            # 测试规则匹配
            logger.info("测试规则匹配能力...")
            rule_based_question = "你好，请介绍一下你自己"
            rule_result = qa.ask(rule_based_question)
            logger.info(f"规则匹配问题: {rule_based_question}")
            logger.info(f"规则匹配回答: {rule_result['answer']}")
            logger.info(f"方法: {rule_result.get('method', 'unknown')}")
            
            # 测试后续问题推荐
            logger.info("测试后续问题推荐功能...")
            if "followup_suggestions" in result and len(result["followup_suggestions"]) > 0:
                logger.info(f"推荐问题数量: {len(result['followup_suggestions'])}")
                logger.info(f"推荐问题示例: {result['followup_suggestions'][0]}")
                logger.info("后续问题推荐功能正常")
            else:
                logger.warning("后续问题推荐功能异常，未生成推荐问题")
            
            # 获取统计信息
            stats = qa.get_stats()
            logger.info(f"引擎统计信息: {stats}")
            
            # 测试成功
            logger.info("问答引擎测试成功!")
            return True
            
        except Exception as e:
            logger.error(f"初始化或测试问答引擎时出错: {e}", exc_info=True)
    
    logger.error("所有知识库目录尝试均失败")
    return False

if __name__ == "__main__":
    test_qa_engine() 