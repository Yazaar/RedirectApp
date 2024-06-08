import psycopg
import asyncio
from . import entities

class DB_CONNECT_ERROR(Exception): pass

class Database:
    def __init__(self, connectionStr : str):
        self.__connectionStr = connectionStr
        self.__adb : psycopg.AsyncConnection = None
        self.__tryReconnectLock = asyncio.Lock()

    async def startup(self):
        if self.__adb is None or self.__adb.closed:
            errorMsg = ''
            try: self.__adb = await psycopg.AsyncConnection.connect(self.__connectionStr)
            except Exception as e:
                self.__adb = None
                errorMsg = ' ' + e.args[0]
            if self.__adb is None or self.__adb.closed: raise DB_CONNECT_ERROR('[DB] ERROR' + errorMsg)
            print('[DB] Connected')
            await self.__create_database()

    async def __try_reconnect(self):
        if self.__tryReconnectLock.locked():
            async with self.__tryReconnectLock:
                 if self.__adb is None or self.__adb.closed: raise SystemExit
                 return
        async with self.__tryReconnectLock:
            loop = asyncio.get_event_loop()
            loop.create_task(self.__try_reconnect())
            tries = 1
            while True:
                try:
                    print(f'Reconnect try {tries}')
                    await self.startup()
                    break
                except DB_CONNECT_ERROR as e:
                    print(f'Failed reconnect {tries}: {e.args[0]}')
                    if tries == 7: raise SystemError('[DB] Failed reaching database')
                    tries += 1
                    await asyncio.sleep(10)

    async def __create_database(self):
        while True:
            try:
                c = self.__adb.cursor()
                await c.execute('''CREATE TABLE IF NOT EXISTS redirects(
                                id BIGSERIAL PRIMARY KEY,
                                path TEXT NOT NULL,
                                type TEXT NOT NULL,
                                target TEXT NOT NULL
                                )''')
                await self.__adb.commit()
                await c.close()
                return
            except psycopg.OperationalError:
                await self.__try_reconnect()

    async def get_redirect_by_path(self, path: str):
        while True:
            try:
                c = self.__adb.cursor()
                await c.execute('SELECT id, path, type, target FROM redirects WHERE path = %s LIMIT 1', (path,))
                data = await c.fetchone()
                await c.close()
                if not data: return None
                return entities.Redirect(data[0], data[1], data[2], data[3])
            except psycopg.OperationalError:
                await self.__try_reconnect()

    async def get_redirect_by_id(self, rId: int):
        while True:
            try:
                c = self.__adb.cursor()
                await c.execute('SELECT id, path, type, target FROM redirects WHERE id = %s LIMIT 1', (rId,))
                data = await c.fetchone()
                await c.close()
                if not data: return None
                return entities.Redirect(data[0], data[1], data[2], data[3])
            except psycopg.OperationalError:
                await self.__try_reconnect()

    async def get_redirects(self):
        while True:
            try:
                c = self.__adb.cursor()
                await c.execute('SELECT id, path, type, target FROM redirects')
                data = await c.fetchall()
                await c.close()
                if not data: return []
                return [entities.Redirect(i[0], i[1], i[2], i[3]) for i in data]
            except psycopg.OperationalError:
                await self.__try_reconnect()

    async def set_redirect(self, rPath: str, rType: str, rTarget: str):
        existing = await self.get_redirect_by_path(rPath)
        if existing: return self.update_redirect(existing, rPath, rType, rTarget)
        while True:
            try:
                c = self.__adb.cursor()
                await c.execute('INSERT INTO redirects(path, type, target) VALUES(%s, %s, %s) RETURNING id', (rPath, rType, rTarget))
                last_id = await c.fetchone()
                await self.__adb.commit()
                await c.close()
                return entities.Redirect(last_id, rPath, rType, rTarget)
            except psycopg.OperationalError:
                await self.__try_reconnect()

    async def update_redirect(self, redirect: entities.Redirect, rPath: str, rType: str, rTarget: str):
        while True:
            try:
                c = self.__adb.cursor()
                await c.execute('UPDATE redirects SET path = %s, type = %s, target = %s WHERE id = %s', (rPath, rType, rTarget, redirect.id))
                await self.__adb.commit()
                await c.close()
                redirect.path = rPath
                redirect.target = rTarget
                redirect.type = rType
                return redirect
            except psycopg.OperationalError:
                await self.__try_reconnect()

    async def delete_redirect(self, redirect: entities.Redirect):
        while True:
            try:
                c = self.__adb.cursor()
                await c.execute('DELETE FROM redirects WHERE id = %s', (redirect.id,))
                await self.__adb.commit()
                await c.close()
                return
            except psycopg.OperationalError:
                await self.__try_reconnect()
