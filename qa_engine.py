# 泰迪杯项目 - 关键词问答引擎
# 负责人: C成员
# 功能: 基于关键词匹配的问答系统
# 更新日期: 2025-03-20

import os
import jieba
import json
import re

class KeywordQA:
    def __init__(self, knowledge_dir="data/processed"):
        """初始化问答引擎
        
        Args:
            knowledge_dir (str): 知识文件所在目录
        """
        # 知识库字典，结构: {关键词: [文本段落列表]}
        self.knowledge_base = {}
        
        # 同义词词典，结构: {词: 标准词}
        self.synonyms = {
            "时间": ["日期", "何时", "时候", "几号", "几点"],
            "地点": ["位置", "哪里", "何处", "在哪", "地址"],
            "规则": ["规定", "要求", "标准", "条例", "办法"],
            "奖项": ["奖励", "奖金", "获奖", "荣誉"],
            "组别": ["分组", "类别", "种类", "分类"],
            "报名": ["申请", "登记", "注册", "参赛"]
        }
        
        # 反向同义词表，用于查询
        self.reverse_synonyms = {}
        for std_word, syn_list in self.synonyms.items():
            for word in syn_list:
                self.reverse_synonyms[word] = std_word
        
        # 加载知识库
        self.load_knowledge(knowledge_dir)
        
    def load_knowledge(self, directory):
        """从文本文件加载知识
        
        Args:
            directory (str): 知识文件所在目录
        """
        # 检查目录是否存在
        if not os.path.exists(directory):
            print(f"警告: 知识目录 {directory} 不存在")
            return
        
        # 遍历目录中的文本文件
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 按段落拆分
                    paragraphs = content.split('\n\n')
                    for para in paragraphs:
                        para = para.strip()
                        if para:
                            # 提取段落关键词
                            keywords = self.extract_keywords(para)
                            
                            # 将段落按关键词索引存入知识库
                            for keyword in keywords:
                                if keyword not in self.knowledge_base:
                                    self.knowledge_base[keyword] = []
                                # 避免重复添加相同段落
                                if para not in self.knowledge_base[keyword]:
                                    self.knowledge_base[keyword].append(para)
                    
                    print(f"已加载知识文件: {filename}")
                except Exception as e:
                    print(f"加载文件 {filename} 时出错: {e}")
        
        # 打印知识库统计信息
        keyword_count = len(self.knowledge_base)
        paragraph_count = sum(len(paras) for paras in self.knowledge_base.values())
        print(f"知识库加载完成，包含 {keyword_count} 个关键词，{paragraph_count} 个知识段落")
    
    def extract_keywords(self, text):
        """提取文本中的关键词
        
        Args:
            text (str): 输入文本
            
        Returns:
            list: 关键词列表
        """
        # 使用jieba分词
        words = list(jieba.cut(text))
        
        # 过滤掉停用词和短词
        filtered_words = []
        stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        
        for word in words:
            # 如果词在同义词表中，替换为标准词
            if word in self.reverse_synonyms:
                word = self.reverse_synonyms[word]
            
            if len(word) > 1 and word not in stopwords:
                filtered_words.append(word)
        
        return filtered_words
    
    def search(self, query, top_k=5):
        """搜索与查询相关的内容
        
        Args:
            query (str): 查询内容
            top_k (int): 返回结果数量上限
            
        Returns:
            list: 相关段落列表
        """
        # 提取查询中的关键词
        keywords = self.extract_keywords(query)
        
        # 匹配结果与权重
        results = {}
        
        # 对每个关键词在知识库中查找匹配段落
        for keyword in keywords:
            if keyword in self.knowledge_base:
                for para in self.knowledge_base[keyword]:
                    # 如果段落已在结果中，增加权重；否则添加新结果
                    if para in results:
                        results[para] += 1
                    else:
                        results[para] = 1
        
        # 按权重排序
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        
        # 返回top_k个结果
        return [para for para, weight in sorted_results[:top_k]]
    
    def answer(self, question):
        """回答问题
        
        Args:
            question (str): 用户问题
            
        Returns:
            dict: 包含问题和答案的字典
        """
        # 搜索相关段落
        results = self.search(question)
        
        # 构建回答
        if results:
            return {
                "question": question,
                "answer_count": len(results),
                "answers": results
            }
        else:
            return {
                "question": question,
                "answer_count": 0,
                "answers": ["抱歉，没有找到相关信息"]
            }
    
    def save_knowledge_base(self, filepath="data/knowledge_base.json"):
        """保存知识库到文件
        
        Args:
            filepath (str): 保存路径
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            print(f"知识库已保存到: {filepath}")
        except Exception as e:
            print(f"保存知识库时出错: {e}")
    
    def load_knowledge_base(self, filepath="data/knowledge_base.json"):
        """从文件加载知识库
        
        Args:
            filepath (str): 加载路径
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            print(f"已从 {filepath} 加载知识库")
        except Exception as e:
            print(f"加载知识库时出错: {e}")

# 当直接运行脚本时，进行简单测试
if __name__ == "__main__":
    print("泰迪杯关键词问答引擎")
    print("===================")
    
    # 初始化问答引擎
    qa = KeywordQA()
    
    # 简单测试
    test_questions = [
        "泰迪杯比赛的时间是什么时候？",
        "比赛地点在哪里？",
        "参赛有哪些要求？",
        "如何报名参加比赛？"
    ]
    
    # 测试问答功能
    print("\n测试问答功能:")
    for question in test_questions:
        result = qa.answer(question)
        print(f"\n问题: {question}")
        print(f"找到 {result['answer_count']} 个相关回答:")
        for i, answer in enumerate(result['answers']):
            print(f"{i+1}. {answer[:100]}{'...' if len(answer) > 100 else ''}")
    
    # 保存知识库示例
    # qa.save_knowledge_base() 