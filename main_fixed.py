"""
娉拌开鏉」鐩?- API鏈嶅姟涓荤▼搴?璐熻矗浜? A鎴愬憳 (鏁村悎BC鎴愬憳浠ｇ爜)
鍔熻兘: 鎻愪緵PDF瑙ｆ瀽鍜岄棶绛擜PI鏈嶅姟
鏇存柊鏃ユ湡: 2023-04-10
鐗堟湰: 2.2.0
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

# 鑾峰彇椤圭洰鏍圭洰褰曡矾寰?PROJECT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_DIR))

# 瀵煎叆渚濊禆妯″潡
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from starlette.exceptions import HTTPException as StarletteHTTPException

# 瀵煎叆鍐呴儴妯″潡
from app.routers import qa_router, table_router, ui_router, session_router
from app.core.config import get_app_config

# 瀵煎叆浼樺寲鐨勭洃鎺фā鍧楋紙鏂板锛?try:
    from app.core.simple_monitor import monitor
except ImportError:
    # 濡傛灉绠€鍖栫増鐩戞帶涓嶅彲鐢紝浣跨敤浼犵粺鐩戞帶
    from app.core.monitoring import (
        ResponseTimeTracker, init_monitoring, get_system_info,
        get_performance_metrics, get_component_health, cleanup_resources, 
        register_component_health
    )
    USE_SIMPLE_MONITOR = False
else:
    USE_SIMPLE_MONITOR = True

# 瀵煎叆浼樺寲鐨勫揩閫熷惎鍔ㄦā鍧楋紙鏂板锛?try:
    from app.core.fast_starter import (
        create_background_loader, get_lightweight_response, 
        is_components_loaded, get_loading_status
    )
    USE_FAST_STARTER = True
except ImportError:
    from app.core.component_loader import load_components_async
    USE_FAST_STARTER = False

# 鑾峰彇閰嶇疆
app_config = get_app_config()

# 缁勪欢鍔犺浇鐘舵€?components_loaded = False

# 鍝嶅簲缂撳瓨
response_cache = {}

# 瀹氫箟搴旂敤鐢熷懡鍛ㄦ湡绠＄悊
@asynccontextmanager
async def lifespan(app: FastAPI):
    """搴旂敤鐢熷懡鍛ㄦ湡绠＄悊"""
    global components_loaded
    
    # 鍚姩鏃舵墽琛?    print("馃殌 姝ｅ湪鍚姩搴旂敤...")
    
    # 瀹氫箟缁勪欢鍔犺浇鍑芥暟
    component_loaders = {}
    
    # 娣诲姞PDF澶勭悊妯″潡
    async def load_data_processing():
        try:
            from app.data_processing import extract_tables, extract_text
            print("鉁?PDF澶勭悊妯″潡鍔犺浇鎴愬姛")
            return True
        except Exception as e:
            print(f"鉂?PDF澶勭悊妯″潡鍔犺浇澶辫触: {str(e)}")
            return False
    
    # 娣诲姞闂瓟寮曟搸妯″潡
    async def load_qa_engine():
        try:
            from app.qa import engine
            print("鉁?闂瓟寮曟搸鍔犺浇鎴愬姛")
            return True
        except Exception as e:
            print(f"鉂?闂瓟寮曟搸鍔犺浇澶辫触: {str(e)}")
            return False
    
    # 閰嶇疆闇€瑕佸姞杞界殑缁勪欢
    component_loaders["data_processing"] = load_data_processing
    component_loaders["qa_engine"] = load_qa_engine
    
    # 鏍规嵁涓嶅悓妯″潡閫夋嫨涓嶅悓鐨勫姞杞芥柟寮?    if USE_FAST_STARTER and app_config.FAST_MODE:
        # 浣跨敤浼樺寲鐨勫揩閫熷惎鍔ㄦā鍧?- 鍚庡彴鍔犺浇
        create_background_loader(component_loaders)
        print("鈿?浣跨敤浼樺寲鐨勫揩閫熷惎鍔ㄦā寮?)
    elif app_config.FAST_MODE:
        # 浣跨敤浼犵粺鐨勫揩閫熷惎鍔?- 鍚庡彴鍔犺浇
        if not USE_SIMPLE_MONITOR:
            init_monitoring()
            register_component_health("API鏈嶅姟", "healthy", "API鏈嶅姟宸插惎鍔?)
            register_component_health("妯″瀷鍔犺浇", "loading", "妯″瀷姝ｅ湪鍚庡彴鍔犺浇涓?)
        asyncio.create_task(load_components_async())
        print("鈿?蹇€熷惎鍔ㄦā寮忓凡婵€娲伙紝缁勪欢灏嗗湪鍚庡彴鍔犺浇")
    else:
        # 鏍囧噯妯″紡 - 鍚屾鍔犺浇缁勪欢
        print("馃摎 姝ｅ湪鍔犺浇缁勪欢...")
        if USE_FAST_STARTER:
            # 浣跨敤浼樺寲鐨勭粍浠跺姞杞藉櫒
            await load_components_async(component_loaders)
        else:
            # 浣跨敤浼犵粺鐨勭粍浠跺姞杞藉櫒
            if not USE_SIMPLE_MONITOR:
                init_monitoring()
            await load_components_async()
            if not USE_SIMPLE_MONITOR:
                register_component_health("妯″瀷鍔犺浇", "healthy", "妯″瀷宸插畬鍏ㄥ姞杞?)
        
        components_loaded = True
        print("鉁?缁勪欢鍔犺浇瀹屾垚")
    
    yield
    
    # 鍏抽棴鏃舵墽琛?    print("馃洃 姝ｅ湪鍏抽棴搴旂敤...")
    # 娓呯悊璧勬簮
    if not USE_SIMPLE_MONITOR:
        cleanup_resources()
    print("馃憢 搴旂敤宸插叧闂?)

# 鍒涘缓FastAPI搴旂敤
app = FastAPI(
    title="娉拌开鏉櫤鑳藉鏈嶇郴缁?,
    description="鍩轰簬FastAPI鐨勬櫤鑳介棶绛斿拰琛ㄦ牸澶勭悊绯荤粺",
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

# 閰嶇疆闈欐€佹枃浠?app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 閰嶇疆妯℃澘
templates = Jinja2Templates(directory="app/templates")

# 娉ㄥ唽璺敱
app.include_router(qa_router.router, prefix="/api", tags=["闂瓟绯荤粺"])
app.include_router(table_router.router, prefix="/api", tags=["琛ㄦ牸澶勭悊"])
app.include_router(ui_router.router, tags=["鐢ㄦ埛鐣岄潰"])
app.include_router(session_router.router, prefix="/api", tags=["浼氳瘽绠＄悊"])

# 鎬ц兘鐩戞帶涓棿浠?@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """璁板綍璇锋眰澶勭悊鏃堕棿骞舵坊鍔犳€ц兘鎸囨爣鍒板搷搴斾腑"""
    # 璁板綍寮€濮嬫椂闂?    start_time = time.time()
    success = True
    
    try:
        # 澶勭悊璇锋眰
        response = await call_next(request)
        
        # 鍒ゆ柇鏄惁鎴愬姛
        success = response.status_code < 400
    except Exception:
        success = False
        raise
    finally:
        # 璁＄畻澶勭悊鏃堕棿
        duration = time.time() - start_time
        
        # 浣跨敤鐩戞帶璁板綍璇锋眰
        endpoint = f"{request.method} {request.url.path}"
        if USE_SIMPLE_MONITOR:
            monitor.track_request(endpoint, duration, success=success)
        
    # 娣诲姞鍝嶅簲澶?    response.headers["X-Process-Time"] = str(duration)
    
    return response

# 缂撳瓨涓棿浠?@app.middleware("http")
async def cache_middleware(request: Request, call_next):
    """瀵归绻佽闂殑鍙绔偣杩涜缂撳瓨"""
    cache_key = f"{request.method}:{request.url.path}"
    
    # 鍙紦瀛楪ET璇锋眰鐨勭壒瀹氳矾寰?    if request.method == "GET" and any(path in request.url.path for path in ["/tables", "/health"]):
        if cache_key in response_cache and time.time() - response_cache[cache_key]["timestamp"] < 30:
            return Response(
                content=response_cache[cache_key]["content"],
                media_type=response_cache[cache_key]["media_type"],
                status_code=200
            )
    
    response = await call_next(request)
    
    # 缂撳瓨鍝嶅簲
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

# 鍋ュ悍妫€鏌ユ帴鍙?@app.get("/health", tags=["绯荤粺"])
async def health_check():
    """
    绯荤粺鍋ュ悍妫€鏌ユ帴鍙ｏ紝杩斿洖绯荤粺鐘舵€佸拰缁勪欢鍋ュ悍淇℃伅
    """
    if USE_SIMPLE_MONITOR:
        # 浣跨敤绠€鍖栫増鐩戞帶
        system_info = monitor.get_system_info()
        
        # 鑾峰彇缁勪欢鍔犺浇鐘舵€?        if USE_FAST_STARTER:
            load_status = "宸插畬鎴? if is_components_loaded() else "鍔犺浇涓?
            loading_info = get_loading_status() if not is_components_loaded() else {}
        else:
            load_status = "宸插畬鎴? if components_loaded else "鍔犺浇涓?
            loading_info = {}
        
        # 鏋勫缓鍝嶅簲
        response = {
            "status": system_info["status"],
            "system": system_info["system"],
            "process": system_info["process"],
            "load_status": load_status,
            "requests": system_info["requests"],
            "timestamp": datetime.now().isoformat()
        }
        
        # 娣诲姞缁勪欢鍔犺浇璇︽儏
        if loading_info:
            response["loading"] = loading_info
            
        return response
    else:
        # 浼犵粺鐩戞帶
        system_info = get_system_info()
        health_data = get_component_health()
        
        # 妫€鏌ョ粍浠剁姸鎬?        status = "healthy"
        for component, data in health_data["components"].items():
            if data["status"] == "error":
                status = "error"
                break
            elif data["status"] == "warning" and status != "error":
                status = "warning"
        
        # 鑾峰彇鍔犺浇鐘舵€?        load_status = "瀹屾垚" if components_loaded else "鍔犺浇涓?
        if not components_loaded and app_config.FAST_MODE:
            load_status += " (蹇€熸ā寮?"
        
        return {
            "status": status,
            "system": system_info,
            "load_status": load_status,
            "components": health_data["components"],
            "timestamp": health_data["timestamp"]
        }

# 鐩戞帶鎸囨爣鎺ュ彛
@app.get("/monitoring/metrics", tags=["鐩戞帶"])
async def system_metrics():
    """
    鑾峰彇绯荤粺鎬ц兘鎸囨爣鎺ュ彛
    """
    if USE_SIMPLE_MONITOR:
        return monitor.get_detailed_metrics()
    else:
        return get_performance_metrics()

# 閲嶇疆鐩戞帶鎸囨爣鎺ュ彛
@app.post("/monitoring/reset", tags=["鐩戞帶"])
async def reset_metrics():
    """
    閲嶇疆鎬ц兘缁熻鏁版嵁
    """
    if USE_SIMPLE_MONITOR:
        return monitor.reset_stats()
    else:
        # 娓呯悊璧勬簮
        result = cleanup_resources()
        # 閲嶇疆鍝嶅簲缂撳瓨
        response_cache.clear()
        return {
            "status": "success",
            "message": "绯荤粺璧勬簮鍜岀洃鎺ф寚鏍囧凡閲嶇疆",
            "details": result
        }

# 鏍硅矾鐢遍噸瀹氬悜鍒癠I
@app.get("/", include_in_schema=False)
async def root():
    """灏嗘牴璺緞璇锋眰閲嶅畾鍚戝埌浠〃鐩橀〉闈?""
    return RedirectResponse(url="/dashboard")

