"""
问答系统集成测试
测试HybridQA与AnswerEvaluator的集成功能
"""

import sys
import os
import asyncio
from pathlib import Path
import json

# 添加项目根目录到路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

# 导入问答模块
from app.models.smart_qa_C import HybridQA
from app.models.qa_evaluator import AnswerEvaluator
from app.models.smart_qa import ask_with_evaluation

# 测试数据目录
TEST_DATA_DIR = Path(__file__).parent / "data"

def setup_test_environment():
    """设置测试环境，确保测试数据目录存在"""
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    
    # 创建测试知识库目录
    test_knowledge_dir = TEST_DATA_DIR / "knowledge"
    os.makedirs(test_knowledge_dir, exist_ok=True)
    
    # 确保样本知识文件存在，如果不存在则复制
    sample_file = TEST_DATA_DIR / "sample_knowledge.txt"
    target_file = test_knowledge_dir / "sample.txt"
    
    if sample_file.exists() and not target_file.exists():
        import shutil
        shutil.copy(sample_file, target_file)
    
    return test_knowledge_dir

def generate_dynamic_questions(qa_model, evaluator, q_model, knowledge_text, max_rounds=5):
    """
    动态生成问题并评估答案质量
    :param qa_model: 问答模型实例
    :param evaluator: 评估器实例
    :param q_model: OpenAI客户端实例
    :param knowledge_text: 知识库文本内容
    :param max_rounds: 最大测试轮次
    """
    history = []
    system_prompt = """
    你是一个严格的竞赛知识库质量评估专家，请按以下规则评估回答质量：
    问题列入:xx什么时间,xx什么地点,如何准备比赛等
    也可以出些知识库以外的问题迷惑它
    只能问一个问题
    """
    
    history.append({'role': 'system', 'content': system_prompt})
    history.append({'role': 'user', 'content': f"知识库:{knowledge_text}"})

    total_score = 0
    results = []

    for i in range(max_rounds):
        try:
            # 动态生成问题
            question = q_model.chat.completions.create(
                model="qwen-plus",
                messages=history,
            ).choices[0].message.content.strip()

            # 获取回答并评估
            response = qa_model.ask(question)
            scores = evaluator.evaluate(question, response['answer'])
            final_score = sum(scores.values()) / len(scores)
            
            results.append({
                "question": question,
                "answer": response['answer'],
                "scores": scores,
                "score": final_score
            })
            total_score += final_score
        except Exception as e:
            print(f"动态问题生成错误: {e}")
            continue

    return results, total_score/max_rounds if max_rounds > 0 else 0


def test_qa_with_evaluator():
    """测试问答引擎与答案评估器的集成"""
    
    print("=" * 50)
    print("开始测试问答引擎与答案评估器集成")
    print("=" * 50)
    
    # 设置测试环境
    test_knowledge_dir = setup_test_environment()
    print(f"使用测试知识库目录: {test_knowledge_dir}")
    
    # 初始化问答引擎和评估器
    qa = HybridQA(knowledge_dir=str(test_knowledge_dir))
    evaluator = AnswerEvaluator()
    
    # 确定是否进行动态评估测试
    dynamic_results = []
    if os.environ.get("OPENAI_API_KEY") and os.environ.get("OPENAI_BASE_URL"):
        try:
            # 仅在需要时导入OpenAI
            from openai import OpenAI
            q_model = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL")
            )
            
            # 加载知识库内容
            knowledge_file = test_knowledge_dir / "sample.txt"
            if knowledge_file.exists():
                knowledge_text = knowledge_file.read_text(encoding="utf-8")
                
                # 执行动态评估
                print("\n" + "="*50)
                print("开始动态问答评估测试")
                print("="*50)
                dynamic_results, avg_dynamic = generate_dynamic_questions(qa, evaluator, q_model, knowledge_text)
                print(f"动态测试平均得分: {avg_dynamic:.2f}")
            else:
                print("知识文件不存在，跳过动态评估")
        except Exception as e:
            print(f"动态评估初始化失败: {e}")
    else:
        print("OpenAI API配置不完整，跳过动态评估")
    
    # 执行固定问题测试
    test_questions = [
        "'未来校园'智能应用专项赛的报名时间是什么时候？",
        "机器人工程挑战赛主要考察什么？",
        "介绍一下无人机主题赛的内容。",
    ]
    fixed_results = []
    
    for question in test_questions:
        print(f"\n问题: {question}")
        
        # 获取答案
        result = qa.ask(question)
        answer = result["answer"]
        print(f"答案: {answer}")
        print(f"方法: {result['method']}, 置信度: {result['confidence']:.2f}")
        
        # 评估答案质量
        scores = evaluator.evaluate(question, answer)
        print(f"质量评分: {scores}")
        
        # 综合评分
        avg_score = sum(scores.values()) / len(scores)
        print(f"综合得分: {avg_score:.2f}")
        
        fixed_results.append({
            "question": question,
            "answer": answer,
            "scores": scores,
            "avg_score": avg_score
        })
    
    # 合并测试结果
    results = dynamic_results + fixed_results
    
    # 计算综合评分
    if results:
        total_score = sum(r.get("avg_score", r.get("score", 0)) for r in results)
        avg_total = total_score / len(results)
        print(f"综合测试平均得分: {avg_total:.2f}")
    
    # 4. 测试统一接口
    print("\n\n" + "="*50)
    print("测试统一问答接口 (ask_with_evaluation):")
    print("="*50)
    
    # 设置环境变量以使用测试知识库
    os.environ["TEST_KNOWLEDGE_DIR"] = str(test_knowledge_dir)
    
    for question in test_questions:
        print(f"\n问题: {question}")
        
        # 使用统一接口获取带评估的答案
        result = ask_with_evaluation(question)
        print(f"答案: {result['answer']}")
        print(f"质量评分: {result['quality_scores']}")
        print(f"综合得分: {result['quality_avg']:.2f}")
    
    # 输出总结
    print("\n===测试总结===")
    print(f"总测试问题数: {len(results)}")
    if results:
        avg_total = sum(r.get("avg_score", r.get("score", 0)) for r in results) / len(results)
        print(f"平均质量得分: {avg_total:.2f}")
    
    return results

# 直接运行时执行测试
if __name__ == "__main__":
    print("运行问答系统集成测试...")
    results = test_qa_with_evaluator()
    print("\n详细测试结果:")
    print(json.dumps(results, ensure_ascii=False, indent=2))