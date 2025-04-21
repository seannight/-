# 泰迪杯智能客服系统用户手册

## 快速开始

### 系统启动

泰迪杯智能客服系统提供了多种启动方式，您可以根据自己的需求选择最合适的方式：

#### 方式1：使用简易启动脚本（推荐）

```bash
# Windows PowerShell
.\scripts\run_easy.ps1

# 或者Windows批处理
.\run.bat
```

#### 方式2：使用高级启动选项

```bash
# 性能优化模式
.\scripts\run_easy.ps1 -Performance

# 指定端口并自动打开浏览器
.\scripts\run_easy.ps1 -Port 8080 -Open
```

#### 方式3：直接使用Python启动

```bash
# 快速启动模式
python -m app.main --fast

# 性能优化模式
python -m app.main --optimize
```

### 访问系统

系统启动后，可以通过以下地址访问：

- **演示界面**：http://localhost:8000/dashboard
- **API文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

## 系统功能

### 1. 智能问答

系统提供智能问答功能，可以回答关于竞赛的各种问题。问答功能支持以下特性：

- **基础信息查询**：竞赛时间、地点、组织方等基本信息
- **统计分析查询**：多个竞赛的统计信息
- **开放性问题**：与竞赛相关的其他信息
- **多轮对话**：系统能够理解上下文，进行连续的对话

**使用方式**：
1. 访问 http://localhost:8000/dashboard
2. 在问答输入框中输入您的问题
3. 点击"提交"按钮或按回车键
4. 查看系统返回的答案

### 2. 表格数据查看

系统从PDF文档中提取出结构化的表格数据，便于查看和分析。

**使用方式**：
1. 访问 http://localhost:8000/dashboard
2. 点击导航栏中的"表格数据"
3. 选择您想查看的竞赛或表格类型
4. 可以按列排序或使用搜索功能过滤数据

### 3. 系统监控

系统提供了监控功能，可以查看系统的运行状态和性能指标。

**使用方式**：
1. 访问 http://localhost:8000/health
2. 查看系统状态、组件健康情况和性能指标
3. 管理员可以通过 http://localhost:8000/monitoring/metrics 获取更详细的性能指标

## API接口说明

系统提供了RESTful API接口，可以通过编程方式集成到其他系统中。完整的API文档可以通过访问 http://localhost:8000/docs 获取。

### 核心API

#### 1. 问答API

```http
POST /api/ask
Content-Type: application/json

{
  "question": "泰迪杯的报名截止日期是什么时候?",
  "session_id": "optional-session-id",
  "context": []
}
```

**参数说明**：
- `question`：用户问题
- `session_id`：会话ID，用于多轮对话（可选）
- `context`：上下文信息，包含之前的对话历史（可选）

**返回示例**：
```json
{
  "answer": "泰迪杯的报名截止日期是2023年3月15日。",
  "confidence": 0.92,
  "source": "01_泰迪杯竞赛通知.pdf",
  "context": ["泰迪杯的报名截止日期是什么时候?"],
  "related_questions": [
    "如何报名泰迪杯?",
    "泰迪杯的比赛时间是什么时候?"
  ]
}
```

#### 2. 表格API

```http
GET /api/tables?file_id=01
```

**参数说明**：
- `file_id`：PDF文件ID（可选，不提供则返回所有表格）

**返回示例**：
```json
{
  "tables": [
    {
      "file_id": "01",
      "table_id": 1,
      "title": "比赛日程安排",
      "headers": ["阶段", "时间", "内容"],
      "data": [
        ["初赛", "2023-04-01", "线上提交材料"],
        ["复赛", "2023-04-15", "线下答辩"],
        ["决赛", "2023-04-30", "现场展示"]
      ]
    }
  ],
  "total_count": 1
}
```

#### 3. 健康检查API

```http
GET /health
```

**返回示例**：
```json
{
  "status": "healthy",
  "system": {
    "platform": "Windows 10",
    "python": "3.9.7",
    "cpu_count": 8,
    "memory_total": "16.00 GB",
    "memory_available": "8.50 GB"
  },
  "load_status": "已完成",
  "process": {
    "pid": 12345,
    "memory_usage": "0.25 GB",
    "cpu_percent": "2.1%",
    "thread_count": 8
  },
  "requests": {
    "total": 42,
    "errors": 0,
    "avg_response_time": "135.21 ms",
    "active_endpoints": 5
  },
  "timestamp": "2023-04-10T15:30:45.123456"
}
```

## 常见问题解答

### 1. 系统启动很慢怎么办？

系统首次启动需要加载模型和处理PDF文件，可能会较慢。您可以：

- 使用快速启动模式：`.\scripts\run_easy.ps1 -Performance`
- 确保您的系统有足够的内存（建议至少4GB可用内存）
- 如果只需要演示界面，可以在启动命令中添加`-ui-priority`参数

### 2. 问答系统无法回答我的问题怎么办？

- 尝试使用更简单、更明确的问法
- 确保您的问题与比赛相关
- 检查问题中是否有错别字或不完整的语句
- 尝试多轮对话，通过上下文补充信息

### 3. 表格数据不完整或有错误怎么办？

- 检查原始PDF文件，确认表格在PDF中的显示是否正确
- 系统可能无法处理某些复杂的表格结构，可以在问题中描述您需要的具体信息
- 联系管理员处理特定的数据问题

### 4. 如何扩展系统支持更多PDF文件？

1. 将新的PDF文件放置在`data/`目录下
2. 重新启动系统，系统会自动处理新增的PDF文件
3. 如果需要立即生效，可以访问`/api/refresh`接口

## 性能优化建议

如果系统运行缓慢，您可以尝试以下优化方法：

1. **启用性能优化模式**：使用`-Performance`参数启动
2. **调整工作进程数**：默认根据CPU核心数自动设置，您也可以手动设置环境变量`WORKER_COUNT`
3. **预热系统**：在使用前运行`python scripts/preload.py`预热系统
4. **清理缓存**：如果长时间运行，可以调用`/monitoring/reset`接口重置缓存
5. **关闭不必要功能**：如果只需要特定功能，可以修改配置文件禁用其他模块

## 联系与支持

如果您遇到任何问题或需要进一步的帮助，请联系系统管理员或开发团队。

- **团队邮箱**：team@example.com
- **问题反馈**：在GitHub仓库提交Issue
- **文档更新**：最后更新日期 2023-04-10 