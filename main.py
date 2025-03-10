from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import os
import argparse
import webbrowser
import threading
import time

parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument("--env", default="prod")
# 忽略所有未知参数
args, unknown = parser.parse_known_args()

from app import create_app

# 创建应用实例
app = create_app()
port=8348

# 只在生产环境下挂载前端静态文件
if args.env != "dev":
    # 使用绝对路径挂载静态文件
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_path = os.path.join(base_dir, "frontend", "dist")
    index_path = os.path.join(dist_path, "index.html")
    
    # 先配置静态文件路由
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def serve_index():
        return FileResponse(index_path)

def open_browser():
    # 等待服务器启动
    time.sleep(2)
    # 根据环境选择正确的URL
    url = "http://localhost:5173" if args.env == "dev" else f"http://localhost:{port}"
    webbrowser.open(url)

if __name__ == "__main__":
    import subprocess
    
    # 在开发环境下启动前端开发服务器
    frontend_process = None
    if args.env == "dev":
        frontend_process = subprocess.Popen(
            "npm run dev",
            shell=True,
            cwd="frontend"
        )
    
    # 创建一个线程来打开浏览器
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        if(args.env == "dev"):
            print("开发环境启动")
            uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
        else:
            print("生产环境启动")
            uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
    finally:
        # 确保在程序退出时关闭前端进程
        if frontend_process:
            frontend_process.terminate()
