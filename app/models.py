from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from .database import Base
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String, nullable=True)
    role = Column(String, default=UserRole.USER)
    xp = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    simulations = relationship("SimulationResult", back_populates="user")

class SimulationResult(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)  # 'phishing', 'quiz'
    score = Column(Integer, default=0)
    details = Column(String, nullable=True) # JSON string or text details
    completed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="simulations")

class UserCourse(Base):
    __tablename__ = "user_courses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer) # ID курсу з нашого файлу courses_data
    completed_at = Column(DateTime, default=datetime.utcnow)

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    content = Column(Text, nullable=False)
    xp_reward = Column(Integer, default=100)
    badge_image_url = Column(String)  # Шлях до файлу бейджа
    
    # Питання зберігаємо як JSON для гнучкості або через relationship
    # Тут використаємо JSON для простоти додавання через одну форму
    quiz_json = Column(JSON, nullable=False)