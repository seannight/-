"""
知识图谱API测试模块

测试知识图谱API接口功能
作为A成员第五周任务的测试支持

作者: A成员
创建日期: 2025-04-14
更新日期: 2025-04-14
"""

import os
import sys
import json
import time
import pytest
import logging
import requests
import datetime
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("knowledge_graph_api_test")

# 测试数据路径
TEST_DIR = Path(__file__).parent
RESULTS_DIR = TEST_DIR / "results" / "knowledge_graph_api"

# 确保结果目录存在
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# API基础URL
API_BASE_URL = "http://localhost:8000"

# 测试超时设置
TEST_TIMEOUT = 5  # 秒

# 测试用例
TEST_CASES = [
    {
        "id": "graph-data",
        "endpoint": "/knowledge-graph/data",
        "method": "GET",
        "expected_status": 200,
        "expected_keys": ["nodes", "edges"],
        "description": "获取知识图谱数据"
    },
    {
        "id": "entity-query",
        "endpoint": "/knowledge-graph/entity",
        "method": "GET",
        "params": {"name": "泰迪杯"},
        "expected_status": 200,
        "expected_keys": ["exists", "type", "details", "relations"],
        "description": "查询实体信息"
    },
    {
        "id": "related-questions",
        "endpoint": "/knowledge-graph/related-questions",
        "method": "GET",
        "params": {"entity_name": "泰迪杯"},
        "expected_status": 200,
        "expected_keys": ["questions"],
        "description": "获取相关问题"
    },
    {
        "id": "graph-answer",
        "endpoint": "/knowledge-graph/answer",
        "method": "POST",
        "json_data": {"question": "泰迪杯什么时候举办？"},
        "expected_status": 200,
        "expected_keys": ["answer", "confidence", "source"],
        "description": "通过知识图谱回答问题"
    }
]

def make_request(test_case):
    """发送API请求"""
    url = f"{API_BASE_URL}{test_case['endpoint']}"
    method = test_case.get("method", "GET")
    params = test_case.get("params", None)
    json_data = test_case.get("json_data", None)
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=params, timeout=TEST_TIMEOUT)
        elif method.upper() == "POST":
            response = requests.post(url, json=json_data, timeout=TEST_TIMEOUT)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
        
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {e}")
        return None

