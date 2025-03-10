import json
import time
import aiohttp
import asyncio
from typing import Dict
from .base import BaseCrawler
from datetime import datetime
from ...models.crawler_config import CrawlResult
from urllib.parse import urlparse, parse_qs

class WeiboCrawler(BaseCrawler):
    def __init__(self, base_url: str = '', cookie: str = ''):
        super().__init__(base_url, cookie)
        self.user_id = self._extract_user_id(base_url)
        self._should_stop = False

    async def stop_crawl(self):
        """停止爬虫任务"""
        self._should_stop = True

    def _extract_user_id(self, url: str) -> str:
        """从微博URL中提取用户ID

        Args:
            url: 微博用户主页URL

        Returns:
            str: 用户ID
        """
        if not url:
            raise ValueError('base_url不能为空')

        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')

        # 处理 /u/数字ID 格式
        if len(path_parts) >= 2 and path_parts[0] == 'u':
            return path_parts[1]
        
        # 如果是其他格式的URL，抛出异常
        raise ValueError('无法从URL中提取用户ID，请确保URL格式正确')

    async def crawl(self) -> Dict:
        yield json.dumps({
            'status': 'processing',
            'current': 0,
            'total': 0,
            'message': '开始获取微博数据'
        }, ensure_ascii=False) + "\n"

        try:
            # 初始化数据
            all_items = []
            page = 1
            total_items = 0
            current_index = 0
            has_more = True
            loadMore=True

            # 创建HTTP会话
            async with aiohttp.ClientSession() as session:
                while has_more and loadMore:
                    if self._should_stop:
                        raise Exception('爬虫已停止')
                        break
                    # 构建API请求URL和参数
                    api_url = 'https://weibo.com/ajax/statuses/mymblog'
                    params = {
                        'uid': self.user_id,  # 需要从配置中获取用户ID
                        'page': page,
                        'feature': 0
                    }
                    headers = {
                        'Cookie': self.cookie,
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }

                    # 发送API请求
                    async with session.get(api_url, params=params, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # 解析返回的数据
                            if 'data' in data and 'list' in data['data']:
                                items = data['data']['list']
                                if not items:  # 如果没有更多数据
                                    has_more = False
                                    continue

                                for item in items:
                                    current_index += 1
                                    
                                    # 提取内容
                                    content = item.get('text_raw', '')
                                    create_time = self._parse_weibo_time(item.get('created_at', ''))
                                    url = f"https://weibo.com/{self.user_id}/{item.get('mblogid', '')}"
                                    if self.exists(url):
                                        loadMore=False
                                        break
                                    
                                    # 提取图片
                                    media_list = []
                                    pics = item.get('pics', [])
                                    for pic in pics:
                                        if 'large' in pic:
                                            media_list.append(pic['large']['url'])
                                    
                                    # 构建内容项
                                    content_item = {
                                        'platform': 'weibo',
                                        'title': content[:50] if content else '',
                                        'content': content,
                                        'images': media_list,
                                        'create_time': create_time,
                                        'location':'' if item.get('title') else item.get('region_name', ''),
                                        'url': url,
                                        'type':item.get('source') or (item.get('title') or {}).get('text') or 'post'
                                    }
                                    
                                    all_items.append(content_item)
                                    total_items = len(all_items)
                                    
                                    # 发送进度
                                    yield json.dumps({
                                        'status': 'processing',
                                        'current': current_index,
                                        'total': total_items,
                                    }, ensure_ascii=False) + "\n"
                            
                            page += 1
                            # 添加延时避免请求过快
                            await asyncio.sleep(1)
                        else:
                            raise Exception(f'API请求失败: HTTP {response.status}')

            # 批量保存所有内容
            for item in all_items:
                result = CrawlResult(
                    platform='weibo',
                    title=item['title'],
                    content=item['content'],
                    images=item['images'],
                    create_time=item['create_time'],
                    location=item['location'],
                    url=item['url'],
                    type=item['type']
                )
                await self.save_content(result)

            # 发送完成状态
            yield json.dumps({
                'status': 'complete',
                'current': total_items,
                'total': total_items,
                'success': True
            }, ensure_ascii=False) + "\n"

        except Exception as e:
            error_message = f'获取微博数据失败: {str(e)}'
            print(error_message)
            yield json.dumps({
                'status': 'error',
                'message': error_message
            }, ensure_ascii=False) + "\n"

    def _parse_weibo_time(self, time_str: str) -> int:
        """将微博时间字符串转换为时间戳

        Args:
            time_str: 微博时间字符串，格式如 'Wed Sep 04 17:03:07 +0800 2024'

        Returns:
            int: 时间戳
        """
        try:
            # 解析时间字符串
            dt = datetime.strptime(time_str, '%a %b %d %H:%M:%S %z %Y')
            # 转换为时间戳
            return int(dt.timestamp())
        except Exception as e:
            print(f'时间解析失败: {str(e)}')
            return 0