from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import database, models, security, schemas
from app.courses_data import COURSES_DB
from pydantic import BaseModel
from app.schemas import Badge

router = APIRouter(prefix="/courses", tags=["Courses"])

# Схеми для відповіді
class QuizData(BaseModel):
    question: str
    options: list[str]

class CourseList(BaseModel):
    id: int
    title: str
    description: str
    content: str
    xp_reward: int
    quiz: QuizData
    is_completed: bool = False

class CourseList(BaseModel):
    id: int
    title: str
    description: str
    xp_reward: int
    badge_name: str
    is_completed: bool

class CourseSubmit(BaseModel):
    success: bool
    message: str
    xp_gained: int
    badge_earned: str | None

# 1. Отримати список курсів
@router.get("/", response_model=list[schemas.CourseList])
async def get_courses(
    db: AsyncSession = Depends(database.get_db),
    user: models.User = Depends(security.get_current_user)
):
    result_user = await db.execute(select(models.UserCourse).where(models.UserCourse.user_id == user.id))
    completed_ids = {uc.course_id for uc in result_user.scalars().all()}

    result_courses = await db.execute(select(models.Course))
    db_courses = result_courses.scalars().all()

    return [
        {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "xp_reward": c.xp_reward,
            "is_completed": (c.id in completed_ids)
        } for c in db_courses
    ]

@router.get("/{course_id}", response_model=schemas.CourseDetail)
async def get_course_detail(
    course_id: int,
    db: AsyncSession = Depends(database.get_db),
    user: models.User = Depends(security.get_current_user)
):
    result = await db.execute(select(models.Course).where(models.Course.id == course_id))
    course = result.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не знайдено")

    res_comp = await db.execute(select(models.UserCourse).where(
        models.UserCourse.user_id == user.id, 
        models.UserCourse.course_id == course_id
    ))
    is_done = res_comp.scalars().first() is not None

    raw_questions = course.quiz_json or []
    formatted_questions = [
        {"question": q.get("question"), "options": q.get("options", [])} 
        for q in raw_questions
    ]

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "content": course.content,
        "xp_reward": course.xp_reward,
        "badge_url": course.badge_image_url or "",
        "questions": formatted_questions,
        "is_completed": is_done
    }

@router.post("/{course_id}/complete", response_model=schemas.SubmitResult)
async def complete_course(
    course_id: int,
    submission: schemas.CourseSubmit,
    db: AsyncSession = Depends(database.get_db),
    user: models.User = Depends(security.get_current_user)
):
    # 1. Отримуємо курс та правильні відповіді
    result = await db.execute(select(models.Course).where(models.Course.id == course_id))
    course = result.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не знайдено")

    quiz_data = course.quiz_json or []
    
    # 2. Перевірка відповідей
    if len(submission.answers) != len(quiz_data):
        return {"success": False, "message": "Надані не всі відповіді", "xp_gained": 0}

    for i, q in enumerate(quiz_data):
        if submission.answers[i] != q.get("correct"):
            return {
                "success": False, 
                "message": f"Помилка у питанні №{i+1}. Спробуйте ще раз!", 
                "xp_gained": 0
            }

    # 3. Якщо все вірно - оновлюємо прогрес
    # Перевіряємо, чи не проходив юзер цей курс раніше
    check_done = await db.execute(select(models.UserCourse).where(
        models.UserCourse.user_id == user.id, 
        models.UserCourse.course_id == course_id
    ))
    
    if not check_done.scalars().first():
        new_completion = models.UserCourse(user_id=user.id, course_id=course_id)
        user.xp += course.xp_reward
        db.add(new_completion)
        db.add(user)
        await db.commit()

    return {
        "success": True,
        "message": "Вітаємо! Ви успішно пройшли курс!",
        "xp_gained": course.xp_reward,
        "badge_earned": course.title
    }

@router.get("/my/badges")
async def get_my_badges(
    db: AsyncSession = Depends(database.get_db),
    user: models.User = Depends(security.get_current_user)
):
    result = await db.execute(
        select(models.Course)
        .join(models.UserCourse, models.UserCourse.course_id == models.Course.id)
        .where(models.UserCourse.user_id == user.id)
    )
    courses = result.scalars().all()
    return [{"name": c.title, "image_url": c.badge_image_url} for c in courses]