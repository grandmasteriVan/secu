import shutil
import os
import json
from uuid import uuid4
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session
from app import schemas, models, database, security
from app.security import get_password_hash
from ..database import get_db
#from .. import models, dependencies
router = APIRouter(prefix="/admin", tags=["Admin"])

UPLOAD_DIR = "static/badges"
os.makedirs(UPLOAD_DIR, exist_ok=True)

from pydantic import BaseModel, EmailStr

class AdminCreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "user" # За замовчуванням 'user'

# Перевірка прав адміна
def check_admin(user: models.User = Depends(security.get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized") # Тепер це всередині if
    return user

# НОВИЙ ЕНДПОІНТ: Отримати список всіх користувачів
@router.get("/users", response_model=list[schemas.UserResponse])
async def get_all_users(
    admin: models.User = Depends(check_admin),
    db: AsyncSession = Depends(database.get_db)
):
    """
    Повертає список всіх користувачів системи. Вимагає прав адміністратора.
    """
    result = await db.execute(select(models.User))
    users = result.scalars().all()
    return users

@router.post("/assign_sim")
async def assign_simulation(
    data: schemas.AdminAssignSim,
    admin: models.User = Depends(check_admin),
    db: AsyncSession = Depends(database.get_db)
):
    # Тут може бути логіка відправки email або створення запису в БД про призначення


    return {"status": "assigned", "detail": f"Simulation {data.sim_type} assigned to user {data.user_id}"}

class AdminCreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "user" # За замовчуванням 'user'

# 2. Додаємо POST обробник
@router.post("/users", status_code=201)
async def create_user_by_admin(
    user_data: AdminCreateUserRequest,
    admin: models.User = Depends(check_admin), # Тільки адмін може це робити
    db: AsyncSession = Depends(database.get_db)
):
    # А. Перевіряємо, чи існує вже такий email
    existing_user = await db.execute(select(models.User).where(models.User.email == user_data.email))
    if existing_user.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Б. Хешуємо пароль (ОБОВ'ЯЗКОВО!)
    hashed_pwd = get_password_hash(user_data.password)

    # В. Створюємо користувача з потрібною роллю
    new_user = models.User(
        email=user_data.email,
        password_hash=hashed_pwd,
        role=user_data.role, # Записуємо роль, яку передав адмін
        full_name="", # Можна залишити пустим
        xp=0
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": f"User {new_user.email} created with role {new_user.role}"}

@router.post("/courses", status_code=201)
async def create_course(
    title: str = Form(...),
    description: str = Form(...),
    content: str = Form(...),
    xp_reward: int = Form(...),
    questions_json: str = Form(...), # JSON рядок: [{"q":"...", "opts":["..."], "correct":0}, ...]
    badge_file: UploadFile = File(...),
    admin: models.User = Depends(check_admin),
    db: AsyncSession = Depends(database.get_db)
):
    # 1. Збереження бейджа
    # Генеруємо унікальне ім'я, щоб не було конфліктів
    file_ext = badge_file.filename.split('.')[-1]
    file_name = f"badge_{uuid4()}.{file_ext}"
    file_path = f"static/badges/{file_name}"
    
    # Створюємо папку якщо немає
    os.makedirs("static/badges", exist_ok=True)
    
    # Зберігаємо файл (асинхронно читаємо, синхронно пишемо - для MVP ок)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(badge_file.file, buffer)

    # 2. Парсинг питань
    try:
        quiz_data = json.loads(questions_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Невірний формат JSON для питань")

    # 3. Запис у БД
    new_course = models.Course(
        title=title,
        description=description,
        content=content,
        xp_reward=xp_reward,
        badge_image_url=f"/{file_path}", # Зберігаємо веб-шлях
        quiz_json=quiz_data # SQLAlchemy автоматично серіалізує JSON
    )

    db.add(new_course)
    await db.commit()
    await db.refresh(new_course)

    return {"status": "created", "course_id": new_course.id}