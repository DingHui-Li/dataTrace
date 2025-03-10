from fastapi import APIRouter, HTTPException, Body, Query, Request
from fastapi.responses import StreamingResponse, JSONResponse
from ..services import AnalyzeService
from typing import Dict, AsyncGenerator, Optional
import json

router = APIRouter()
analyze_service=AnalyzeService()

@router.get("/analyze")
async def analyze(request: Request):
    try:
        async def event_generator() -> AsyncGenerator[str, None]:
            try:
                async for chunk in analyze_service.analyze_data():
                    if await request.is_disconnected():
                        # 客户端断开连接，停止分析
                        await analyze_service.stop_analyze()
                        break
                    yield json.dumps(chunk, ensure_ascii=False)+'\n'
            except Exception as e:
                # 发生异常时确保资源被清理
                await analyze_service.stop_analyze()
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
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/analyze/checkprogress")
async def checkProgress(request: Request):
    try:
        result = analyze_service.checkProgress()
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )