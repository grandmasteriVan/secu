from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import schemas, models, database, security

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=schemas.Token)
async def register(user_data: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    # Перевірка існування
    existing = await db.execute(select(models.User).where(models.User.email == user_data.email))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        email=user_data.email,
        password_hash=security.get_password_hash(user_data.password),
        full_name=user_data.full_name
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = security.create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.User).where(models.User.email == form_data.username))
    user = result.scalars().first()

    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(security.get_current_user)):
    return current_user

# ЕНДПОІНТ: Оновлення профілю
@router.put("/profile", response_model=schemas.UserResponse)
async def update_profile(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(security.get_current_user),
    db: AsyncSession = Depends(database.get_db)
):
    """
    Дозволяє користувачу змінити своє ім'я.
    """
    # Оновлюємо поле
    current_user.full_name = user_update.full_name
    
    # Зберігаємо в БД
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return current_user