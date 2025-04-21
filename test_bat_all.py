"""
全面测试脚本：用于测试run.bat的所有功能和参数组合
支持-port/-open/-help等参数的测试，模拟实际使用场景
"""
import subprocess
import time
import sys
import os
import socket
import requests
import platform
import signal
import webbrowser
from pathlib import Path
import argparse
import psutil

# 设置全局超时
TIMEOUT = 10
# 设置运行的进程
running_process = None
# 测试状态
TEST_STATUS = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0
}

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

def kill_process_by_port(port):
    """关闭占用指定端口的进程"""
    if platform.system() != "Windows":
        return False  # 非Windows系统暂不支持

    try:
        # 使用netstat查找端口占用进程
        output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
        
        # 解析输出找到PID
        lines = output.strip().split('\n')
        if not lines:
            return False
            
        # 通常PID在最后一列
        for line in lines:
            if f":{port}" in line and "LISTENING" in line:
                parts = line.strip().split()
                if len(parts) >= 5:
                    pid = int(parts[-1])
                    # 终止进程
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                    print(f"已终止占用端口 {port} 的进程，PID: {pid}")
                    return True
        
        return False
    except Exception as e:
        print(f"尝试终止占用端口 {port} 的进程时出错: {str(e)}")
        return False

def is_browser_opened(url):
    """检查是否有浏览器打开了指定URL（仅在Windows下有效）"""
    if platform.system() != "Windows":
        return False  # 非Windows系统暂不支持
        
    # 获取所有进程名
    browser_names = ['chrome.exe', 'msedge.exe', 'firefox.exe', 'iexplore.exe', 'opera.exe']
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # 检查是否是浏览器进程
            proc_name = proc.info['name'].lower()
            if any(browser in proc_name for browser in browser_names):
                return True  # 发现浏览器进程即认为可能已打开
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    return False

def terminate_process():
    """终止运行的进程"""
    global running_process
    if running_process:
        print("正在终止服务器进程...")
        try:
            if platform.system() == "Windows":
                # Windows下终止进程树
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(running_process.pid)], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                # Unix/Linux/Mac下终止进程组
                try:
                    os.killpg(os.getpgid(running_process.pid), signal.SIGTERM)
                except:
                    running_process.terminate()
                    
            # 等待进程终止
            try:
                running_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("进程未能在规定时间内终止，强制终止")
                if platform.system() == "Windows":
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(running_process.pid)], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    running_process.kill()
        except Exception as e:
            print(f"终止进程时出错: {str(e)}")
        
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
                                 cwd=root_dir,
                                 preexec_fn=os.setsid)
        
        print(f"进程已启动，PID: {running_process.pid}")
        return running_process
    except Exception as e:
        print(f"启动批处理文件时出错: {str(e)}")
        return None

