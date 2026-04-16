from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app import schemas, models, database, security

# Імпортуємо лімітер з main (або створюємо локально, якщо імпорт циклічний)
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/organizations", response_model=list[schemas.OrganizationRead])
async def get_organizations(db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Organization))
    return result.scalars().all()

@router.post("/register")
async def register(user_data: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    existing = await db.execute(select(models.User).where(models.User.email == user_data.email))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Користувач з таким Email вже існує")

    new_user = models.User(
        email=user_data.email,
        password_hash=security.get_password_hash(user_data.password),
        full_name=user_data.full_name,
        organization_id=user_data.organization_id,
        is_active=False
    )
    db.add(new_user)
    await db.commit()
    return {"message": "Реєстрація успішна! Очікуйте активації адміністратором."}

# ДОДАНО ДЛЯ БЕЗПЕКИ: Декоратор ліміту та параметр request
@router.post("/login")
@limiter.limit("5/minute") # Дозволяємо лише 5 запитів на хвилину
async def login(
    request: Request, # Обов'язково додайте цей параметр для slowapi!
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(database.get_db)
):
    stmt = select(models.User).where(models.User.email == form_data.username)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Невірний email або пароль")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Ваш акаунт ще не активовано")

    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/leaderboard", response_model=list[schemas.UserLeaderboard])
async def get_leaderboard(db: AsyncSession = Depends(database.get_db)):
    query = select(models.User).order_by(models.User.xp.desc()).limit(10)
    result = await db.execute(query)
    users = result.scalars().all()
    
    output = []
    for u in users:
        org_name = "Без організації"
        if u.organization_id:
            org = await db.get(models.Organization, u.organization_id)
            if org: org_name = org.name
        output.append({"full_name": u.full_name, "xp": u.xp, "organization": org_name})
    return output

@router.get("/me", response_model=schemas.UserRead)
async def get_me(
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    # Робимо свіжий запит до БД для поточного користувача
    # selectinload гарантує, що ми завантажимо організацію асинхронно
    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.organization))
        .where(models.User.id == current_user.id)
    )
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user
