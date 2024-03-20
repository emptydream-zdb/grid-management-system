import aiomysql

class Database:
    def __init__(self, host, port, user, password, db):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.pool = None

    async def start(self):
        self.pool = await aiomysql.create_pool(
            host=self.host, port=self.port,
            user=self.user, password=self.password,
            db=self.db)

    async def stop(self):
        self.pool.close()
        await self.pool.wait_closed()

    async def execute(self, query, args=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                await conn.commit()

    async def fetch(self, query, args=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                return await cur.fetchall()
