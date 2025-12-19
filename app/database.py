from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings

# Створення асинхронного двигуна
engine = create_async_engine(settings.DATABASE_URL, echo=False)
Base = declarative_base()

# Фабрика сесій
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Залежність (Dependency) для отримання сесії в роутерах
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session