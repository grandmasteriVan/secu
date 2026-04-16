from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, models, database, security

router = APIRouter(prefix="/simulations", tags=["Simulations"])

@router.post("/submit", response_model=schemas.SimResultResponse)
async def submit_result(
    res: schemas.SimResultCreate, 
    user: models.User = Depends(security.get_current_user), 
    db: AsyncSession = Depends(database.get_db)
):
    # Захист: перевірка чи не надсилав користувач результат занадто часто (наприклад, раз на хвилину)
    last_sim = await db.execute(
        select(models.SimulationResult)
        .where(models.SimulationResult.user_id == user.id)
        .order_by(models.SimulationResult.id.desc())
    )
    last_res = last_sim.scalars().first()
    
    # Спрощена логіка анти-флуду
    # if last_res and (datetime.now() - last_res.created_at) < timedelta(minutes=1):
    #    raise HTTPException(429, "Занадто часто. Зачекайте хвилину.")

    new_sim = models.SimulationResult(
        user_id=user.id,
        type=res.type,
        score=res.score,
        details=res.details
    )
    
    # Нараховуємо XP тільки за реальні досягнення (приклад)
    xp_to_add = min(res.score, 100) 
    user.xp += xp_to_add
    
    db.add(new_sim)
    db.add(user)
    await db.commit()
    await db.refresh(new_sim)
    return new_sim
