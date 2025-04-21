"""
测试脚本：用于检查run.bat的启动和功能运行情况
可测试不同的命令行参数和启动模式
"""
import subprocess
import time
import sys
import os
import socket
import requests
import platform
import signal
from pathlib import Path

# 设置全局超时
TIMEOUT = 10
# 设置运行的进程
running_process = None

def get_root_dir():
    """获取项目根目录"""
    current_file = Path(__file__).resolve()
    return current_file.parent.parent

def is_port_in_use(port):
    """检查指定端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def terminate_process():
    """终止运行的进程"""
    global running_process
    if running_process:
        print("正在终止服务器进程...")
        if platform.system() == "Windows":
            # Windows下终止进程
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(running_process.pid)], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Unix/Linux/Mac下终止进程
            try:
                os.killpg(os.getpgid(running_process.pid), signal.SIGTERM)
            except:
                running_process.terminate()
        
        running_process = None
        print("服务器进程已终止")
        
        # 等待端口释放
        time.sleep(2)

def run_bat_with_params(params=None):
    """运行bat文件并返回进程"""
    global running_process
    
    # 首先终止之前的进程
    terminate_process()
    
    # 项目根目录
    root_dir = get_root_dir()
    bat_path = os.path.join(root_dir, "run.bat")
    
    # 确保bat文件存在
    if not os.path.exists(bat_path):
        print(f"错误：找不到批处理文件: {bat_path}")
        return None
    
    # 构建命令
    cmd = [bat_path]
    if params:
        cmd.extend(params)
    
    print(f"运行命令: {' '.join(cmd)}")
    
    try:
        if platform.system() == "Windows":
            # Windows下使用CREATE_NEW_CONSOLE创建新窗口
            running_process = subprocess.Popen(cmd, 
                                 creationflags=subprocess.CREATE_NEW_CONSOLE,
                                 cwd=root_dir)
        else:
            # Unix/Linux/Mac下在后台运行
            running_process = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 cwd=root_dir)
        
        print(f"进程已启动，PID: {running_process.pid}")
        return running_process
    except Exception as e:
        print(f"启动批处理文件时出错: {str(e)}")
        return None

def wait_for_server(port, max_wait=30):
    """等待服务器启动，返回是否成功启动"""
    print(f"等待服务器在端口 {port} 上启动...")
    
    for i in range(max_wait):
        if is_port_in_use(port):
            print(f"\n✅ 服务器已在端口 {port} 上启动!")
            time.sleep(2)  # 额外等待确保API可用
            return True
            
        if i % 5 == 0:
            print(f"已等待 {i} 秒...")
        else:
            print(".", end="", flush=True)
            
        time.sleep(1)
    
    print(f"\n❌ 服务器启动超时（{max_wait}秒）!")
    return False

def test_server_api(port):
    """测试服务器API是否正常响应"""
    endpoints = [
        "",                # 根路径
        "/dashboard",      # 演示界面
        "/health",         # 健康检查
        "/docs"            # API文档
    ]
    
    success_count = 0
    for endpoint in endpoints:
        url = f"http://localhost:{port}{endpoint}"
        print(f"\n测试访问: {url}")
        
        try:
            response = requests.get(url, timeout=TIMEOUT)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ 访问成功: {endpoint or '/'}")
                success_count += 1
                
                # 如果是健康检查API，尝试解析JSON响应
                if endpoint == "/health":
                    try:
                        health_data = response.json()
                        print(f"健康检查数据: {health_data}")
                    except:
                        print("健康检查API返回的不是有效JSON")
            else:
                print(f"❌ 访问失败: {endpoint or '/'}, 状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e.__class__.__name__}, {str(e)}")
    
    success_rate = (success_count / len(endpoints)) * 100
    print(f"\n测试完成: {success_count}/{len(endpoints)} 通过 ({success_rate:.1f}%)")
    return success_count == len(endpoints)

def test_bat_file():
    """测试批处理文件的各种启动参数"""
    test_cases = [
        {
            "name": "默认参数",
            "params": [],
            "port": 8000
        },
        {
            "name": "指定端口",
            "params": ["-port", "8080"],
            "port": 8080
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print("\n" + "="*50)
        print(f"测试场景: {test_case['name']}")
        print("="*50)
        
        # 启动服务器
        proc = run_bat_with_params(test_case['params'])
        if not proc:
            results.append({
                "case": test_case['name'],
                "success": False,
                "error": "启动失败"
            })
            continue
        
        # 等待服务器启动
        port = test_case['port']
        server_started = wait_for_server(port)
        
        if not server_started:
            terminate_process()
            results.append({
                "case": test_case['name'],
                "success": False,
                "error": "服务器启动超时"
            })
            continue
        
        # 测试API
        api_success = test_server_api(port)
        
        # 终止进程
        terminate_process()
        
        # 记录结果
        results.append({
            "case": test_case['name'],
            "success": server_started and api_success,
            "error": None if (server_started and api_success) else "API测试失败"
        })
    
    # 打印测试摘要
    print("\n" + "="*50)
    print("测试摘要")
    print("="*50)
    
    all_success = True
    for result in results:
        status = "✅ 通过" if result['success'] else f"❌ 失败 ({result['error']})"
        print(f"{result['case']}: {status}")
        all_success = all_success and result['success']
    
    if all_success:
        print("\n✅ 全部测试通过!")
    else:
        print("\n❌ 测试存在失败项!")
    
    return all_success

if __name__ == "__main__":
    try:
        print("开始测试run.bat文件...")
        test_bat_file()
    except KeyboardInterrupt:
        print("\n用户中断测试")
    finally:
        # 确保进程被终止
        terminate_process() 