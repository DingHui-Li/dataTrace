import json
from collections import defaultdict
from ..models.analyze import Analyze
from ..repositories.analyze_repository import AnalyzeRepository
from ..repositories.crawler_repository import CrawlerRepository
from datetime import datetime
from openai import OpenAI
import app

CrawlerRepository = CrawlerRepository()
class AnalyzeService:
    def __init__(self):
        self.analyze_repository = AnalyzeRepository()
        self._stop_analysis = False
        self.openaiClient = None

    def initOpenAI(self):
        if self.openaiClient:
            return
        config=app.global_AI_config
        if config:
            self.api_key = config['api_key']
            self.api_base = config['api_base']
            self.model_config = config['model']['summary']
            # 配置openai客户端
            self.openaiClient=OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
    def checkProgress(self):
        dateList=defaultdict(int)
        page = 1
        total_items = 0
        processed_items=0
        unanalyzed_count=0
        while True:
            rawData = CrawlerRepository.query_results(page=page)
            total_items=rawData['total']
            if total_items==0:
                return {
                    'total':0,
                    'curent':0,
                    'percentage': 0
                }
            for data in rawData['list']:
                date = datetime.fromtimestamp(data['create_time']).strftime('%Y-%m-%d')
                dateList[date]+=1
                processed_items+=1
            page+=1
            if processed_items >= total_items:
                    break
        for date,count in dateList.items():
            if not self.analyze_repository.exists(date):
                unanalyzed_count+=1
        return {
            'total':len(dateList),
            'curent':len(dateList)-unanalyzed_count,
            'percentage': round(((len(dateList)-unanalyzed_count) / len(dateList)) * 100, 2)
        }


    async def analyze_data(self):
        try:
            self._stop_analysis = False
            page = 1
            processed_items = 0
            daily_data = defaultdict(list)  # 用于临时存储每天的数据
            total_items = 0
            analysis_result={}
            total_tokens=0

            # 第一步：收集所有数据并按日期分组
            while True and not self._stop_analysis:
                rawData = CrawlerRepository.query_results(page=page)
                total_items = rawData['total']

                for data in rawData['list']:
                    date = datetime.fromtimestamp(data['create_time']).strftime('%Y-%m-%d')
                    daily_data[date].append(data)
                    processed_items += 1

                page += 1
                if processed_items >= total_items:
                    break

                yield {
                    'status': 'processing',
                    'message': '正在获取数据...',
                    'progress': {
                        'current': processed_items,
                        'total': total_items,
                        'percentage': round((processed_items / total_items) * 100, 2)
                    }
                }

            # 第二步：分析每天的数据
            analyzed_count = 0
            total_days = len(daily_data)
            yield {
                'status': 'processing',
                'message': f'开始分析数据...',
                'progress': {
                    'current': 0,
                    'total': total_days,
                    'percentage': round((analyzed_count / total_days) * 100, 2)
                }
            }

            for date, data_list in daily_data.items():
                if self.analyze_repository.exists(date):
                    analyzed_count+=1
                    continue
                if self._stop_analysis:
                    raise
                    break

                try:
                    combined_content = "\n".join([str(data) for data in data_list])
                    analysis_result = await self.analyze_text(combined_content)
                    
                    analyze = Analyze(
                        date=date,
                        create_time=int(datetime.now().timestamp()),
                        summary=analysis_result['result']['summary'],
                        emotion_score=analysis_result['result']['emotion_score'],
                        emotion_desc=analysis_result['result']['emotion_desc'],
                        topic=analysis_result['result']['topic'],
                        keywords=analysis_result['result']['keywords'],
                        urls='\n'.join([data['url'] for data in data_list])
                    )
                    await self.analyze_repository.save(analyze)
                    
                    analyzed_count += 1
                    total_tokens+=analysis_result['total_tokens']
                    yield {
                        'status': 'processing',
                        'message': f'正在分析 {date} 的数据...',
                        'data':analyze.__dict__,
                        'model':analysis_result['model'],
                        'total_tokens':total_tokens,
                        'progress': {
                            'current': analyzed_count,
                            'total': total_days,
                            'percentage': round((analyzed_count / total_days) * 100, 2)
                        }
                    }
                except Exception as e:
                    raise ValueError(f'分析 {date} 的数据时发生错误: {str(e)}')

            yield {
                'status': 'completed',
                'message': f'分析完成，共处理 {total_items} 条数据，涵盖{total_days} 天',
                'model':analysis_result['model'],
                'total_tokens':total_tokens,
                'progress': {
                    'current': total_days,
                    'total': total_days,
                    'percentage': 100
                }
            }

        except Exception as e:
            yield {
                'status': 'error',
                'message': f'分析数据时发生错误: {str(e)}',
                'progress': {
                    'current': 0,
                    'total': 0,
                    'percentage': 0
                }
            }

    async def stop_analyze(self):
        """停止当前的分析任务"""
        self._stop_analysis = True

    async def analyze_text(self, text: str) -> dict:
        """使用deepseek API分析文本内容"""
        try:
            self.initOpenAI()
            # 调用API进行文本摘要
            response = self.openaiClient.chat.completions.create(
                model=self.model_config['name'],
                messages=[
                    {
                        "role": "system", 
                        "content": """
                        请分析用户在不同社交平台发布的内容,如果有多条数据则合在一起,生成以下内容:
                        摘要(注意地理位置),分析出真实想法;
                        情绪评分(0-100)和情绪描述;
                        主题分类,从[瞬时情绪,价值观沉淀,压力释放,群体记忆,文化共鸣,争议反思,技术赋能,娱乐技艺,生存智慧,地理脉搏,生态网络,气候韵律,人化自然界面,隐喻自然符号]中选择一个或多个,以/分隔;
                        关键词,只要内容中关键词,以/分隔;
                        并以json格式生成结果;
                        例子:{
                            "summary":"",
                            "emotion_score":90,
                            "emotion_desc":"积极",
                            "topic":"",
                            "keywords":""}
                        """
                    },
                    {"role": "user", "content": f"以下是内容：\n{text}"}
                ],
                temperature=self.model_config['temperature']
            )

            # 提取摘要内容
            result = response.choices[0].message.content.strip()
            print(result)
            result = json.loads(result.replace('```json', '').replace('```', ''))
            return {
                "result":result,
                "model":response.model,
                "total_tokens":response.usage.total_tokens
            }
        except Exception as e:
            raise Exception(f'文本分析失败: {str(e)}')