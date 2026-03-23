import json
import time
from .base import BaseCrawler
import asyncio
from typing import Dict
import aiohttp
from ...models.crawler_config import CrawlResult
import re

class TiebaCrawler(BaseCrawler):
    def __init__(self, base_url: str = '', cookie: str = ''):
        super().__init__(base_url, cookie)
        self._should_stop = False
        self._user_un = ''

    async def stop_crawl(self):
        """停止爬虫任务"""
        self._should_stop = True

    async def _get_user_un(self, session):
        """从用户主页获取un参数"""
        try:
            url = self.base_url
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                html = await response.text()
                # 查找PageData.current_page_uname
                match = re.search( r"PageData\.current_page_uname\s*=\s*'([^']*)'", html)
                if match:
                    return match.group(1)
                return None
        except Exception as e:
            print(f'获取用户un失败: {str(e)}')
            return None

    async def crawl(self) -> Dict:
        yield json.dumps({
            'status': 'processing',
            'current': 0,
            'total': 0,
            'message': '开始获取贴吧数据'
        }, ensure_ascii=False) + "\n"

        try:
            page = 1
            total_items = 0
            current_index = 0
            all_items = []
            loadMore=True
            
            async with aiohttp.ClientSession() as session:
                # 首先获取用户的un
                self._user_un = await self._get_user_un(session)
                if not self._user_un:
                    yield json.dumps({
                        'status': 'error',
                        'message': '无法获取用户un参数'
                    }, ensure_ascii=False) + "\n"
                    return

                while loadMore:
                    if self._should_stop:
                        raise Exception('爬虫已停止')
                        break
                    # 使用获取到的un构建API请求URL
                    api_url = f"https://tieba.baidu.com/home/get/getthread?un={self._user_un}&pn={page}&ie=utf8"

                    # 发送请求获取数据
                    async with session.get(api_url) as response:
                        if response.status != 200:
                            yield json.dumps({
                                'status': 'error',
                                'message': f'请求失败: HTTP {response.status}'
                            }, ensure_ascii=False) + "\n"
                            return
                        
                        data = await response.json()
                        # 确保data是一个字典
                        if not isinstance(data, dict):
                            yield json.dumps({
                                'status': 'error',
                                'message': f'API返回的数据格式不正确: {data}'
                            }, ensure_ascii=False) + "\n"
                            return
                        if "error" in data and data['error']!='成功':
                            yield json.dumps({
                                'status': 'error',
                                'message': f'API请求失败: {data["error"]}'
                            }, ensure_ascii=False) + "\n"
                            return
                            
                        # 安全地获取thread_list
                        thread_list = data.get('data', {})
                        if isinstance(thread_list, list):
                            threads = thread_list
                        else:
                            threads = thread_list.get('thread_list', [])
                        
                        if not threads:
                            break
                        
                        # 处理当前页的帖子数据
                        for thread in threads:
                            url=f"https://tieba.baidu.com/p/{thread.get('thread_id', '')}"
                            if self.exists(url):
                                loadMore=False
                                break
                            current_index += 1
                            total_items = current_index
                            
                            # 解析帖子数据
                            content_item = {
                                'platform': 'tieba',
                                'title': thread.get('title', ''),
                                'content': thread.get('content', ''),
                                'images': [],  # API返回的数据中可能包含图片信息，需要根据实际返回格式调整
                                'create_time': int(thread.get('create_time', '')),
                                'location': '',
                                'url': url,
                                'type': 'post'
                            }
                            
                            # 创建爬取结果
                            result = CrawlResult(
                                platform='tieba',
                                title=content_item['title'],
                                content=content_item['content'],
                                images=content_item['images'],
                                create_time=content_item['create_time'],
                                location=content_item['location'],
                                url=content_item['url'],
                                type=content_item['type']
                            )
                            all_items.append(result)
                            
                            # 发送进度信息
                            yield json.dumps({
                                'status': 'processing',
                                'current': current_index,
                                'total': total_items,
                            }, ensure_ascii=False) + "\n"
                    
                    page += 1
                    # 添加延时避免请求过快
                    await asyncio.sleep(1)
            
            # 批量保存所有爬取的数据
            if all_items:
                await self.save_content(all_items)
            
            # 发送完成状态
            yield json.dumps({
                'status': 'complete',
                'current': total_items,
                'total': total_items,
                'success': True
            }, ensure_ascii=False) + "\n"
            
        except Exception as e:
            error_message = f'获取贴吧数据失败: {str(e)}'
            print(error_message)
            yield json.dumps({
                'status': 'error',
                'message': error_message
            }, ensure_ascii=False) + "\n"
        finally:
            await self.close_browser()