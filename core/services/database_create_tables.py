import asyncio
import asyncpg
from environs import Env


from database import Database


async def create_tables() -> None:
    env = Env()
    env.read_env('.env')

    pool_connect = await asyncpg.create_pool(env.str('DB_URI'))
    db = Database(pool_connect)
    await db.execute(
        """
        DROP TABLE IF EXISTS admins CASCADE;
        CREATE TABLE admins (
            id serial primary key,
            user_id VARCHAR(10) UNIQUE NOT NULL
        );
        """
    )

    await pool_connect.close()


if __name__ == '__main__':
    asyncio.run(create_tables())
