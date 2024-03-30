import aiomysql
from aiomysql import DictCursor

class Database:
    """
    Database class to manage the connection pool
    use aiomysql to create a connection pool
    """
    def __init__(self, host, port, user, password, db) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.pool = None

    async def start(self, loop) -> None:
            """
            Starts the database connection pool and creates the database if it doesn't exist.

            Args:
                loop (asyncio.AbstractEventLoop): The event loop to use for the connection pool.

            Returns:
                None
            """

            self.pool = await aiomysql.create_pool(
                host=self.host, port=self.port,
                user=self.user, password=self.password,
                loop=loop)
            
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(f"CREATE DATABASE IF NOT EXISTS {self.db} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

            self.pool.close()
            await self.pool.wait_closed()

            self.pool = await aiomysql.create_pool(
                host=self.host, port=self.port,
                user=self.user, password=self.password,
                db=self.db, loop=loop,charset='utf8mb4')

    async def stop(self) -> None:
        """
        close the connection pool
        """
        self.pool.close()
        await self.pool.wait_closed()

    async def execute(self, queries, args=None) -> None:
        """
        Executes the given SQL queries with optional arguments.

        Args:
            queries : The SQL queries to execute. now the arg type can be list or str
            args optional: The arguments to pass to the queries. Defaults to None. 
            args should be as long as queries or absolutely a None, can't be shorter than queries.

        Returns:
            None

        Raises:
            Any exceptions raised by the underlying database driver.

        """
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                if type(queries) != list:
                    queries = [queries]
                    args = [args]
                for i, query in enumerate(queries):
                    await cur.execute(query, args[i] if args else None)
                await conn.commit()

    async def fetch(self, query, args=None):
            """
            Executes the given query with optional arguments and returns all the results.

            Args:
                query (str): The SQL query to execute.
                args (tuple, optional): The arguments to pass to the query. Defaults to None.

            Returns:
                list: A list of tuples representing the fetched results.
            """
            async with self.pool.acquire() as conn:
                async with conn.cursor(DictCursor) as cur:
                    await cur.execute(query, args)
                    result = await cur.fetchall()
                    return result if result else []
