from ..repositories.analyze_repository import AnalyzeRepository
import json
from openai import OpenAI
import app

class ChartService:
    def __init__(self):
        self._stop_analysis = False
        self.analyze_repository = AnalyzeRepository()
        self.openaiClient = None
    
    def initOpenAI(self):
        if self.openaiClient:
            return
        config=app.global_AI_config
        if config:
            self.api_key = config['api_key']
            self.api_base = config['api_base']
            self.model_config = config['model']['analysis']
            # 配置openai客户端
            self.openaiClient=OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )

    def stop_analyze(self):
        """停止当前的分析任务"""
        self._stop_analysis = True
        
    def getData(self) -> list[dict]:
        return self.analyze_repository.getAllResult()

    async def aiAnalyze(self):
        data = self.analyze_repository.getAllResult()
        # 按时间排序数据
        sorted_data = sorted(data, key=lambda x: x['date'])
        
        # 准备分析文本
        max_text_length = 50000  # 每批次的最大文本长度
        current_batch = []
        current_length = 0
        batches = []
        
        for item in sorted_data:
            item_text = f"时间: {item['date']}\n概要: {item['summary']}\n\n关键词: {item['keywords']}\n\n"
            item_length = len(item_text)
            
            if current_length + item_length > max_text_length and current_batch:
                batches.append(current_batch)
                current_batch = []
                current_length = 0
            
            current_batch.append(item)
            current_length += item_length
        
        if current_batch:
            batches.append(current_batch)
        
        total_batches = len(batches)
        try:
            self.initOpenAI()
            
            # 分批处理数据
            batch_results = []
            for batch_index, batch_data in enumerate(batches):
                # 准备当前批次的分析文本
                batch_text = ""
                for item in batch_data:
                    batch_text += f"时间: {item['date']}\n"
                    batch_text += f"概要: {item['summary']}\n\n"
                    batch_text += f"关键词: {item['keywords']}\n\n"
                
                # 调用API进行文本分析
                response = self.openaiClient.chat.completions.create(
                    model=self.model_config['name'],
                    messages=[
                        {
                            "role": "system", 
                            "content": f"""
                            以下内容是用户在不同社交平台发布的内容(第{batch_index + 1}/{total_batches}批)，注意时间跨度,
                            从时间轴概览,深度需求洞察,主题分类,平台分布,里程碑,时空轨迹,情绪波动,隐性情绪,用户画像,潜在发展预测,异常数据点解读,
                            总结等方面进行分析:
                            """
                        },
                        {"role": "user", "content": f"以下是内容：\n{batch_text}"}
                    ],
                    stream=True,
                    temperature=self.model_config['temperature']
                )
                
                # 流式处理响应
                current_batch_result = ""
                for chunk in response:
                    if self._stop_analysis:
                        response.close()
                        break
                    if chunk.usage:
                        usage=chunk.usage.__dict__
                    if chunk.choices[0].delta.reasoning_content:
                        content = chunk.choices[0].delta.reasoning_content
                        current_batch_result += content
                        yield {
                                'analysis': content,
                                "type":"reasoning",
                                "model":chunk.model,
                                "usage":usage,
                                'is_final': False,
                                'batch_progress': {
                                    'current': batch_index + 1,
                                    'total': total_batches
                                }
                            }
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        current_batch_result += content
                        yield {
                                'analysis': content,
                                "type":"result",
                                "model":chunk.model,
                                "usage":usage,
                                'is_final': False,
                                'batch_progress': {
                                    'current': batch_index + 1,
                                    'total': total_batches
                                }
                            }
                
                if self._stop_analysis:
                    break
                    
                batch_results.append(current_batch_result)
            
            # 生成总结
            if not self._stop_analysis and len(batch_results)>1:
                summary_text = "\n".join(batch_results)
                summary_response = self.openaiClient.chat.completions.create(
                    model=self.model_config['name'],
                    messages=[
                        {
                            "role": "system", 
                            "content": """
                            请对以下所有分析结果进行全局总结，需要包含以下方面：
                            1. 时间跨度概述
                            2. 主要事件和里程碑
                            3. 情感趋势分析
                            4. 关键主题分布
                            5. 用户画像演变
                            6. 重要发现和建议
                            """
                        },
                        {"role": "user", "content": f"以下是各批次的分析结果：\n{summary_text}"}
                    ],
                    stream=True,
                    temperature=self.model_config['temperature']
                )
                
                for chunk in summary_response:
                    if self._stop_analysis:
                        summary_response.close()
                        break
                    if chunk.usage:
                        usage=chunk.usage.__dict__
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        yield {
                            'analysis': content,
                            "type":"final_summary",
                            "model":chunk.model,
                            "usage":usage,
                            'is_final': False,
                            'batch_progress': {
                                'current': total_batches,
                                'total': total_batches
                            }
                        }
            
            # 返回最终结果
            if not self._stop_analysis:
                yield {
                    'analysis':'全部数据分析完成',
                    'is_final': True,
                    'batch_progress': {
                        'current': total_batches,
                        'total': total_batches
                    }
                }
                
        except Exception as e:
            raise Exception(f'文本分析失败: {str(e)}')