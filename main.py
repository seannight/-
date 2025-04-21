"""
泰迪杯项目 - API服务主程序
负责人: A成员 (整合BC成员代码)
功能: 提供PDF解析和问答API服务
更新日期: 2023-04-10
版本: 2.2.0
"""

import os
import sys
import time
import threading
import traceback
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union
import logging
import json
import uuid
import shutil
from pathlib import Path
import asyncio
from contextlib import asynccontextmanager

# 获取项目根目录路径
PROJECT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_DIR))

# 读取teddy_config.txt中的端口配置
TEDDY_CONFIG_FILE = os.path.join(PROJECT_DIR, "teddy_config.txt")
DEFAULT_PORT = 53085  # 与teddy_server.py中的默认端口保持一致

def read_port_from_config():
    """从teddy_config.txt读取端口配置"""
    try:
        if os.path.exists(TEDDY_CONFIG_FILE):
            with open(TEDDY_CONFIG_FILE, "r") as f:
                for line in f:
                    if line.startswith("API_PORT="):
                        return int(line.strip().split("=")[1])
    except Exception as e:
        print(f"读取端口配置失败: {str(e)}")
    return DEFAULT_PORT

# 导入依赖模块
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from starlette.exceptions import HTTPException as StarletteHTTPException

# 导入内部模块
from app.routers import qa_router, table_router, ui_router, session_router
from app.core.config import get_app_config

# 尝试导入改进后的会话API
try:
    from app.api import session_router as api_session_router
    HAS_IMPROVED_SESSION_API = True
except ImportError:
    HAS_IMPROVED_SESSION_API = False

# 尝试导入知识图谱API
try:
    from app.api.knowledge_graph import router as knowledge_graph_router
    HAS_KNOWLEDGE_GRAPH_API = True
except ImportError:
    HAS_KNOWLEDGE_GRAPH_API = False
    knowledge_graph_router = None

    # 如果简化版监控不可用，使用传统监控
    from app.core.monitoring import (
        ResponseTimeTracker, init_monitoring, get_system_info,
        get_performance_metrics, get_component_health, cleanup_resources, 
        register_component_health
    )
    USE_SIMPLE_MONITOR = False
else:
    # 导入简化版监控模块
    from app.core.simple_monitor import SimpleMonitor
    monitor = SimpleMonitor()
    USE_SIMPLE_MONITOR = True

# 导入优化的快速启动模块（新增）
try:
    from app.core.fast_starter import (
        create_background_loader, get_lightweight_response, 
        is_components_loaded, get_loading_status
    )
    USE_FAST_STARTER = True
except ImportError:
    from app.core.component_loader import load_components_async
    USE_FAST_STARTER = False

# 获取配置
app_config = get_app_config()

# 组件加载状态
components_loaded = False

# 响应缓存
response_cache = {}

# 定义应用生命周期管理

# 组件加载函数
async def load_components_async(component_loaders=None):
    """组件异步加载函数"""
    if component_loaders:
        print("正在加载组件...")
        for name, loader in component_loaders.items():
            print(f"加载组件: {name}")
            success = await loader()
            print(f"组件 {name} 加载{'成功' if success else '失败'}")
    else:
        print("无组件需要加载")
    return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global components_loaded
    
    # 启动时执行
    print("🚀 正在启动应用...")
    
    # 定义组件加载函数
    component_loaders = {}
    
    # 添加PDF处理模块
    async def load_data_processing():
        try:
            # 正确导入extract_tables函数
            from app.data_processing import extract_tables, extract_text
            print("✅ PDF处理模块加载成功")
            return True
        except Exception as e:
            print(f"❌ PDF处理模块加载失败: {str(e)}")
            traceback.print_exc()  # 添加堆栈跟踪，方便调试
            return False
    
    # 添加问答引擎模块
    async def load_qa_engine():
        try:
            from app.qa import engine
            print("✅ 问答引擎加载成功")
            return True
        except Exception as e:
            print(f"❌ 问答引擎加载失败: {str(e)}")
            return False
    
    # 添加知识图谱模块
    async def load_knowledge_graph():
        try:
            from app.models.knowledge_graph import KnowledgeGraph
            # 直接导入router避免使用.router属性
            print("✅ 知识图谱模块加载成功")
            return True
        except Exception as e:
            print(f"❌ 知识图谱模块加载失败: {str(e)}")
            return False
    
    # 配置需要加载的组件
    component_loaders["data_processing"] = load_data_processing
    component_loaders["qa_engine"] = load_qa_engine
    component_loaders["knowledge_graph"] = load_knowledge_graph
    
    # 根据不同模块选择不同的加载方式
    if USE_FAST_STARTER and app_config.FAST_MODE:
        # 使用优化的快速启动模块 - 后台加载
        create_background_loader(component_loaders)
        print("⚡ 使用优化的快速启动模式")
    elif app_config.FAST_MODE:
        # 使用传统的快速启动 - 后台加载
        if not USE_SIMPLE_MONITOR:
            init_monitoring()
            register_component_health("API服务", "healthy", "API服务已启动")
            register_component_health("模型加载", "loading", "模型正在后台加载中")
        asyncio.create_task(load_components_async())
        print("⚡ 快速启动模式已激活，组件将在后台加载")
    else:
        # 标准模式 - 同步加载组件
        print("📚 正在加载组件...")
        if USE_FAST_STARTER:
            # 使用优化的组件加载器
            await load_components_async(component_loaders)
        else:
            # 使用传统的组件加载器
            if not USE_SIMPLE_MONITOR:
                init_monitoring()
            await load_components_async()
            if not USE_SIMPLE_MONITOR:
                register_component_health("模型加载", "healthy", "模型已完全加载")
        
        components_loaded = True
        print("✅ 组件加载完成")
    
    yield
    
    # 关闭时执行
    print("🛑 正在关闭应用...")
    # 清理资源
    if not USE_SIMPLE_MONITOR:
        cleanup_resources()
    print("👋 应用已关闭")

# 创建FastAPI应用
app = FastAPI(
    title="泰迪杯智能客服系统",
    description="基于FastAPI的智能问答和表格处理系统",
    version="2.2.0",
    lifespan=lifespan,
    docs_url="/docs" if app_config.ENABLE_DOCS else None,
    redoc_url="/redoc" if app_config.ENABLE_DOCS else None,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# 添加CORS中间件，解决跨域问题
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应设置为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置静态文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 配置模板
templates = Jinja2Templates(directory="app/templates")

# 注册路由
app.include_router(qa_router.router, prefix="/api", tags=["问答系统"])
app.include_router(table_router.router, prefix="/api", tags=["表格处理"])
app.include_router(ui_router.router, tags=["用户界面"])
app.include_router(session_router.router, prefix="/api", tags=["会话管理"])

# 注册改进版会话API (如果可用)
if HAS_IMPROVED_SESSION_API:
    app.include_router(api_session_router.router, prefix="/api", tags=["会话管理API"])

# 注册知识图谱API (如果可用)
if HAS_KNOWLEDGE_GRAPH_API:
    app.include_router(knowledge_graph_router, prefix="/api", tags=["知识图谱"])

# 增加直接API路由注册，确保健康检查可被前端访问
# 直接注册到主应用
from app.api.health import router as health_router
app.include_router(health_router, prefix="/api", tags=["健康检查"])

# 尝试导入和注册会话API
# try:
#     from app.api.session import router as sessions_router
#     app.include_router(sessions_router, prefix="/api", tags=["会话管理"])
# except ImportError:
#     print("警告: 会话API模块无法导入")

# 性能监控中间件
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """记录请求处理时间并添加性能指标到响应中"""
    # 记录开始时间
    start_time = time.time()
    success = True
    
    try:
        # 处理请求
        response = await call_next(request)
        
        # 判断是否成功
        success = response.status_code < 400
    except Exception:
        success = False
        raise
    finally:
        # 计算处理时间
        duration = time.time() - start_time
        
        # 使用监控记录请求
        endpoint = f"{request.method} {request.url.path}"
        if USE_SIMPLE_MONITOR:
            monitor.track_request(endpoint, duration, success=success)
        
    # 添加响应头
    response.headers["X-Process-Time"] = str(duration)
    
    return response

# 缓存中间件
@app.middleware("http")
async def cache_middleware(request: Request, call_next):
    """对频繁访问的只读端点进行缓存"""
    cache_key = f"{request.method}:{request.url.path}"
    
    # 只缓存GET请求的特定路径
    if request.method == "GET" and any(path in request.url.path for path in ["/tables", "/health"]):
        if cache_key in response_cache and time.time() - response_cache[cache_key]["timestamp"] < 30:
            return Response(
                content=response_cache[cache_key]["content"],
                media_type=response_cache[cache_key]["media_type"],
                status_code=200
            )
    
    response = await call_next(request)
    
    # 缓存响应
    if request.method == "GET" and any(path in request.url.path for path in ["/tables", "/health"]):
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
            
        response_cache[cache_key] = {
            "content": response_body,
            "media_type": response.media_type,
            "timestamp": time.time()
        }
        
        return Response(
            content=response_body,
            media_type=response.media_type,
            status_code=response.status_code
        )
        
    return response

# 健康检查接口
@app.get("/health", tags=["系统"])
async def health_check():
    """
    系统健康检查接口，返回系统状态和组件健康信息
    """
    if USE_SIMPLE_MONITOR:
        # 使用简化版监控
        system_info = monitor.get_system_info()
        
        # 获取组件加载状态
        if USE_FAST_STARTER:
            load_status = "completed" if is_components_loaded() else "loading"
            loading_info = get_loading_status() if not is_components_loaded() else {}
        else:
            load_status = "completed" if components_loaded else "loading"
            loading_info = {}
        
        # 构建响应
        response = {
            "status": system_info["status"],
            "system": system_info["system"],
            "process": system_info["process"],
            "load_status": load_status,
            "requests": system_info["requests"],
            "timestamp": datetime.now().isoformat()
        }
        
        # 添加组件加载详情
        if loading_info:
            response["loading"] = loading_info
            
        return response
    else:
        # 传统监控
        system_info = get_system_info()
        health_data = get_component_health()
        
        # 确保使用英文状态值来避免编码问题
        components = {}
        for component, data in health_data["components"].items():
            # 复制原始数据
            clean_data = data.copy()
            
            # 标准化状态值为英文
            if "status" in clean_data:
                status = clean_data["status"].lower() if isinstance(clean_data["status"], str) else "unknown"
                if "健康" in status or "正常" in status:
                    clean_data["status"] = "healthy"
                elif "警告" in status:
                    clean_data["status"] = "warning"
                elif "错误" in status or "异常" in status:
                    clean_data["status"] = "error"
            
            # 保存处理后的组件数据
            components[component] = clean_data
        
        # 检查组件状态
        status = "healthy"
        for component, data in components.items():
            if data["status"] == "error":
                status = "error"
                break
            elif data["status"] == "warning" and status != "error":
                status = "warning"
        
        # 使用英文的加载状态
        load_status = "completed" if components_loaded else "loading"
        if not components_loaded and app_config.FAST_MODE:
            load_status += " (Fast Mode)"
        
        return {
            "status": status,
            "system": system_info,
            "load_status": load_status,
            "components": components,
            "timestamp": health_data["timestamp"]
        }

# 监控指标接口
@app.get("/monitoring/metrics", tags=["监控"])
async def system_metrics():
    """
    获取系统性能指标接口
    """
    if USE_SIMPLE_MONITOR:
        return monitor.get_detailed_metrics()
    else:
        return get_performance_metrics()

# 重置监控指标接口
@app.post("/monitoring/reset", tags=["监控"])
async def reset_metrics():
    """
    重置性能统计数据
    """
    if USE_SIMPLE_MONITOR:
        return monitor.reset_stats()
    else:
        # 清理资源
        result = cleanup_resources()
        # 重置响应缓存
        response_cache.clear()
        return {
            "status": "success",
            "message": "系统资源和监控指标已重置",
            "details": result
        }

# 根路由重定向到UI
@app.get("/", include_in_schema=False)
async def root():
    """将根路径请求重定向到仪表盘页面"""
    return RedirectResponse(url="/dashboard")

# 在生产环境中使用此代码启动服务器
if __name__ == "__main__":
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="启动泰迪杯智能客服系统")
    config_port = read_port_from_config()
    parser.add_argument("--port", type=int, default=config_port, help=f"服务器端口 (默认: {config_port})")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="服务器主机")
    parser.add_argument("--reload", action="store_true", help="启用自动重载")
    parser.add_argument("--fast", action="store_true", help="启用快速启动模式")
    parser.add_argument("--optimize", action="store_true", help="启用性能优化")
    parser.add_argument("--ui-priority", action="store_true", help="UI优先模式")
    args = parser.parse_args()
    
    # 设置环境变量
    if args.fast:
        os.environ["FAST_MODE"] = "1"
    
    if args.ui_priority:
        os.environ["UI_PRIORITY"] = "1"
    
    if args.optimize:
        os.environ["OPTIMIZE_MEMORY"] = "1"
        os.environ["ENABLE_MONITORING"] = "1"
    
    # 配置uvicorn选项
    uvicorn_config = {
        "app": "app.main:app", 
        "host": args.host, 
        "port": args.port,
        "reload": args.reload,
        "log_level": "info" if not args.optimize else "warning"
    }
    
    # 优化模式下，调整worker配置
    if args.optimize and not args.reload:
        import multiprocessing
        workers = min(multiprocessing.cpu_count(), 4)
        # 启动多进程模式需要禁用reload
        uvicorn_config["workers"] = workers
        print(f"性能优化: 使用 {workers} 个worker进程")
    
    # 启动服务器
    print(f"启动服务器 - 访问地址: http://{args.host}:{args.port}")
    uvicorn.run(**uvicorn_config)