# 鍦ㄧ敓浜х幆澧冧腑浣跨敤姝や唬鐮佸惎鍔ㄦ湇鍔″櫒
if __name__ == "__main__":
    import argparse
    
    # 瑙ｆ瀽鍛戒护琛屽弬鏁?    parser = argparse.ArgumentParser(description="鍚姩娉拌开鏉櫤鑳藉鏈嶇郴缁?)
    parser.add_argument("--port", type=int, default=app_config.PORT, help="鏈嶅姟鍣ㄧ鍙?)
    parser.add_argument("--host", type=str, default="0.0.0.0", help="鏈嶅姟鍣ㄤ富鏈?)
    parser.add_argument("--reload", action="store_true", help="鍚敤鑷姩閲嶈浇")
    parser.add_argument("--fast", action="store_true", help="鍚敤蹇€熷惎鍔ㄦā寮?)
    parser.add_argument("--optimize", action="store_true", help="鍚敤鎬ц兘浼樺寲")
    parser.add_argument("--ui-priority", action="store_true", help="UI浼樺厛妯″紡")
    args = parser.parse_args()
    
    # 璁剧疆鐜鍙橀噺
    if args.fast:
        os.environ["FAST_MODE"] = "1"
    
    if args.ui_priority:
        os.environ["UI_PRIORITY"] = "1"
    
    if args.optimize:
        os.environ["OPTIMIZE_MEMORY"] = "1"
        os.environ["ENABLE_MONITORING"] = "1"
    
    # 閰嶇疆uvicorn閫夐」
    uvicorn_config = {
        "app": "app.main:app", 
        "host": args.host, 
        "port": args.port,
        "reload": args.reload,
        "log_level": "info" if not args.optimize else "warning"
    }
    
    # 浼樺寲妯″紡涓嬶紝璋冩暣worker閰嶇疆
    if args.optimize and not args.reload:
        import multiprocessing
        workers = min(multiprocessing.cpu_count(), 4)
        # 鍚姩澶氳繘绋嬫ā寮忛渶瑕佺鐢╮eload
        uvicorn_config["workers"] = workers
        print(f"鎬ц兘浼樺寲: 浣跨敤 {workers} 涓獁orker杩涚▼")
    
    # 鍚姩鏈嶅姟鍣?    print(f"鍚姩鏈嶅姟鍣?- 璁块棶鍦板潃: http://{args.host}:{args.port}")
    uvicorn.run(**uvicorn_config)
