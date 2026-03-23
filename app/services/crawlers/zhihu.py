import json
import time
from datetime import datetime
from typing import Dict
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import BaseCrawler
from ...models.crawler_config import CrawlResult

class ZhihuCrawler(BaseCrawler):
    def __init__(self, base_url: str, cookie: str = None):
        super().__init__(base_url, cookie)
        # 从base_url中提取user_id
        self.user_id = self.base_url.split('/people/')[-1].split('/')[0] if '/people/' in self.base_url else ''
        if not self.user_id:
            raise ValueError('无法从base_url中提取用户ID')
        self._should_stop = False

    async def stop_crawl(self):
        """停止爬虫任务"""
        self._should_stop = True

    async def crawl(self) -> Dict:
        yield json.dumps({
            'status': 'processing',
            'current': 0,
            'total': 0,
            'message': '开始获取数据'
        }, ensure_ascii=False) + "\n"

        try:
            page_num = 1
            processed_items = set()
            all_items = []
            total_items = 0
            current_index = 0

            # 初始化WebDriver
            self._browser = await self.get_browser()
            wait = WebDriverWait(self._browser, 10)

            # 访问用户主页
            self._browser.get(self.base_url)

            # 等待页面加载完成
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ProfileMain-header')))

            # 移除遮挡内容的Modal弹窗
            self._browser.execute_script("document.querySelector('.Modal-wrapper')?.remove();")

            # 切换到回答标签页
            tabs = self._browser.find_element(By.CLASS_NAME, 'ProfileMain-header').find_elements(By.CLASS_NAME, 'Tabs-item')
            if len(tabs) >= 2:
                tabs[1].click()
                time.sleep(3)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'List-item')))
            loadMore=True

            while loadMore:
                if self._should_stop:
                    raise Exception('爬虫已停止')
                    break
                # 获取当前页面的HTML内容
                html_content = self._browser.page_source
                soup = BeautifulSoup(html_content, 'html.parser')
                answer_items = soup.find_all('div', class_='List-item')
                print(len(answer_items))

                if not answer_items:
                    break

                for answer_item in answer_items:
                    try:
                        # 获取问题链接和ID
                        question_link = answer_item.find('h2', class_='ContentItem-title').find('a')
                        if not question_link:
                            continue
                        
                        question_url = question_link.get('href', '')
                        if not question_url.startswith('//www.zhihu.com/question/'):
                            continue

                        # 提取问题ID和回答ID
                        url_parts = question_url.replace('//www.zhihu.com/question/', '').split('/answer/')
                        if len(url_parts) >= 2:
                            question_id = url_parts[0]
                            answer_id = url_parts[1]
                        else:
                            continue

                        if answer_id in processed_items:
                            continue

                        url=f"https://www.zhihu.com/question/{question_id}/answer/{answer_id}"
                        if self.exists(url):
                            loadMore=False
                            break

                        processed_items.add(answer_id)
                        current_index += 1
                        total_items = len(processed_items)

                        # 获取问题标题
                        title = question_link.get_text(strip=True)

                        # 获取回答内容
                        content_div = answer_item.find('span', class_='RichText')
                        content = content_div.get_text(strip=True) if content_div else ''

                        # 获取创建时间
                        time_meta = answer_item.find('meta', itemprop='dateCreated')
                        time_str = time_meta.get('content', '') if time_meta else ''
                        try:
                            timestamp = int(datetime.fromisoformat(time_str.replace('Z', '+00:00')).timestamp())
                        except:
                            timestamp = int(time.time())

                        content_item = {
                            'platform': 'zhihu',
                            'title': title,
                            'content': content,
                            'images': [],  # 暂不处理图片
                            'create_time': timestamp,
                            'location': '',
                            'url': url,
                            'type': '回答'
                        }

                        all_items.append(content_item)

                        yield json.dumps({
                            'status': 'processing',
                            'current': current_index,
                            'total': total_items,
                        }, ensure_ascii=False) + "\n"
                    except Exception as e:
                        raise e
                        continue

                # 查找下一页按钮
                try:
                    # 先检查是否存在下一页按钮
                    next_buttons = self._browser.find_elements(By.CLASS_NAME, 'PaginationButton-next')
                    if not next_buttons:
                        print('没有找到下一页按钮，爬取结束')
                        break
                    
                    next_button = next_buttons[0]
                    if 'disabled' in next_button.get_attribute('class'):
                        print('已到达最后一页')
                        break
                        
                    self._browser.execute_script("arguments[0].click();", self._browser.find_element(By.CLASS_NAME, 'PaginationButton-next'))
                    # 等待页面内容更新
                    time.sleep(2)  # 增加等待时间，确保页面加载完成
                    
                except Exception as e:
                    print(e)
                    raise e
                    break
            
            # 批量保存所有内容
            for item in all_items:
                result = CrawlResult(
                    platform='zhihu',
                    title=item['title'],
                    content=item['content'],
                    images=item['images'],
                    create_time=item['create_time'],
                    location=item['location'],
                    url=item['url'],
                    type=item['type']
                )
                await self.save_content(result)
            
            # 发送完成进度和数据
            yield json.dumps({
                'status': 'complete',
                'current': total_items,
                'total': total_items,
                'success': True,
                'message': f'共处理 {total_items} 条内容'
            }, ensure_ascii=False) + "\n"
            
        except Exception as e:
            error_message = f'获取知乎数据失败: {str(e)}'
            print(error_message)
            yield json.dumps({
                'status': 'error',
                'message': error_message
            }, ensure_ascii=False) + "\n"
        finally:
            await self.close_browser()