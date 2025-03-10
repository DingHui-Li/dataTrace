from fastapi import APIRouter, HTTPException, Body, Query, Request
from fastapi.responses import StreamingResponse, JSONResponse
from ..services import ChartService
from typing import Dict, AsyncGenerator, Optional
import json

router = APIRouter()
chart_service=ChartService()
@router.get("/chart/alldata")
async def get_chart_data():
    try:
        result = chart_service.getData()
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/chart/ai")
async def get_chart_data(request: Request):
    
    try:
        async def event_generator() -> AsyncGenerator[str, None]:
            try:
                async for chunk in chart_service.aiAnalyze():
                    if await request.is_disconnected():
                        # 客户端断开连接，停止分析
                        chart_service.stop_analyze()
                        break
                    yield f"{json.dumps(chunk)}\n"
            except Exception as e:
                # 发生异常时确保资源被清理
                chart_service.stop_analyze()
                yield f"{json.dumps({'error': str(e)})}\n"
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