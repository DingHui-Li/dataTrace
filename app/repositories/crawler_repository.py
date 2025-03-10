import sqlite3
from typing import Dict
from datetime import datetime
from ..models.crawler_config import  CrawlResult

class CrawlerRepository:
    def __init__(self):
        self.db_path = 'data-trace.db'
        self._init_db()

    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建爬取结果表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS crawl_results (
            platform TEXT,
            title TEXT,
            content TEXT,
            images TEXT,
            create_time INTEGER,
            location TEXT,
            url TEXT PRIMARY KEY,
            type TEXT
        )
        """)

        conn.commit()
        conn.close()
    def exists(self, url: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # 先检查记录是否存在
        cursor.execute(f"SELECT url FROM crawl_results WHERE url = ?", (url,))
        return cursor.fetchone()

    def save_results(self, results: list[CrawlResult]) -> bool:
        """保存爬取结果"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for result in results:
                cursor.execute("""
                INSERT INTO crawl_results 
                (platform, title, content, images, create_time, location, url, type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.platform,
                    result.title,
                    result.content,
                    ','.join(result.images),
                    result.create_time,
                    result.location,
                    result.url,
                    result.type
                ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存爬取结果失败: {str(e)}")
            return False

    def query_results(self, platform: str = None, start_time: int = None, end_time: int = None, page: int = 1, page_size: int = 20) -> dict:
        """查询爬取结果
        Args:
            platform: 平台名称
            start_time: 开始时间戳
            end_time: 结束时间戳
            page: 页码，从1开始
            page_size: 每页数量
        Returns:
            dict: 包含分页信息和结果列表的字典
                {
                    'page': 当前页码,
                    'size': 每页大小,
                    'total': 总记录数,
                    'items': 爬取结果列表
                }
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 构建基础查询条件
            base_where = "WHERE 1=1"
            params = []

            if platform:
                base_where += " AND platform = ?"
                params.append(platform)

            if start_time is not None:
                base_where += " AND create_time >= ?"
                params.append(start_time)

            if end_time is not None:
                base_where += " AND create_time <= ?"
                params.append(end_time)

            # 查询总记录数
            count_query = f"SELECT COUNT(*) FROM crawl_results {base_where}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]

            # 查询分页数据
            query = f"SELECT * FROM crawl_results {base_where}"

            query += " ORDER BY create_time DESC"
            query += " LIMIT ? OFFSET ?"
            params.extend([page_size, (page - 1) * page_size])

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            results = []
            for row in rows:
                result = {
                    'platform':row[0],
                    'title':row[1],
                    'content':row[2],
                    'images':row[3].split(',') if row[3] else [],
                    'create_time':int(row[4]),
                    'location':row[5],
                    'url':row[6],
                    'type':row[7]
                }
                results.append(result)

            return {
                'page': page,
                'size': page_size,
                'total': total,
                'list': results
            }
        except Exception as e:
            print(f"查询爬取结果失败: {str(e)}")
            return {
                'page': page,
                'size': page_size,
                'total': 0,
                'list': []
            }
    def query_platform_stats(self) -> Dict[str, int]:
        """查询各平台的数据总量
        Returns:
            Dict[str, int]: 平台数据总量统计，key为平台名称，value为数据总量
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = "SELECT platform, COUNT(*) as count FROM crawl_results GROUP BY platform"
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()

            stats = {}
            for row in rows:
                stats[row[0]] = row[1]

            return stats
        except Exception as e:
            print(f"查询平台数据统计失败: {str(e)}")
            return {}
    def clear_all_data(self) -> bool:
        """清空所有爬取结果数据
        Returns:
            bool: 操作是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM crawl_results")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"清空数据失败: {str(e)}")
            return False
    def _parse_weibo_time(self, time_str: str) -> int:
        """将微博时间字符串转换为时间戳

        Args:
            time_str: 微博时间字符串，格式如 'Wed Sep 04 17:03:07 +0800 2024'

        Returns:
            int: 时间戳
        """
        # 解析时间字符串
        dt = datetime.strptime(time_str, '%a %b %d %H:%M:%S %z %Y')
        # 转换为时间戳
        return int(dt.timestamp())