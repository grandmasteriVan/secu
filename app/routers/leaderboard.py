from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sqlalchemy import select, desc, func # Важливий імпорт для сортування
from sqlalchemy.orm import selectinload

from app import models, schemas, database, security

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

@router.get("/top", response_model=list[schemas.UserRead]) # Переконайтеся, що response_model вказано
async def get_leaderboard(db: AsyncSession = Depends(database.get_db)):
    res = await db.execute(
        select(models.User)
        .options(selectinload(models.User.organization)) # ПРИМУСОВЕ ЗАВАНТАЖЕННЯ ОРГАНІЗАЦІЇ
        .order_by(models.User.total_xp.desc())
        .limit(10)
    )
    return res.scalars().all()
