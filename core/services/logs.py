import aiofiles
from datetime import datetime
from environs import Env


async def add_logs(text):
    env = Env()
    env.read_env('.env')
    if env.bool('LOGS'):
        async with aiofiles.open('logs.txt', mode='a') as f:
            await f.write(f'[ {datetime.now()} ] {text}\n')
