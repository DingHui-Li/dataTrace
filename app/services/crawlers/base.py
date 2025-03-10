import json
import time
from typing import Dict
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from ...models.crawler_config import CrawlResult
from ...repositories.crawler_repository import CrawlerRepository

class BaseCrawler:
    def __init__(self, base_url: str = '', cookie: str = ''):
        self.base_url = base_url
        self.cookie = cookie
        self._browser = None
        self._cookie_added = False
        self.repository = CrawlerRepository()

    async def save_content(self, result: CrawlResult | list[CrawlResult]):
        """保存爬取的内容到数据库
        
        Args:
            result: 爬取结果对象或对象列表
        """
        if isinstance(result, list):
            return self.repository.save_results(result)
        return self.repository.save_results([result])

    def exists(self,url:str):
        return self.repository.exists(url)

    async def init_browser(self):
        try:
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-infobars')
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')
            
            if self.cookie:
                options.add_experimental_option('prefs', {
                    'profile.default_content_settings.cookies': 1
                })
                self._cookie_added = False  # 重置cookie添加状态
            
            try:
                service = Service()
                self._browser = webdriver.Chrome(service=service, options=options)
                
                print('Chrome浏览器初始化成功')
                return True
            except Exception as e:
                print(f'Chrome浏览器初始化失败，错误信息: {str(e)}')
                return False
        except Exception as e:
            print(f'初始化浏览器失败，详细错误: {str(e)}')
            return False

    async def close_browser(self):
        if self._browser:
            try:
                self._browser.quit()
            except:
                pass
            self._browser = None

    async def fetch_page(self, url: str) -> str:
        try:
            # 如果有cookie且未添加，则先添加cookie
            if self.cookie and not self._cookie_added:
                await self._add_cookies()
            
            response = await self._browser.get(url)
            return response.text
        except Exception as e:
            print(f'获取页面失败: {str(e)}')
            return ''
    
    async def _add_cookies(self):
        """添加cookie到浏览器"""
        try:
            if not self.cookie:
                return
                
            # 确保浏览器已经打开一个页面
            if not self._browser.current_url.startswith('http'):
                self._browser.get('about:blank')
                
            # 解析并添加cookie
            cookie_list = self.cookie.split(';')
            for cookie_str in cookie_list:
                if not cookie_str.strip():
                    continue
                    
                try:
                    name, value = cookie_str.strip().split('=', 1)
                    # 从base_url提取域名
                    from urllib.parse import urlparse
                    domain = urlparse(self.base_url).netloc
                    if domain.startswith('www.'):
                        domain = domain[4:]
                    if not domain.startswith('.'):
                        domain = '.' + domain
                    
                    self._browser.add_cookie({
                        'name': name.strip(),
                        'value': value.strip(),
                        'domain': domain
                    })
                except Exception as e:
                    print(f'添加cookie失败: {str(e)}')
                    continue
                    
            self._cookie_added = True
            print('Cookie添加成功')
            # 刷新页面以确保cookie生效
            if self._browser.current_url.startswith('http'):
                self._browser.refresh()
                time.sleep(2)  # 等待页面刷新完成
        except Exception as e:
            print(f'设置cookie过程中出错: {str(e)}')
            self._cookie_added = False

    async def crawl(self) -> Dict:
        raise NotImplementedError('子类必须实现此方法')
    
    async def get_browser(self):
        """初始化并返回浏览器实例"""
        if not self._browser:
            await self.init_browser()
        return self._browser