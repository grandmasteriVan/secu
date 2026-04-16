from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List # Виправлено: додано імпорт
from app import schemas, models, database, security

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/me", response_model=schemas.UserResponse)
async def get_me(current_user: models.User = Depends(security.get_current_user)):
    # Тепер цей маршрут доступний за адресою /api/dashboard/me
    return current_user

@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    # Приклад статистики
    return {
        "xp": current_user.xp,
        "role": current_user.role,
        "full_name": current_user.full_name
    }

@router.get("/summary", response_model=schemas.DashboardStats)
async def get_dashboard_summary(
    db: AsyncSession = Depends(database.get_db),
    user: models.User = Depends(security.get_current_user)
):
    # Кількість завершених курсів
    res_completed = await db.execute(
        select(func.count(models.UserCourse.id)).where(models.UserCourse.user_id == user.id)
    )
    completed_count = res_completed.scalar() or 0

    # Загальна кількість курсів у системі
    res_total = await db.execute(select(func.count(models.Course.id)))
    total_count = res_total.scalar() or 0

    # Розрахунок місця в рейтингу (ранг)
    res_rank = await db.execute(
        select(func.count(models.User.id)).where(models.User.xp > user.xp)
    )
    rank = (res_rank.scalar() or 0) + 1

    return {
        "xp": user.xp,
        "rank": rank,
        "completed_courses": completed_count,
        "total_courses": total_count,
        "recent_badges": []
    }
