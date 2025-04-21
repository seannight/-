"""
简单测试脚本，用于检查演示页面是否可访问
最新版本：修复启动和连接问题，提高稳定性
"""
import requests
import time
import sys
import os
import socket
import subprocess
import signal
import platform
from urllib.parse import urlparse

# 设置全局超时
TIMEOUT = 5

def find_available_ports():
    """查找本地可能正在运行服务的端口"""
    potential_ports = []
    common_ports = [8000, 8080, 3000, 5000, 8800]
    
    # 首先检查环境变量中的端口
    env_port = os.environ.get("API_PORT")
    if env_port and env_port.isdigit():
        common_ports.insert(0, int(env_port))
    
    # 检查哪些端口已被占用（可能是我们的服务）
    for port in common_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result == 0:  # 端口已被占用
            potential_ports.append(port)
    
    return potential_ports

def start_server_if_needed(port=8000):
    """如果服务器未运行，尝试启动服务器"""
    # 检查端口是否已被占用
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    
    if result != 0:  # 端口未被占用，服务器未运行
        print(f"服务器未运行在端口 {port}，正在尝试启动...")
        
        # 根据操作系统选择合适的启动命令
        if os.name == 'nt':  # Windows
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            os.environ["API_PORT"] = str(port)
            os.environ["FASTSTART"] = "1"
            
            # 在新的窗口中启动服务器
            try:
                print("使用新窗口方式启动服务器...")
                # 使用start命令在新窗口中启动
                cmd = f'start "TeddyCup Server" cmd /c "cd {script_path} && python -m app.main --port {port} --emergency"'
                subprocess.Popen(cmd, shell=True)
            except Exception as e:
                print(f"无法通过start命令启动服务器: {str(e)}")
                try:
                    # 尝试直接启动
                    print("尝试直接启动服务器...")
                    cmd = [sys.executable, "-m", "app.main", "--port", str(port), "--emergency"]
                    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
                except Exception as e2:
                    print(f"无法启动服务器: {str(e2)}")
                    return False
        else:  # Unix/Linux/Mac
            print("使用Python命令启动服务器...")
            env = os.environ.copy()
            env["API_PORT"] = str(port)
            env["FASTSTART"] = "1"
            
            try:
                # 尝试在后台启动
                cmd = [sys.executable, "-m", "app.main", "--port", str(port), "--emergency"]
                proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # 不等待进程完成，在后台运行
            except Exception as e:
                print(f"启动服务器出错: {str(e)}")
                return False
            
        # 等待服务器启动
        print(f"等待服务器启动，端口: {port}...")
        for i in range(30):  # 最多等待30秒
            time.sleep(1)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                print(f"\n✅ 服务器已在端口 {port} 上启动!")
                time.sleep(2)  # 额外等待2秒，确保API可用
                return True
            if i % 5 == 0:
                print(f"已等待 {i} 秒...")
            else:
                print(".", end="", flush=True)
            
        print(f"\n❌ 无法启动服务器，超时!")
        return False
    else:
        print(f"服务器已在端口 {port} 上运行")
        return True

def test_with_retry(url, max_retries=5, timeout=TIMEOUT, retry_delay=2):
    """带重试机制的HTTP请求测试"""
    for attempt in range(max_retries):
        try:
            print(f"尝试访问 {url} (尝试 {attempt+1}/{max_retries})")
            response = requests.get(url, timeout=timeout)
            return response
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                print(f"连接失败，{retry_delay}秒后重试... (ConnectionError)")
                time.sleep(retry_delay)
            else:
                print(f"❌ 无法连接到服务器: {url}")
                return None
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"请求超时，{retry_delay}秒后重试... (Timeout)")
                time.sleep(retry_delay)
            else:
                print(f"❌ 请求超时: {url}")
                return None
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"请求失败，{retry_delay}秒后重试... ({e.__class__.__name__})")
                time.sleep(retry_delay)
            else:
                print(f"❌ 所有尝试均失败: {str(e)}")
                return None
    return None

