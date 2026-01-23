from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

def get_local_time():
    """Get current local time (not UTC) - uses server's local timezone"""
    return datetime.now()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./spars_forms.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class NewsletterSubscription(Base):
    __tablename__ = "newsletter_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    subscribed_at = Column(DateTime, default=get_local_time)

class ContactForm(Base):
    __tablename__ = "contact_forms"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, index=True)
    phone = Column(String)
    company = Column(String)
    message = Column(Text, nullable=True)
    demo_date = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=get_local_time)

class BrochureForm(Base):
    __tablename__ = "brochure_forms"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, index=True)
    company = Column(String)
    phone = Column(String, nullable=True)
    job_role = Column(String, nullable=True)
    agreed_to_marketing = Column(Boolean, default=False)
    submitted_at = Column(DateTime, default=get_local_time)

class ProductProfileForm(Base):
    __tablename__ = "product_profile_forms"
    
    id = Column(Integer, primary_key=True, index=True)
    # User Information
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, index=True)
    phone = Column(String)
    job_title = Column(String, nullable=True)
    # Company Information
    company_name = Column(String)
    industry = Column(String, nullable=True)
    company_size = Column(String, nullable=True)
    website = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    # Requirements
    current_system = Column(String, nullable=True)
    warehouses = Column(Integer, nullable=True)
    users = Column(Integer, nullable=True)
    requirements = Column(Text, nullable=True)
    timeline = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=get_local_time)

class TalkToSalesForm(Base):
    __tablename__ = "talk_to_sales_forms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, index=True)
    phone = Column(String)
    company = Column(String, nullable=True)
    message = Column(Text)
    submitted_at = Column(DateTime, default=get_local_time)

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

