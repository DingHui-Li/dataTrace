from typing import Dict
from pydantic import BaseModel

class CrawlResult(BaseModel):
    """爬取结果统一格式"""
    platform: str  # 平台名称
    title:str
    content: str   # 内容
    images: list   # 图片列表
    create_time: int  # 创建时间
    location: str    # 位置信息
    url: str         # 原文链接
    type: str         # 类型