def test_demo_page(base_url=None, start_if_needed=False):
    """测试演示页面是否可访问"""
    print("开始测试演示页面...")
    
    # 如果未提供基础URL，尝试找到可能的端口
    if not base_url:
        potential_ports = find_available_ports()
        
        if not potential_ports:
            port = 8080
            print(f"未找到任何可能的端口，将使用默认端口{port}")
            potential_ports = [port]
            
            if start_if_needed:
                start_server_if_needed(port)
        
        # 尝试所有潜在端口
        server_found = False
        for port in potential_ports:
            test_url = f"http://localhost:{port}"
            print(f"尝试测试服务器: {test_url}")
            
            try:
                response = requests.get(f"{test_url}/health", timeout=TIMEOUT)
                if response.status_code == 200:
                    print(f"✅ 在端口 {port} 上找到活跃的服务器!")
                    base_url = test_url
                    server_found = True
                    break
            except requests.exceptions.RequestException:
                continue
        
        # 如果没有找到服务器且需要启动，选择第一个端口启动
        if not server_found and start_if_needed:
            port = potential_ports[0] if potential_ports else 8080
            if start_server_if_needed(port):
                base_url = f"http://localhost:{port}"
                server_found = True
        
        if not base_url:
            default_port = 8080
            print(f"❌ 未找到活跃的服务器，将使用默认端口{default_port}")
            # 如果需要启动服务器
            if start_if_needed:
                if start_server_if_needed(default_port):
                    base_url = f"http://localhost:{default_port}"
                else:
                    print("⚠️ 无法启动服务器，测试可能会失败")
            if not base_url:
                base_url = f"http://localhost:{default_port}"
    
    print(f"使用基础URL: {base_url}")
    
    # 尝试访问首页
    print(f"\n测试访问: {base_url}")
    response = test_with_retry(base_url)
    if response:
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 首页访问成功!")
        else:
            print(f"❌ 首页访问失败! 状态码: {response.status_code}")
    
    # 尝试访问演示页面
    print(f"\n测试访问: {base_url}/dashboard")
    response = test_with_retry(f"{base_url}/dashboard")
    if response:
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 演示页面访问成功!")
        else:
            print(f"❌ 演示页面访问失败! 状态码: {response.status_code}")
    
    # 尝试访问健康检查API
    print(f"\n测试访问: {base_url}/health")
    response = test_with_retry(f"{base_url}/health")
    if response:
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 健康检查API访问成功!")
            try:
                print(f"响应内容摘要: {response.json()}")
            except:
                print("无法解析JSON响应")
        else:
            print(f"❌ 健康检查API访问失败! 状态码: {response.status_code}")
    return True

if __name__ == "__main__":
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='测试演示页面')
    parser.add_argument('--url', type=str, help='服务器基础URL')
    parser.add_argument('--wait', type=int, default=5, help='等待服务器启动的秒数')
    parser.add_argument('--start', action='store_true', help='如果服务器未运行，尝试启动')
    parser.add_argument('--port', type=int, help='指定服务器端口')
    args = parser.parse_args()
    
    # 如果指定了端口，把它设为环境变量
    if args.port:
        os.environ["API_PORT"] = str(args.port)
        if args.start:
            start_server_if_needed(args.port)
    
    # 等待服务器启动
    if args.wait > 0:
        print(f"等待服务器启动 {args.wait} 秒...")
        time.sleep(args.wait)
    
    # 执行测试
    url = args.url
    if not url and args.port:
        url = f"http://localhost:{args.port}"
        
    try:
        test_demo_page(url, start_if_needed=args.start)
        print("\n测试完成!")
    except KeyboardInterrupt:
        print("\n测试被用户中断!")
    except Exception as e:
        print(f"\n测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("测试结束") 