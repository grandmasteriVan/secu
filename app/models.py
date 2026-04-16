from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    users = relationship("User", back_populates="organization")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String)
    role = Column(String, default="user") # 'user' або 'admin'
    is_active = Column(Boolean, default=False)
    xp = Column(Integer, default=0)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    organization = relationship("Organization", back_populates="users")
    simulations = relationship("SimulationResult", back_populates="user")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    content = Column(Text)
    xp_reward = Column(Integer, default=100)
    badge_image_url = Column(String)
    quiz_json = Column(JSON) # Зберігаємо питання як список об'єктів

class UserCourse(Base):
    __tablename__ = "user_courses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    completed_at = Column(DateTime, default=datetime.utcnow)

class SimulationResult(Base):
    __tablename__ = "simulation_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    sim_type = Column(String)
    score = Column(Integer)
    completed_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="simulations")
