# 泰迪杯智能客服系统

## 项目概述
基于FastAPI的智能问答和表格处理系统，支持PDF文档解析、表格提取、智能问答和会话管理功能。

## 主要功能
1. PDF文档解析与表格提取
2. 智能问答引擎
3. 答案质量评估系统
4. 多轮对话与会话管理（新增）

## 技术栈
- 后端：FastAPI + Uvicorn
- 数据处理：PyPDF2、pdfplumber、正则表达式
- 问答系统：TF-IDF + Sentence-BERT
- 储存：文件系统（JSON）

## 表格提取功能
表格提取模块是系统的核心组件之一，提供从PDF文档中提取表格的能力。

### 使用extract_tables函数
`extract_tables`是系统提供的主要表格提取函数，使用方法如下：

```python
# 导入方式
from app.data_processing import extract_tables

# 使用示例
pdf_path = "path/to/your/document.pdf"
tables = extract_tables(pdf_path)

# 处理提取的表格
for i, table in enumerate(tables):
    print(f"表格 {i+1} - 页码: {table.get('page', 'N/A')}")
    data = table.get('data', [])
    if data:
        print(f"表头: {data[0]}")
        print(f"行数: {len(data)-1}")
```

### 表格数据结构
提取的表格数据结构如下：
```python
{
    "page": 1,               # 表格所在页码
    "table_num": 1,          # 页面内表格序号
    "data": [                # 表格数据（二维数组）
        ["表头1", "表头2", "表头3"],  # 第一行通常是表头
        ["数据1", "数据2", "数据3"],  # 数据行
        # ...更多行
    ],
    "organizations": ["组织1", "组织2"],  # 可能包含的组织信息
    "excel_path": "path/to/exported.xlsx"  # 导出的Excel文件路径
}
```

### 高级用法
对于需要更精细控制的场景，可以直接使用`TableExtractor`类：

```python
from app.data_processing import TableExtractor

# 创建提取器实例
extractor = TableExtractor(
    input_dir="data/raw",
    output_dir="data/processed/excel_tables"
)

# 提取表格
tables = extractor.extract_tables("path/to/your/document.pdf")

# 导出到Excel（extract_tables已自动执行此步骤）
output_path = "path/to/output.xlsx"
extractor._export_to_excel(tables, output_path)
```

## 会话管理功能（新增）
会话管理模块提供创建、存储、检索和管理会话的功能，支持多轮对话历史记录。

### 主要特性
- 创建和管理用户会话
- 储存对话历史
- 支持会话上下文的智能问答
- 会话统计数据

### API接口
- `POST /api/sessions` - 创建新会话
- `GET /api/sessions` - 获取会话列表
- `GET /api/sessions/{session_id}` - 获取会话详情
- `DELETE /api/sessions/{session_id}` - 删除会话
- `POST /api/sessions/{session_id}/messages` - 添加会话消息
- `GET /api/sessions/{session_id}/messages` - 获取会话消息列表
- `GET /api/statistics` - 获取会话统计信息

### 与问答系统集成
问答API已支持会话功能，使用方法：
```python
# 发送具有会话ID的问题
response = requests.post("http://localhost:53085/api/ask", json={
    "text": "未来校园智能应用专项赛的报名时间是什么时候？",
    "session_id": "your_session_id"  # 提供会话ID自动记录历史
})

# 发送后续问题（自动利用会话历史）
response = requests.post("http://localhost:53085/api/ask", json={
    "text": "这个比赛的主题是什么？",  # 可使用代词，系统会理解上下文
    "session_id": "your_session_id"
})
```

## 网络连接管理
系统设计了完善的网络连接管理机制，支持离线模式和连接问题诊断。

### 主要特性
- 自动检测网络状态变化并适应连接环境
- 在网络不可用时自动切换到离线模式
- 网络恢复时自动重新连接和同步
- 提供诊断和修复工具解决连接问题

### 离线模式
当系统无法连接到服务器时，会自动切换到离线模式，提供基本问答功能：
- 基础智能问答（基于预先加载的常见问题库）
- 本地会话管理（数据将在网络恢复后同步）
- 热门问题和推荐功能

### 连接诊断工具
系统提供了内置的连接诊断工具，用于解决网络连接问题：
- 检测网络连接、VPN状态和API可达性
- 提供自动修复功能
- 支持手动配置API连接参数

详细使用方法请参考[网络连接指南](./docs/network-connection-guide.md)。

## API端口配置方法
系统支持自定义API端口配置，便于前后端分离部署或在不同环境中运行：

### 后端端口配置
1. 通过命令行参数指定端口（优先级最高）：
   ```bash
   # 指定端口为53085（PowerShell语法）
   python -m app.main --port 53085
   ```

2. 通过环境变量配置（优先级中）：
   ```bash
   # Windows PowerShell
   $env:API_PORT=53085; python -m app.main
   
   # Linux/macOS
   API_PORT=53085 python -m app.main
   ```

3. 通过配置文件配置（优先级低）：
   编辑项目根目录下的`teddy_config.txt`文件：
   ```
   API_PORT=53085
   API_HOST=127.0.0.1
   ```

### 前端连接配置
前端页面通过`api-config.js`自动连接到后端API：

1. 所有页面需引入配置脚本：
   ```html
   <script src="/static/js/api-config.js"></script>
   ```

2. 使用配置的API地址进行请求：
   ```javascript
   // 等待配置加载完成
   document.addEventListener('api-config-loaded', function(e) {
     // 发起API请求
     fetch(getApiUrl('/qa/answer'), {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ text: "泰迪杯是什么比赛?" })
     })
     .then(response => response.json())
     .then(data => console.log(data));
   });
   ```

3. 或者直接检查配置是否加载：
   ```javascript
   if (window.API_CONFIG) {
     // API配置已加载，可以直接使用
     fetch(getApiUrl('/qa/answer'), { /*...*/ });
   } else {
     // 等待配置加载完成
     document.addEventListener('api-config-loaded', function() {
       fetch(getApiUrl('/qa/answer'), { /*...*/ });
     });
   }
   ```
## 智能推荐与用户反馈系统
系统提供智能问题推荐和用户反馈收集功能，支持个性化推荐和系统使用情况分析。

### 主要特性
- 基于用户历史行为和知识图谱的混合推荐策略
- 支持热门问题推荐、相关问题推荐和个性化推荐
- 用户反馈收集与分析
- 用户画像和系统使用情况统计

### API接口
- `POST /api/feedback/submit` - 提交用户反馈
- `POST /api/feedback/recommend` - 获取智能推荐问题
- `POST /api/feedback/user-profile` - 获取用户画像
- `GET /api/feedback/system-stats` - 获取系统使用情况统计
- `GET /api/feedback/hot-questions` - 获取热门问题

### 使用示例
```javascript
// 获取推荐问题
fetch('/api/feedback/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    question: "泰迪杯报名时间是什么时候?",
    user_id: "user123"
  })
})
.then(response => response.json())
.then(data => console.log(data.recommended_questions));

// 提交反馈
fetch('/api/feedback/submit', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    question_id: "q123",
    answer_id: "a456",
    rating: "helpful", // helpful 或 not_helpful
    user_id: "user123"
  })
})
.then(response => response.json())
.then(data => console.log(data.status));
```

## 系统监控与性能统计
系统提供实时监控和性能统计功能，帮助管理员了解系统运行状态。

### 监控接口
- `GET /health` - 系统健康检查
- `GET /monitoring/metrics` - 获取系统性能指标
- `
