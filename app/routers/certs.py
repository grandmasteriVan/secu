from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import models, database, security
from app.services.pdf_service import create_certificate

router = APIRouter(prefix="/certificates", tags=["Certificates"])

@router.get("/download/{course_id}")
async def download_cert(
    course_id: int,
    db: AsyncSession = Depends(database.get_db),
    user: models.User = Depends(security.get_current_user)
):
    # Перевірка проходження курсу
    res = await db.execute(
        select(models.UserCourse).where(
            models.UserCourse.user_id == user.id,
            models.UserCourse.course_id == course_id
        )
    )
    if not res.scalars().first():
        raise HTTPException(status_code=403, detail="Курс ще не завершено")

    c_res = await db.execute(select(models.Course).where(models.Course.id == course_id))
    course = c_res.scalars().first()
    
    name = user.full_name or "Користувач"
    filename = f"cert_{user.id}_{course_id}.pdf"
    file_path = create_certificate(name, course.title, filename)

    return FileResponse(
        path=file_path,
        filename=f"Certificate_{course.id}.pdf",
        media_type='application/pdf'
    )
