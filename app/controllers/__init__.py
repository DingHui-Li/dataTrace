from fastapi import APIRouter
from .data_harvest import router as data_harvest_router
from .analyze import router as analyze_router
from .chart import router as chart_router

def register_routes(app):
    api_router = APIRouter(prefix="/api")
    
    # 注册各个模块的路由
    api_router.include_router(data_harvest_router, tags=["data_harvest"])
    api_router.include_router(analyze_router, tags=["analyze"])
    api_router.include_router(chart_router, tags=["chart"])
    
    # 将总路由注册到应用
    app.include_router(api_router)