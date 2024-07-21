import os
import asyncpg
from asyncpg.exceptions import DuplicateDatabaseError, DuplicateTableError
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
DB_NAME = "history"
TABLE_NAME = "search_history"


async def create_database():
	conn = await asyncpg.connect(DATABASE_URL)
	try:
		await conn.execute(f'CREATE DATABASE {DB_NAME}')
	except DuplicateDatabaseError:
		print(f"Database {DB_NAME} already exists.")
	finally:
		await conn.close()


async def create_table():
	db_url_with_dbname = f"{DATABASE_URL}/{DB_NAME}"
	conn = await asyncpg.connect(db_url_with_dbname)
	try:
		await conn.execute(
		f'''
			CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
				user_id BIGINT PRIMARY KEY,
				search_history JSONB
            )
        '''
		)
	except DuplicateTableError:
		print(f"Table {TABLE_NAME} already exists.")
	finally:
		await conn.close()


async def main():
	await create_database()
	await create_table()