def run_bat_with_help():
    """运行批处理文件的帮助命令并获取输出"""
    root_dir = get_root_dir()
    bat_path = os.path.join(root_dir, "run.bat")
    
    try:
        # 使用-help参数运行
        result = subprocess.run([bat_path, "-help"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              cwd=root_dir,
                              encoding='utf-8',
                              shell=True)
        
        if result.returncode == 0:
            print("帮助命令执行成功！")
            print("\n输出内容:")
            print("-" * 50)
            print(result.stdout)
            print("-" * 50)
            return True
        else:
            print(f"帮助命令执行失败，返回码: {result.returncode}")
            print(f"错误信息: {result.stderr}")
            return False
    except Exception as e:
        print(f"执行帮助命令时出错: {str(e)}")
        return False

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

def record_test_result(case_name, success, error=None):
    """记录测试结果并更新全局统计"""
    global TEST_STATUS
    
    TEST_STATUS["total"] += 1
    if success:
        TEST_STATUS["passed"] += 1
        status = "✅ 通过"
    else:
        TEST_STATUS["failed"] += 1
        status = f"❌ 失败 ({error})" if error else "❌ 失败"
    
    print(f"{case_name}: {status}")
    return {
        "case": case_name,
        "success": success,
        "error": error
    }

def print_test_summary():
    """打印测试摘要"""
    print("\n" + "="*50)
    print("测试摘要")
    print("="*50)
    
    total = TEST_STATUS["total"]
    passed = TEST_STATUS["passed"]
    failed = TEST_STATUS["failed"]
    skipped = TEST_STATUS["skipped"]
    
    print(f"总测试数: {total}")
    print(f"通过数: {passed} ({(passed/total*100):.1f}% 通过率)")
    print(f"失败数: {failed}")
    print(f"跳过数: {skipped}")
    
    if failed == 0:
        print("\n✅ 全部测试通过!")
    else:
        print(f"\n❌ 有 {failed} 个测试失败!")
    
    return failed == 0

def test_help_parameter():
    """测试-help参数功能"""
    print("\n" + "="*50)
    print("测试场景: 帮助参数")
    print("="*50)
    
    success = run_bat_with_help()
    return record_test_result("帮助参数", success, "未正确显示帮助信息" if not success else None)

def test_port_parameter():
    """测试-port参数功能"""
    # 定义要测试的端口
    test_ports = [8080, 9000]
    results = []
    
    for port in test_ports:
        print("\n" + "="*50)
        print(f"测试场景: 指定端口 {port}")
        print("="*50)
        
        # 如果端口被占用，先尝试释放
        if is_port_in_use(port):
            print(f"端口 {port} 已被占用，尝试释放...")
            if not kill_process_by_port(port):
                print(f"无法释放端口 {port}，跳过此测试")
                result = record_test_result(f"指定端口 {port}", False, "端口已被占用")
                results.append(result)
                TEST_STATUS["skipped"] += 1
                TEST_STATUS["failed"] -= 1
                continue
        
        # 启动服务器
        proc = run_bat_with_params(["-port", str(port)])
        if not proc:
            result = record_test_result(f"指定端口 {port}", False, "启动失败")
            results.append(result)
            continue
        
        # 等待服务器启动
        server_started = wait_for_server(port)
        
        if not server_started:
            terminate_process()
            result = record_test_result(f"指定端口 {port}", False, "服务器启动超时")
            results.append(result)
            continue
        
        # 测试API
        api_success = test_server_api(port)
        
        # 终止进程
        terminate_process()
        
        # 记录结果
        result = record_test_result(
            f"指定端口 {port}", 
            server_started and api_success, 
            "API测试失败" if not api_success else None
        )
        results.append(result)
    
    return results

def test_open_parameter():
    """测试-open参数功能"""
    print("\n" + "="*50)
    print("测试场景: 自动打开浏览器")
    print("="*50)
    
    # 选择一个可用端口
    port = 8888
    if is_port_in_use(port):
        print(f"端口 {port} 已被占用，尝试释放...")
        if not kill_process_by_port(port):
            print(f"无法释放端口 {port}，使用备用端口")
            port = 9999
            if is_port_in_use(port):
                print(f"备用端口 {port} 也被占用")
                result = record_test_result("自动打开浏览器", False, "所有测试端口均被占用")
                TEST_STATUS["skipped"] += 1
                TEST_STATUS["failed"] -= 1
                return result
    
    # 检查之前是否有浏览器打开测试URL
    test_url = f"http://localhost:{port}/dashboard"
    # 启动服务器并指定open参数
    proc = run_bat_with_params(["-port", str(port), "-open"])
    if not proc:
        return record_test_result("自动打开浏览器", False, "启动失败")
    
    # 等待服务器启动
    server_started = wait_for_server(port)
    
    if not server_started:
        terminate_process()
        return record_test_result("自动打开浏览器", False, "服务器启动超时")
    
    # 检查是否打开了浏览器
    print("检查是否自动打开了浏览器...")
    time.sleep(3)  # 给浏览器启动一些时间
    
    # 在Windows上尝试检测是否有浏览器进程
    browser_opened = is_browser_opened(test_url)
    
    if browser_opened:
        print("✅ 检测到浏览器已打开")
        browser_test = True
    else:
        print("❓ 无法确定浏览器是否已打开，通过API测试验证功能")
        # 退回到API测试
        browser_test = test_server_api(port)
    
    # 终止进程
    terminate_process()
    
    return record_test_result(
        "自动打开浏览器", 
        server_started and browser_test, 
        "浏览器未打开或API测试失败" if not browser_test else None
    )

def test_default_parameters():
    """测试默认参数启动"""
    print("\n" + "="*50)
    print("测试场景: 默认参数")
    print("="*50)
    
    # 默认端口
    port = 8000
    
    # 如果端口被占用，先尝试释放
    if is_port_in_use(port):
        print(f"默认端口 {port} 已被占用，尝试释放...")
        if not kill_process_by_port(port):
            print(f"无法释放默认端口 {port}，跳过此测试")
            result = record_test_result("默认参数", False, "默认端口已被占用")
            TEST_STATUS["skipped"] += 1
            TEST_STATUS["failed"] -= 1
            return result
    
    # 启动服务器
    proc = run_bat_with_params([])
    if not proc:
        return record_test_result("默认参数", False, "启动失败")
    
    # 等待服务器启动
    server_started = wait_for_server(port)
    
    if not server_started:
        terminate_process()
        return record_test_result("默认参数", False, "服务器启动超时")
    
    # 测试API
    api_success = test_server_api(port)
    
    # 终止进程
    terminate_process()
    
    return record_test_result(
        "默认参数", 
        server_started and api_success, 
        "API测试失败" if not api_success else None
    )

def run_all_tests():
    """运行所有测试"""
    results = []
    
    # 测试帮助参数
    try:
        result = test_help_parameter()
        if isinstance(result, list):
            results.extend(result)
        else:
            results.append(result)
    except Exception as e:
        print(f"执行帮助参数测试时出错: {str(e)}")
        results.append(record_test_result("帮助参数", False, f"测试执行错误: {str(e)}"))
    
    # 测试默认参数
    try:
        result = test_default_parameters()
        if isinstance(result, list):
            results.extend(result)
        else:
            results.append(result)
    except Exception as e:
        print(f"执行默认参数测试时出错: {str(e)}")
        results.append(record_test_result("默认参数", False, f"测试执行错误: {str(e)}"))
    
    # 测试端口参数
    try:
        result = test_port_parameter()
        if isinstance(result, list):
            results.extend(result)
        else:
            results.append(result)
    except Exception as e:
        print(f"执行端口参数测试时出错: {str(e)}")
        results.append(record_test_result("端口参数", False, f"测试执行错误: {str(e)}"))
    
    # 测试自动打开浏览器参数
    try:
        result = test_open_parameter()
        if isinstance(result, list):
            results.extend(result)
        else:
            results.append(result)
    except Exception as e:
        print(f"执行自动打开浏览器参数测试时出错: {str(e)}")
        results.append(record_test_result("自动打开浏览器", False, f"测试执行错误: {str(e)}"))
    
    # 打印测试摘要
    all_passed = print_test_summary()
    
    return all_passed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="测试run.bat批处理文件")
    parser.add_argument('--help-only', action='store_true', help='仅测试帮助参数')
    parser.add_argument('--port-only', action='store_true', help='仅测试端口参数')
    parser.add_argument('--open-only', action='store_true', help='仅测试自动打开浏览器参数')
    parser.add_argument('--default-only', action='store_true', help='仅测试默认参数')
    
    args = parser.parse_args()
    
    try:
        print("开始测试run.bat批处理文件...")
        
        if args.help_only:
            test_help_parameter()
        elif args.port_only:
            test_port_parameter()
        elif args.open_only:
            test_open_parameter()
        elif args.default_only:
            test_default_parameters()
        else:
            run_all_tests()
            
    except KeyboardInterrupt:
        print("\n用户中断测试")
    finally:
        # 确保进程被终止
        terminate_process() 