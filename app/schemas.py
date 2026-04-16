from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional, List, Any

class SimResultCreate(BaseModel):
    sim_type: str
    score: int
    details: Optional[str] = None

class SimResultResponse(BaseModel):
    id: int
    sim_type: str
    score: int
    message: str = "Результат збережено"

    class Config:
        from_attributes = True

# --- Організації ---
class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationRead(OrganizationBase):
    id: int
    class Config:
        from_attributes = True

# --- Користувачі ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_id: Optional[int] = None

class UserUpdate(BaseModel):
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    xp: int
    organization_id: Optional[int] = None
    is_active: bool
    
    class Config:
        from_attributes = True

class UserLeaderboard(BaseModel):
    full_name: str
    xp: int
    organization: str = None
    class Config:
        from_attributes = True

# --- Статистика Дашборду (DashboardStats) ---
class DashboardStats(BaseModel):
    xp: int
    rank: int
    completed_courses: int
    total_courses: int
    recent_badges: List[str]

# --- Курси ---
class QuizQuestion(BaseModel):
    question: str
    options: List[str]

class CourseList(BaseModel):
    id: int
    title: str
    description: str
    xp_reward: int
    is_completed: bool = False
    class Config:
        from_attributes = True

class CourseDetail(CourseList):
    content: str
    badge_url: Optional[str] = None
    questions: List[QuizQuestion]

# --- Результати та Чат ---
class SubmitResult(BaseModel):
    success: bool
    message: str
    xp_gained: int

class CourseSubmit(BaseModel):
    answers: List[int]

class ChatMessage(BaseModel):
    # Виправлено з text на message, щоб відповідати запиту з фронтенду
    message: str

class ChatResponse(BaseModel):
    reply: str

class Badge(BaseModel):
    name: str
    image_url: str

    class Config:
        from_attributes = True

class LeaderboardEntry(BaseModel):
    full_name: str
    xp: int
    organization: Optional[str] = None

    class Config:
        from_attributes = True

class UserRead(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    total_xp: int = 0
    role: str
    organization: Optional[str] = None # Залишаємо str, але додаємо логіку нижче

    @field_validator("organization", mode="before")
    @classmethod
    def transform_org(cls, v):
        # Якщо v - це об'єкт моделі Organization, беремо його ім'я
        if v and hasattr(v, "name"):
            return v.name
        return v

    model_config = ConfigDict(from_attributes=True)