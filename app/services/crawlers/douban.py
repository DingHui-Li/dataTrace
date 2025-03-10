import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
from .base import BaseCrawler
from typing import Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ...models.crawler_config import CrawlResult

class DoubanCrawler(BaseCrawler):
    async def crawl_page(self, url: str, page_type: str) -> set:
        processed_urls = set()
        try:
            self._browser.get(url)
            time.sleep(3)
            
            while True:
                soup = BeautifulSoup(self._browser.page_source, 'html.parser')
                items = []
                
                if page_type == 'notes':
                    items = soup.find_all('div', class_='note-container')
                    for item in items:
                        header = item.find('div', class_='note-header-container')
                        title_elem = header.find('a', title=True) if header else None
                        url = title_elem['href'] if title_elem else ''
                        if url and url not in processed_urls:
                            processed_urls.add(url)
                            content = {
                                'platform': 'douban',
                                'title': title_elem['title'] if title_elem else '',
                                'content': item.find('div', id=lambda x: x and x.endswith('_short')).text.strip() if item.find('div', id=lambda x: x and x.endswith('_short')) else '',
                                'images': [],  # 暂时为空列表，后续可以添加图片解析
                                'create_time': int(datetime.strptime(header.find('span', class_='pub-date').text.strip().split('\n')[0].strip(), '%Y-%m-%d %H:%M:%S').timestamp()) if header and header.find('span', class_='pub-date') else 0,
                                'location': '',
                                'url': url,
                                'type': 'note'
                            }
                            yield json.dumps(content, ensure_ascii=False) + "\n"
                
                elif page_type == 'statuses':
                    items = soup.find_all('div', class_='status-item')
                    for item in items:
                        content_elem = item.find('div', class_='status-saying')
                        created_at_span = item.find('span', class_='created_at')
                        url = ''
                        if created_at_span and created_at_span.find('a'):
                            url = created_at_span.find('a').get('href', '')
                        if url and url not in processed_urls:
                            processed_urls.add(url)
                            create_time = created_at_span['title'] if created_at_span else ''
                            # 获取图片URL
                            images = []
                            photo_imgs = item.find_all('div', class_='photo-img')
                            for photo_img in photo_imgs:
                                img_tag = photo_img.find('img')
                                if img_tag and img_tag.get('src'):
                                    images.append(img_tag['src'])
                            content = {
                                'platform': 'douban',
                                'title': content_elem.text.strip()[:50] if content_elem else '',
                                'content': content_elem.text.strip() if content_elem else '',
                                'images': images,
                                'create_time': int(datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S').timestamp()) if create_time else 0,
                                'location': '',
                                'url': url,
                                'type': 'status'
                            }
                            yield json.dumps(content, ensure_ascii=False) + "\n"
                
                # 查找下一页按钮
                next_link = soup.find('span', class_='next').find('a') if soup.find('span', class_='next') else None
                if not next_link:
                    break
                
                # 点击下一页
                next_url = next_link['href']
                self._browser.execute_script("arguments[0].click();", self._browser.find_element(By.CSS_SELECTOR, 'span.next a'))
                time.sleep(3)  # 等待新页面加载
                
        except Exception as e:
            print(f'解析{page_type}页面失败: {str(e)}')

    async def crawl(self) -> Dict:
        await self.init_browser()
        yield json.dumps({
            'status': 'processing',
            'current': 0,
            'total': 0,
            'message': '初始化浏览器成功'
        }, ensure_ascii=False) + "\n"
        if not self._browser:
            yield json.dumps({
                'status': 'error',
                'message': '初始化浏览器失败'
            }, ensure_ascii=False) + "\n"
            return

        try:
            # 创建数组存储所有数据
            all_items = []
            
            # 访问主页面
            self._browser.get(self.base_url)
            time.sleep(3)  # 等待页面加载
            if self.cookie and not self._cookie_added:
                await self._add_cookies()
            
            # 使用BeautifulSoup解析页面并获取日记链接
            soup = BeautifulSoup(self._browser.page_source, 'html.parser')
            notes_link = soup.find('a', href=lambda x: x and '/notes' in x)
            if not notes_link:
                raise Exception('未找到日记链接')
            notes_url = notes_link['href']
            
            # 爬取日记页面
            notes_count = 0
            async for item in self.crawl_page(notes_url, 'notes'):
                if item['status']=='error':
                    yield json.dumps(item, ensure_ascii=False) + "\n"
                    return
                all_items.append(json.loads(item))
                notes_count += 1
                if notes_count % 10 == 0:  # 每处理10个项目发送一次进度
                    yield json.dumps({
                        'status': 'processing',
                        'current': len(all_items),
                        'total': len(all_items),
                        'message': f'已处理{len(all_items)}个项目'
                    }, ensure_ascii=False) + "\n"
            
            # 访问主页面并获取广播链接
            self._browser.get(self.base_url)
            time.sleep(3)  # 等待页面加载
            
            # 使用BeautifulSoup解析页面并获取广播链接
            soup = BeautifulSoup(self._browser.page_source, 'html.parser')
            statuses_link = soup.find('a', href=lambda x: x and '/statuses' in x)
            if not statuses_link:
                raise Exception('未找到广播链接')
            statuses_url = statuses_link['href']
            
            # 爬取广播页面
            statuses_count = 0
            async for item in self.crawl_page(statuses_url, 'statuses'):
                if item['status']=='error':
                    yield json.dumps(item, ensure_ascii=False) + "\n"
                    return
                all_items.append(json.loads(item))
                statuses_count += 1
                if statuses_count % 10 == 0:  # 每处理10个项目发送一次进度
                    yield json.dumps({
                        'status': 'processing',
                        'current': len(all_items),
                        'total': len(all_items),
                        'message': f'已处理{len(all_items)}个项目'
                    }, ensure_ascii=False) + "\n"
            
            # 批量保存所有内容
            for item in all_items:
                result = CrawlResult(
                    platform='douban',
                    title=item['title'],
                    content=item['content'],
                    images=item['images'],
                    create_time=item['create_time'],
                    location=item['location'],
                    url=item['url'],
                    type=item['type']
                )
                await self.save_content(result)

            total_items = len(all_items)
            # 发送完成状态
            yield json.dumps({
                'status': 'complete',
                'current': total_items,
                'total': total_items,
                'success': True
            }, ensure_ascii=False) + "\n"
            
        except Exception as e:
            error_message = f'解析豆瓣页面失败: {str(e)}'
            print(error_message)
            yield json.dumps({
                'status': 'error',
                'message': error_message
            }, ensure_ascii=False) + "\n"
        finally:
            await self.close_browser()