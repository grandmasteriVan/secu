from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base
from app.routers import auth, dashboard, chat, simulations, admin, leaderboard, courses
from app.routers import certs
from contextlib import asynccontextmanager

# ДОДАНО ДЛЯ БЕЗПЕКИ: Імпорти slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request

limiter = Limiter(key_func=get_remote_address)

async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# Створення таблиць при старті (Для MVP. У продакшені використовуйте Alembic)
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="SecuLearn API", lifespan=lifespan)

# ДОДАНО ДЛЯ БЕЗПЕКИ: Підключення лімітера до додатку
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS (Дозволяє фронтенду звертатися до бекенду)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["seculearn.com.ua"], # Змініть на домен вашого сайту в продакшені
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключення роутерів
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(leaderboard.router)
app.include_router(admin.router)
app.include_router(courses.router)
app.include_router(chat.router)
app.include_router(certs.router)


@app.get("/")
def root():
    return {"message": "SecuLearn AI Backend is running"}

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Автоматичне створення таблиць у БД
        await conn.run_sync(Base.metadata.create_all)
