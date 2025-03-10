from typing import Dict, AsyncGenerator
import json

class CrawlerService:
    def __init__(self):
        self.current_crawler = None

    async def crawl_platform(self, platform: str, base_url: str, cookie: str = '') -> AsyncGenerator[str, None]:
        """统一的平台爬取方法
        
        Args:
            platform: 平台名称
            base_url: 目标URL
            cookie: 平台cookie
            
        Yields:
            str: JSON格式的爬取结果
        """
        try:
            # 根据平台选择对应的爬虫实现
            self.current_crawler = self._get_crawler(platform, base_url, cookie)
            if not self.current_crawler:
                yield json.dumps({
                    'status': 'error',
                    'message': f'不支持的平台: {platform}'
                }, ensure_ascii=False)
                return

            async for chunk in self.current_crawler.crawl():
                yield chunk+'\n'

        except Exception as e:
            yield json.dumps({
                'status': 'error',
                'message': f'爬取过程发生错误: {str(e)}'
            }, ensure_ascii=False)

    def _get_crawler(self, platform: str, base_url: str, cookie: str = ''):
        """获取对应平台的爬虫实例
        
        Args:
            platform: 平台名称
            base_url: 目标URL
            cookie: 平台cookie
            
        Returns:
            BaseCrawler: 爬虫实例
        """
        from .crawlers.weibo import WeiboCrawler
        from .crawlers.zhihu import ZhihuCrawler
        from .crawlers.tieba import TiebaCrawler
        from .crawlers.douban import DoubanCrawler

        crawlers = {
            'weibo': WeiboCrawler,
            'zhihu': ZhihuCrawler,
            'tieba': TiebaCrawler,
            'douban': DoubanCrawler
        }

        crawler_class = crawlers.get(platform)
        if crawler_class:
            return crawler_class(base_url, cookie)
        return None

    async def stop_crawl(self):
        """停止当前正在运行的爬虫任务"""
        if self.current_crawler:
            if hasattr(self.current_crawler, 'close_browser'):
                await self.current_crawler.close_browser()
            if hasattr(self.current_crawler, 'stop_crawl'):
                await self.current_crawler.stop_crawl()
            self.current_crawler = None