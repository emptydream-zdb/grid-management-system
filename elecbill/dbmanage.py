import aiomysql

import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "..")) # 添加父级目录到系统路径,以解决模块导入问题

from utils import Database


class DB(Database):
    def __init__(self, host, port, user, password, name):
        super().__init__(host, port, user, password, name)

    async def init_table(self):
        """
        Create the table if it doesn't exist
        """
        query = ["""
        CREATE TABLE IF NOT EXISTS elecbill (
            id VARCHAR(20) NOT NULL PRIMARY KEY,
            bill DOUBLE(16,2) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS data_day (
            uid VARCHAR(20) NOT NULL PRIMARY KEY,
            id VARCHAR(20) NOT NULL,
            data DOUBLE(16,2) NOT NULL,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS data_hour (
            uid VARCHAR(20) NOT NULL PRIMARY KEY,
            id VARCHAR(20) NOT NULL,
            data DOUBLE(16,2) NOT NULL,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
        """]
        await self.execute(query)
