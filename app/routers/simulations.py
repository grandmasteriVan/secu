from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, models, database, security

router = APIRouter(prefix="/simulations", tags=["Simulations"])

@router.post("/submit", response_model=schemas.SimResultResponse)
async def submit_result(res: schemas.SimResultCreate, 
                        user: models.User = Depends(security.get_current_user),
                        db: AsyncSession = Depends(database.get_db)):
    
    new_sim = models.SimulationResult(
        user_id=user.id,
        type=res.type,
        score=res.score,
        details=res.details
    )
    
    # Оновлення XP користувача
    user.xp += 100
    
    db.add(new_sim)
    db.add(user)
    await db.commit()
    await db.refresh(new_sim)
    return new_sim