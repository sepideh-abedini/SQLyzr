import asyncio
import getpass
import time
# from tqdm.asyncio import tqdm
import tqdm

import oracledb
from oracledb import InterfaceError, POOL_GETMODE_TIMEDWAIT


def exec_ora(sql: str):
    connection = oracledb.connect(
        user="system",
        password="sheep",
        dsn="localhost:1521/FREEPDB1")

    cursor = connection.cursor()

    cursor.execute(sql)

    connection.commit()
    connection.close()


class OraClient:
    def __init__(self):
        self.pool = oracledb.create_pool_async(user="system", password="sheep",
                                               dsn="localhost:1521/FREEPDB1",
                                               min=1, max=10, increment=1,
                                               )

    async def exec(self, sql):
        async with self.pool.acquire() as conn:
            with conn.cursor() as cursor:
                await cursor.execute(sql)
                # await cursor.executemany(sql, params)
                await conn.commit()
                try:
                    return await cursor.fetchall()
                except InterfaceError:
                    return None

    async def exec_batch(self, sqls):
        async with self.pool.acquire() as conn:
            with conn.cursor() as cursor:
                tasks = []
                for sql in tqdm.tqdm(sqls):
                    tasks.append(cursor.execute(sql))
                    # await cursor.execute(sql)
                    # await conn.commit()
                await asyncio.gather(*tasks)
                await conn.commit()

    async def exec_many(self, sql, params):
        async with self.pool.acquire() as conn:
            with conn.cursor() as cursor:
                    # tasks.append(cursor.execute(sql))
                await cursor.executemany(sql, params)
                    # await conn.commit()
                await conn.commit()

    async def close(self):
        await self.pool.close()
