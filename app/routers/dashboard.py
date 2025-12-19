from fastapi import APIRouter, Depends
from app import schemas, models, security

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=schemas.DashboardStats)
async def get_dashboard_stats(user: models.User = Depends(security.get_current_user)):
    """
    Генерує статистику для головного екрану користувача.
    """
    
    # 1. Логіка розрахунку рівня ризику
    # Чим більше XP (знань), тим менший ризик злому
    if user.xp < 100:
        risk = "Критичний 🔴"
        risk_msg = "Пройдіть базовий курс!"
    elif user.xp < 300:
        risk = "Середній 🟡"
        risk_msg = "Ввімкніть 2FA"
    elif user.xp < 800:
        risk = "Низький 🟢"
        risk_msg = "Продовжуйте навчання"
    else:
        risk = "Захищено 🛡️"
        risk_msg = "Ви експерт!"

    # 2. Розрахунок прогресу (Припустимо, мета — 1000 XP)
    MAX_XP = 1000
    progress = int((user.xp / MAX_XP) * 100)
    if progress > 100: progress = 100

    # 3. Імітація кількості курсів (наприклад, кожні 200 XP = 1 курс)
    courses_done = user.xp // 200

    return {
        "total_xp": user.xp,
        "risk_level": risk,
        "progress_percent": progress,
        "courses_completed": courses_done,
        "next_goal": risk_msg
    }