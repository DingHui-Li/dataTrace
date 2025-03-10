import sqlite3
from typing import List, Optional
from ..models.analyze import Analyze
from datetime import datetime

class AnalyzeRepository:
    def __init__(self):
        self.db_path = 'data-trace.db'
        self.tb='base_analyze'
        self._init_db()

    def _init_db(self):
        """初始化数据库连接和表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建分析结果表
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.tb} (
            date TEXT PRIMARY KEY,
            create_time TIMESTAMP,
            summary TEXT,
            emotion_score INTEGER,
            emotion_desc TEXT,
            topic TEXT,
            urls TEXT,
            keywords TEXT
        )
        """)
        
        conn.commit()
        conn.close()
    def exists(self, date: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # 先检查记录是否存在
        cursor.execute(f"SELECT date FROM {self.tb} WHERE date = ?", (date,))
        return cursor.fetchone()

    async def save(self, analyze: Analyze,update=False) -> Analyze:
        """保存单条分析结果，如果记录已存在则更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # 先检查记录是否存在
        cursor.execute(f"SELECT date FROM {self.tb} WHERE date = ?", (analyze.date,))
        exists = cursor.fetchone()
        
        if exists and update:
            # 更新已存在的记录
            cursor.execute(f"""
            UPDATE {self.tb} 
            SET create_time = ?, summary = ?, emotion_score = ?,emotion_desc = ?,topic = ?, urls = ?,keywords=?
            WHERE date = ?
            """, (analyze.create_time, analyze.summary,analyze.emotion_score,analyze.emotion_desc,analyze.topic,analyze.urls,analyze.keywords,analyze.date))
        else:
            # 插入新记录
            cursor.execute(f"""
            INSERT INTO {self.tb} (date, create_time, summary,emotion_score,emotion_desc,topic,urls,keywords)
            VALUES (?, ?, ?, ?,?,?,?,?)
            """, (analyze.date, analyze.create_time, analyze.summary,analyze.emotion_score,analyze.emotion_desc,analyze.topic, analyze.urls,analyze.keywords))
            
        conn.commit()
        conn.close()
        return analyze

    def getAllResult(self) -> list[dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {self.tb}")
        rows = cursor.fetchall()
        conn.close()
        list = []
        for row in rows:
            list.append({
                'date': row[0],
                'create_time': row[1],
                'summary': row[2],
                'emotion_score': row[3],
                'emotion_desc': row[4],
                'topic': row[5],
                'urls': row[6],
                'keywords': row[7],
            })
        return list
    def clear_all_data(self) -> bool:
        """清空所有分析结果数据
        Returns:
            bool: 操作是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f"DELETE FROM {self.tb}")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"清空数据失败: {str(e)}")
            return False