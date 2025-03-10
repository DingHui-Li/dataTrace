from fastapi import APIRouter, HTTPException, Body, Query, Request
from fastapi.responses import StreamingResponse, JSONResponse
from ..repositories.crawler_repository import CrawlerRepository
from ..repositories.analyze_repository import AnalyzeRepository
from ..services import CrawlerService
from typing import Dict, AsyncGenerator, Optional
from datetime import datetime
from pydantic import BaseModel
import app

class HarvestRequest(BaseModel):
    base_url: str
    cookie:str

router = APIRouter()
CrawlerRepository = CrawlerRepository()
AnalyzeRepository = AnalyzeRepository()
crawler_service=CrawlerService()

@router.post("/harvest/{platform}")
async def harvest_data(platform: str, data: HarvestRequest, request: Request):
    try:
        base_url = data.base_url
        cookie = data.cookie

        # 创建一个异步生成器函数来处理爬虫的流式输出
        async def event_generator() -> AsyncGenerator[str, None]:
            try:
                async for chunk in crawler_service.crawl_platform(platform, base_url, cookie):
                    if await request.is_disconnected():
                        # 客户端断开连接，停止采集
                        await crawler_service.stop_crawl()
                        break
                    yield chunk
            except Exception as e:
                # 发生异常时确保资源被清理
                await crawler_service.stop_crawl()
                raise e
        
        # 使用StreamingResponse返回流式响应，设置正确的响应头
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except Exception as e:
        # 发生异常时返回错误信息
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/data/stats")
async def get_platform_stats():
    try:
        stats = CrawlerRepository.query_platform_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/data/clear")
async def get_platform_stats():
    try:
        flag = CrawlerRepository.clear_all_data()
        flag2 = AnalyzeRepository.clear_all_data()
        return JSONResponse(content={'result':flag and flag2})
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/data/query")
async def query_results(
    platform: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    try:
        data = CrawlerRepository.query_results(
            platform,
            start_time=start_time,
            end_time=end_time,
            page=page,
            page_size=page_size
        )
        try:
            return JSONResponse(content=data)
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/aiconfig")
async def getAIConfig(config: dict):
    try:
        app.global_AI_config=config['config']
        print('global_AI_config=')
        print(app.global_AI_config)
        return {"status":"success"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )