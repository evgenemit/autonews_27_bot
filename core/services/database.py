import asyncpg


class Database:
    
    def __init__(self, pool_connect: asyncpg.pool.Pool) -> None:
        self.connect = pool_connect

    async def execute(self, text: str) -> None:
        await self.connect.execute(text)

    async def fetch(self, text: str) -> list:
        return await self.connect.fetch(text)

    async def fetchrow(self, text: str) -> list:
        return await self.connect.fetchrow(text)
