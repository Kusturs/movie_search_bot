import os
import asyncpg
import app.database.models as md
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = f"{os.getenv('DATABASE_URL')}/{md.DB_NAME}"


async def create_pool():
	return await asyncpg.create_pool(DATABASE_URL)


async def set_user(user_id):
	pool = await create_pool()
	async with pool.acquire() as connection:
		await connection.execute(
			'''
				INSERT INTO search_history (user_id, search_history)
				VALUES ($1, $2)
				ON CONFLICT (user_id) DO NOTHING
			''', user_id, '[]'
			)
	await pool.close()
