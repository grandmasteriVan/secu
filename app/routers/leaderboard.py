from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc # Важливий імпорт для сортування

from app import models, schemas, database, security

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

@router.get(
    "/top", 
    response_model=list[schemas.LeaderboardEntry] # Повертаємо список записів
)
async def get_top_users(
    limit: int = 10,
    db: AsyncSession = Depends(database.get_db),
    # Для перегляду таблиці лідерів потрібна авторизація (перевірка токена)
    user: models.User = Depends(security.get_current_user) 
):
    """
    Повертає список ТОП-користувачів, відсортованих за XP.
    """
    
    # Створюємо запит:
    # 1. Вибрати всіх користувачів (models.User)
    # 2. Відсортувати за полем xp у порядку спадання (desc)
    # 3. Обмежити результат до 'limit' (за замовчуванням 10)
    stmt = (
        select(models.User)
        .order_by(desc(models.User.xp))
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    
    # Повертаємо об'єкти. FastAPI автоматично перетворить їх на схему LeaderboardEntry
    return result.scalars().all()