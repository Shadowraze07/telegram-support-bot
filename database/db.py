from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.models import Base

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

# expire_on_commit=False решает проблему MissingGreenlet
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def db_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)