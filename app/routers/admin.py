import json, os
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app import schemas, models, database, security
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(security.get_current_admin)])

class OrgCreate(BaseModel):
    name: str

# --- ОРГАНІЗАЦІЇ ---
@router.get("/organizations", response_model=list[schemas.OrganizationRead])
async def list_orgs(db: AsyncSession = Depends(database.get_db)):
    res = await db.execute(select(models.Organization))
    return res.scalars().all()

@router.post("/organizations")
async def create_org(data: OrgCreate, db: AsyncSession = Depends(database.get_db)):
    new_org = models.Organization(name=data.name)
    db.add(new_org)
    await db.commit()
    return {"status": "ok"}

@router.delete("/organizations/{org_id}")
async def delete_org(org_id: int, db: AsyncSession = Depends(database.get_db)):
    org = await db.get(models.Organization, org_id)
    if org:
        await db.delete(org)
        await db.commit()
    return {"status": "deleted"}

# --- КОРИСТУВАЧІ ---
@router.get("/users", response_model=list[schemas.UserResponse])
async def get_users(db: AsyncSession = Depends(database.get_db)):
    res = await db.execute(select(models.User))
    return res.scalars().all()

@router.post("/users/{user_id}/activate")
async def activate_user(user_id: int, db: AsyncSession = Depends(database.get_db)):
    user = await db.get(models.User, user_id)
    if not user: raise HTTPException(404)
    user.is_active = True
    await db.commit()
    return {"message": "activated"}

# --- КУРСИ ---
@router.post("/courses")
async def create_course(
    title: str = Form(...),
    description: str = Form(...),
    content: str = Form(...),
    xp_reward: int = Form(...),
    questions_json: str = Form(...),
    badge_file: UploadFile = File(...),
    db: AsyncSession = Depends(database.get_db)
):
    file_ext = badge_file.filename.split('.')[-1]
    file_path = f"static/badges/badge_{uuid4()}.{file_ext}"
    os.makedirs("static/badges", exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(await badge_file.read())

    new_course = models.Course(
        title=title, description=description, content=content,
        xp_reward=xp_reward, badge_image_url=f"/{file_path}",
        quiz_json=json.loads(questions_json)
    )
    db.add(new_course)
    await db.commit()
    return {"status": "created"}
