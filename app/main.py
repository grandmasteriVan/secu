from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base
from app.routers import auth, dashboard, chat, simulations, admin, leaderboard, courses
from app.routers import certs
from contextlib import asynccontextmanager


# Створення таблиць при старті (Для MVP. У продакшені використовуйте Alembic)
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="SecuLearn API", lifespan=lifespan)


# CORS (Дозволяє фронтенду звертатися до бекенду)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Змініть на домен вашого сайту в продакшені
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключення роутерів
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(chat.router)
app.include_router(simulations.router)
app.include_router(admin.router)
app.include_router(certs.router)
app.include_router(leaderboard.router)
app.include_router(courses.router)


@app.get("/")
def root():
    return {"message": "SecuLearn AI Backend is running"}
