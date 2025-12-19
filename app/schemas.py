from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- Auth ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: str
    xp: int
    full_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Simulations ---
class SimResultCreate(BaseModel):
    type: str  # 'phishing' or 'quiz'
    score: int
    details: Optional[str] = None

class SimResultResponse(SimResultCreate):
    id: int
    completed_at: datetime
    class Config:
        from_attributes = True

# --- Chat ---
class ChatMessage(BaseModel):
    text: str

class ChatResponse(BaseModel):
    reply: str

# --- Admin ---
class AdminAssignSim(BaseModel):
    user_id: int
    sim_type: str

# --- Dashboard Stats ---
class DashboardStats(BaseModel):
    total_xp: int
    risk_level: str          # Наприклад: "Високий", "Середній", "Низький"
    progress_percent: int    # 0-100
    courses_completed: int
    next_goal: str           # Текст наступної цілі

    #from pydantic import BaseModel, EmailStr

# --- Laderbord ---
class LeaderboardEntry(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    xp: int
    
    #class Config:
    #     Це дозволяє Pydantic працювати з моделями SQLAlchemy (models.User)
    #    from_attributes = True#/

# Клас для отримання даних при оновленні профілю
class UserUpdate(BaseModel):
    full_name: str

class Badge(BaseModel):
    name: str
    course: str

# курси

# Схема для відправки відповідей (тепер це список)
class CourseSubmit(BaseModel):
    answers: List[int] # Список індексів відповідей: [0, 2, 1]

# Це те, що ми ПОВЕРТАЄМО фронтенду
class SubmitResult(BaseModel):
    success: bool
    message: str
    xp_gained: int
    badge_earned: Optional[str] = None

# Допоміжна схема для відображення питань
class QuizQuestion(BaseModel):
    question: str
    options: List[str]

class CourseList(BaseModel):
    id: int
    title: str
    description: str
    xp_reward: int
    is_completed: bool
    # Прибираємо звідси content, badge_url та questions, 
    # бо вони потрібні тільки всередині самого курсу

    class Config:
        from_attributes = True

class CourseDetail(CourseList): # Успадковуємо базові поля
    content: str
    badge_url: str
    questions: List[QuizQuestion]

    