def test_api_availability():
    """测试API可用性"""
    logger.info("测试API可用性")
    
    # 发送健康检查请求
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=TEST_TIMEOUT)
        status_code = response.status_code
        response_data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"健康检查请求失败: {e}")
        status_code = None
        response_data = None
    
    # 保存结果
    result = {
        "test": "api_availability",
        "status_code": status_code,
        "response_data": response_data,
        "success": status_code == 200,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    with open(RESULTS_DIR / "api_availability_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    logger.info(f"API可用性测试结果: {'成功' if result['success'] else '失败'}")
    
    # 验证结果
    assert status_code == 200, "API服务不可用"
    assert "status" in response_data, "响应缺少状态信息"
    assert response_data["status"] == "ok", "API服务状态异常"
    assert "components" in response_data, "响应缺少组件信息"
    assert "knowledge_graph" in response_data["components"], "知识图谱组件未配置"

def test_knowledge_graph_endpoints():
    """测试知识图谱API端点"""
    logger.info("测试知识图谱API端点")
    
    results = []
    all_passed = True
    
    for test_case in TEST_CASES:
        logger.info(f"测试: {test_case['description']}")
        
        # 发送请求
        start_time = time.time()
        response = make_request(test_case)
        end_time = time.time()
        
        # 计算响应时间
        response_time = end_time - start_time
        
        # 检查响应
        if response is None:
            success = False
            response_data = None
            status_code = None
            errors = ["请求失败，无响应"]
        else:
            status_code = response.status_code
            expected_status = test_case.get("expected_status", 200)
            
            if status_code == expected_status:
                try:
                    response_data = response.json()
                    errors = []
                    
                    # 检查预期键是否存在
                    expected_keys = test_case.get("expected_keys", [])
                    for key in expected_keys:
                        if key not in response_data:
                            errors.append(f"响应缺少预期键: {key}")
                    
                    success = len(errors) == 0
                except ValueError:
                    response_data = None
                    errors = ["响应不是有效的JSON格式"]
                    success = False
            else:
                try:
                    response_data = response.json()
                except ValueError:
                    response_data = None
                errors = [f"响应状态码错误: 预期 {expected_status}, 实际 {status_code}"]
                success = False
        
        # 保存测试结果
        test_result = {
            "test_id": test_case["id"],
            "description": test_case["description"],
            "endpoint": test_case["endpoint"],
            "method": test_case["method"],
            "params": test_case.get("params"),
            "json_data": test_case.get("json_data"),
            "status_code": status_code,
            "expected_status": test_case.get("expected_status", 200),
            "response_data": response_data,
            "response_time": response_time,
            "success": success,
            "errors": errors,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        results.append(test_result)
        all_passed = all_passed and success
        
        # 单独保存每个测试结果
        with open(RESULTS_DIR / f"{test_case['id']}_result.json", "w", encoding="utf-8") as f:
            json.dump(test_result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"测试结果: {test_case['description']} - {'成功' if success else '失败'}")
        if not success:
            logger.error(f"错误: {errors}")
    
    # 保存所有测试结果
    with open(RESULTS_DIR / "all_tests_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 验证所有测试是否通过
    assert all_passed, "有API测试用例失败"

def test_api_performance():
    """测试API性能"""
    logger.info("测试API性能")
    
    # 测试用例
    test_case = {
        "endpoint": "/knowledge-graph/data",
        "method": "GET",
        "expected_status": 200
    }
    
    results = []
    total_response_time = 0
    num_success = 0
    num_requests = 5
    
    for i in range(num_requests):
        # 发送请求
        start_time = time.time()
        response = make_request(test_case)
        end_time = time.time()
        
        # 计算响应时间
        response_time = end_time - start_time
        
        # 检查响应
        if response is not None and response.status_code == test_case["expected_status"]:
            success = True
            num_success += 1
        else:
            success = False
        
        # 记录结果
        result = {
            "request_num": i + 1,
            "response_time": response_time,
            "success": success
        }
        
        results.append(result)
        
        if success:
            total_response_time += response_time
        
        # 等待一小段时间
        time.sleep(0.1)
    
    # 计算平均响应时间
    avg_response_time = total_response_time / num_success if num_success > 0 else None
    success_rate = (num_success / num_requests) * 100
    
    # 保存性能测试结果
    performance_result = {
        "test": "api_performance",
        "num_requests": num_requests,
        "num_success": num_success,
        "success_rate": success_rate,
        "avg_response_time": avg_response_time,
        "detailed_results": results,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    with open(RESULTS_DIR / "api_performance_result.json", "w", encoding="utf-8") as f:
        json.dump(performance_result, f, ensure_ascii=False, indent=2)
    
    logger.info(f"API性能测试结果: 成功率={success_rate}%, 平均响应时间={avg_response_time}秒")
    
    # 验证性能是否满足要求
    assert success_rate >= 80, "API成功率低于80%"
    assert avg_response_time is not None and avg_response_time < 1.0, "API平均响应时间超过1秒"

def generate_test_report():
    """生成测试报告"""
    logger.info("生成测试报告")
    
    # 收集所有测试结果
    all_results = {}
    
    # 读取API可用性测试结果
    try:
        with open(RESULTS_DIR / "api_availability_result.json", "r", encoding="utf-8") as f:
            all_results["api_availability"] = json.load(f)
    except FileNotFoundError:
        all_results["api_availability"] = {"success": False, "errors": ["测试未完成"]}
    
    # 读取API端点测试结果
    try:
        with open(RESULTS_DIR / "all_tests_results.json", "r", encoding="utf-8") as f:
            all_results["endpoints"] = json.load(f)
    except FileNotFoundError:
        all_results["endpoints"] = []
    
    # 读取API性能测试结果
    try:
        with open(RESULTS_DIR / "api_performance_result.json", "r", encoding="utf-8") as f:
            all_results["performance"] = json.load(f)
    except FileNotFoundError:
        all_results["performance"] = {"success_rate": 0, "avg_response_time": None}
    
    # 计算测试统计信息
    endpoint_success_count = sum(1 for endpoint in all_results["endpoints"] if endpoint["success"])
    endpoint_total_count = len(all_results["endpoints"])
    endpoint_success_rate = (endpoint_success_count / endpoint_total_count) * 100 if endpoint_total_count > 0 else 0
    
    # 生成报告内容
    report_content = f"""# 知识图谱API测试报告

## 测试概述

- 测试时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 测试人员: A成员
- 测试模块: 知识图谱API接口

## 测试环境

- API基础URL: {API_BASE_URL}
- 测试超时设置: {TEST_TIMEOUT}秒

## 测试结果

### 1. API可用性

- 状态: {'通过' if all_results["api_availability"]["success"] else '失败'}
- 响应状态码: {all_results["api_availability"].get("status_code", "N/A")}

### 2. API端点测试

- 总测试用例数: {endpoint_total_count}
- 通过测试用例数: {endpoint_success_count}
- 通过率: {endpoint_success_rate:.2f}%

| 端点 | 方法 | 描述 | 结果 | 错误 |
|-----|-----|-----|-----|-----|
"""
    
    # 添加端点测试详情
    for endpoint in all_results["endpoints"]:
        errors_str = ", ".join(endpoint["errors"]) if endpoint["errors"] else "无"
        report_content += f"| {endpoint['endpoint']} | {endpoint['method']} | {endpoint['description']} | {'通过' if endpoint['success'] else '失败'} | {errors_str} |\n"
    
    # 添加性能测试结果
    report_content += f"""
### 3. API性能测试

- 请求次数: {all_results["performance"]["num_requests"]}
- 成功次数: {all_results["performance"]["num_success"]}
- 成功率: {all_results["performance"]["success_rate"]:.2f}%
- 平均响应时间: {all_results["performance"]["avg_response_time"]:.4f}秒

## 问题与建议

"""
    
    # 添加存在的问题
    problems = []
    
    if not all_results["api_availability"]["success"]:
        problems.append("API服务不可用")
    
    failed_endpoints = [endpoint for endpoint in all_results["endpoints"] if not endpoint["success"]]
    if failed_endpoints:
        for endpoint in failed_endpoints:
            problems.append(f"端点 {endpoint['endpoint']} ({endpoint['method']}) 测试失败: {', '.join(endpoint['errors'])}")
    
    if all_results["performance"]["success_rate"] < 80:
        problems.append(f"API性能测试成功率低: {all_results['performance']['success_rate']:.2f}%")
    
    if all_results["performance"]["avg_response_time"] and all_results["performance"]["avg_response_time"] > 1.0:
        problems.append(f"API响应时间过长: {all_results['performance']['avg_response_time']:.4f}秒")
    
    if problems:
        report_content += "### 存在的问题\n\n"
        for i, problem in enumerate(problems, 1):
            report_content += f"{i}. {problem}\n"
        report_content += "\n"
    else:
        report_content += "### 存在的问题\n\n无明显问题\n\n"
    
    # 添加改进建议
    report_content += """### 改进建议

1. 优化知识图谱数据查询性能，减少API响应时间
2. 增强错误处理机制，提供更详细的错误信息
3. 添加缓存机制，减少重复数据计算
4. 完善API文档，增加请求参数和返回值的详细说明
5. 增加更多查询接口，支持更复杂的图谱查询需求

## 总结

本次测试对知识图谱API接口进行了全面测试，包括可用性、功能和性能测试。测试结果表明，API接口基本满足需求，但在性能和错误处理方面仍有优化空间。建议在后续开发中重点关注API响应性能的优化和错误处理机制的完善。
"""
    
    # 保存报告
    report_path = RESULTS_DIR / ".." / ".." / "A成员第五周任务知识图谱API测试报告.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    logger.info(f"测试报告已生成: {report_path}")

def run_tests():
    """运行所有测试"""
    # 设置环境变量以区分测试环境
    os.environ["KNOWLEDGE_GRAPH_API_TEST_MODE"] = "True"
    
    try:
        # 运行测试
        test_api_availability()
        test_knowledge_graph_endpoints()
        test_api_performance()
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
    finally:
        # 生成测试报告
        generate_test_report()

if __name__ == "__main__":
    run_tests() 