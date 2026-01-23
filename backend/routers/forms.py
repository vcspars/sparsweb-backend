from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import os
from pathlib import Path
from sqlalchemy.orm import Session

from services.email_service import EmailService
from services.db_service import DatabaseService
from services.excel_service import ExcelService
from database import get_db, init_db

router = APIRouter()

# Lazy initialization - create service instances when first needed
# This ensures .env is loaded before services are instantiated
_email_service = None
_db_service = None
_excel_service = None

def get_email_service():
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

def get_db_service():
    """Get or create database service instance"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service

def get_excel_service():
    """Get or create excel service instance"""
    global _excel_service
    if _excel_service is None:
        _excel_service = ExcelService()
    return _excel_service

# PDF file paths (you'll need to add these files to backend/pdfs/)
pdfs_dir = os.path.join(os.path.dirname(__file__), "..", "pdfs")

# Check for multiple possible filenames
BROCHURE_PDF = None
PRODUCT_PROFILE_PDF = None

possible_brochure_names = [
    "SPARS_Brochure.pdf",
    "SPARS-Brochure.pdf",
    "SPARS-Product-Brochure.pdf"
]

possible_profile_names = [
    "SPARS_Profile.pdf",
    "SPARS-Product-Profile.pdf",
    "SPARS-ProductProfile.pdf"
]

# Find brochure PDF
for name in possible_brochure_names:
    path = os.path.join(pdfs_dir, name)
    if os.path.exists(path):
        BROCHURE_PDF = path
        break

# Find product profile PDF
for name in possible_profile_names:
    path = os.path.join(pdfs_dir, name)
    if os.path.exists(path):
        PRODUCT_PROFILE_PDF = path
        break

# Newsletter Subscription Model
class NewsletterSubscription(BaseModel):
    email: EmailStr

# General Contact/Inquiry Model
class ContactForm(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    inquiry_type: str
    message: str

# Demo Request Model
class DemoRequestForm(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    company_name: str
    company_size: Optional[str] = None
    preferred_demo_date: str
    preferred_demo_time: Optional[str] = None
    additional_information: Optional[str] = None

# Brochure Request Model
class BrochureForm(BaseModel):
    full_name: str
    email: EmailStr
    company: str
    phone: Optional[str] = None
    job_role: Optional[str] = None
    agreed_to_marketing: bool

# Product Profile Model
class ProductProfileForm(BaseModel):
    # User Information
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    job_title: Optional[str] = None
    
    # Company Information
    company_name: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    
    # Requirements
    current_system: Optional[str] = None
    warehouses: Optional[int] = None
    users: Optional[int] = None
    requirements: Optional[str] = None
    timeline: Optional[str] = None

# Talk to Sales Model
class TalkToSalesForm(BaseModel):
    name: str
    email: EmailStr
    phone: str
    company: Optional[str] = None
    message: str
    current_system: Optional[str] = None
    warehouses: Optional[int] = None
    users: Optional[int] = None
    requirements: Optional[str] = None
    timeline: Optional[str] = None

@router.post("/newsletter")
async def subscribe_newsletter(
    subscription: NewsletterSubscription,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Subscribe to newsletter"""
    try:
        # Save to database
        get_db_service().save_newsletter(db, subscription.email)
        
        # Export to Excel in background
        background_tasks.add_task(get_excel_service().export_all_forms, db)
        
        form_data = {
            "email": subscription.email,
            "subscribed_at": datetime.now().isoformat()
        }
        
        # Send notification to admin
        background_tasks.add_task(
            get_email_service().send_form_notification,
            "Newsletter Subscription",
            form_data
        )
        
        # Send confirmation to user
        background_tasks.add_task(
            get_email_service().send_confirmation_email,
            subscription.email,
            "Newsletter Subscription",
            None,
            subscription.email.split("@")[0]  # Use email prefix as name
        )
        
        return {
            "success": True,
            "message": "Successfully subscribed to newsletter"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing subscription: {str(e)}")

@router.post("/contact")
async def submit_contact_form(
    form: ContactForm,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit general contact/inquiry form"""
    try:
        # Split name into first and last for database storage
        name_parts = form.name.strip().split(" ", 1)
        first_name = name_parts[0] if name_parts else form.name
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # Save to database
        form_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": form.email,
            "phone": form.phone or "",
            "company": form.company or "",
            "message": form.message,
            "demo_date": None
        }
        get_db_service().save_contact_form(db, form_data)
        
        # Export to Excel in background
        background_tasks.add_task(get_excel_service().export_all_forms, db)
        
        notification_data = {
            "name": form.name,
            "email": form.email,
            "phone": form.phone or "",
            "company": form.company or "",
            "inquiry_type": form.inquiry_type,
            "message": form.message,
            "submitted_at": datetime.now().isoformat()
        }
        
        # Send notification to admin
        background_tasks.add_task(
            get_email_service().send_form_notification,
            f"Contact Inquiry - {form.inquiry_type}",
            notification_data
        )
        
        # Send confirmation to user
        background_tasks.add_task(
            get_email_service().send_confirmation_email,
            form.email,
            "Contact Inquiry",
            None,
            form.name
        )
        
        return {
            "success": True,
            "message": "Your inquiry has been submitted successfully. We'll get back to you shortly."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing form: {str(e)}")

@router.post("/brochure")
async def request_brochure(
    form: BrochureForm,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request brochure download"""
    try:
        if not form.agreed_to_marketing:
            raise HTTPException(
                status_code=400,
                detail="Marketing agreement is required"
            )
        
        # Save to database
        form_data = {
            "full_name": form.full_name,
            "email": form.email,
            "company": form.company,
            "phone": form.phone,
            "job_role": form.job_role,
            "agreed_to_marketing": form.agreed_to_marketing
        }
        get_db_service().save_brochure_form(db, form_data)
        
        # Export to Excel in background
        background_tasks.add_task(get_excel_service().export_all_forms, db)
        
        # Prepare PDF attachment if exists
        attachments = []
        if BROCHURE_PDF and os.path.exists(BROCHURE_PDF):
            attachments.append(BROCHURE_PDF)
            print(f"Found brochure PDF: {BROCHURE_PDF}")
        else:
            print(f"Brochure PDF not found in {pdfs_dir}")
        
        notification_data = {**form_data, "submitted_at": datetime.now().isoformat()}
        
        # Send notification to admin
        background_tasks.add_task(
            get_email_service().send_form_notification,
            "Brochure Request",
            notification_data
        )
        
        # Send brochure email with PDF to user
        background_tasks.add_task(
            get_email_service().send_brochure_email,
            form.email,
            form.full_name,
            attachments if attachments else None
        )
        
        return {
            "success": True,
            "message": "Brochure request submitted successfully. Check your email for the download link.",
            "has_pdf": len(attachments) > 0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@router.post("/product-profile")
async def submit_product_profile(
    form: ProductProfileForm,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit product profile form"""
    try:
        # Save to database
        form_data = {
            "first_name": form.first_name,
            "last_name": form.last_name,
            "email": form.email,
            "phone": form.phone,
            "job_title": form.job_title,
            "company_name": form.company_name,
            "industry": form.industry,
            "company_size": form.company_size,
            "website": form.website,
            "address": form.address,
            "current_system": form.current_system,
            "warehouses": form.warehouses,
            "users": form.users,
            "requirements": form.requirements,
            "timeline": form.timeline
        }
        get_db_service().save_product_profile_form(db, form_data)
        
        # Export to Excel in background
        background_tasks.add_task(get_excel_service().export_all_forms, db)
        
        # Prepare PDF attachment if exists
        attachments = []
        if PRODUCT_PROFILE_PDF and os.path.exists(PRODUCT_PROFILE_PDF):
            attachments.append(PRODUCT_PROFILE_PDF)
            print(f"Found product profile PDF: {PRODUCT_PROFILE_PDF}")
        else:
            print(f"Product profile PDF not found in {pdfs_dir}")
        
        notification_data = {**form_data, "submitted_at": datetime.now().isoformat()}
        for key, value in notification_data.items():
            if value is None:
                notification_data[key] = ""
            elif isinstance(value, int):
                notification_data[key] = str(value)
        
        # Send notification to admin
        background_tasks.add_task(
            get_email_service().send_form_notification,
            "Product Profile Request",
            notification_data
        )
        
        # Send product profile email with PDF to user
        full_name = f"{form.first_name} {form.last_name}"
        background_tasks.add_task(
            get_email_service().send_product_profile_email,
            form.email,
            full_name,
            None,  # pdf_url - can be added later if needed
            attachments if attachments else None
        )
        
        return {
            "success": True,
            "message": "Product profile submitted successfully. Check your email for the download link.",
            "has_pdf": len(attachments) > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing form: {str(e)}")

@router.post("/request-demo")
async def request_demo(
    form: DemoRequestForm,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit demo request form"""
    try:
        # Save to database (using contact form structure)
        form_data = {
            "first_name": form.first_name,
            "last_name": form.last_name,
            "email": form.email,
            "phone": form.phone,
            "company": form.company_name,
            "message": form.additional_information or "",
            "demo_date": form.preferred_demo_date
        }
        get_db_service().save_contact_form(db, form_data)
        
        # Export to Excel in background
        background_tasks.add_task(get_excel_service().export_all_forms, db)
        
        notification_data = {
            "first_name": form.first_name,
            "last_name": form.last_name,
            "email": form.email,
            "phone": form.phone,
            "company_name": form.company_name,
            "company_size": form.company_size or "",
            "preferred_demo_date": form.preferred_demo_date,
            "preferred_demo_time": form.preferred_demo_time or "",
            "additional_information": form.additional_information or "",
            "submitted_at": datetime.now().isoformat()
        }
        
        # Send notification to admin
        background_tasks.add_task(
            get_email_service().send_form_notification,
            "Demo Request",
            notification_data
        )
        
        # Send confirmation to user
        background_tasks.add_task(
            get_email_service().send_confirmation_email,
            form.email,
            "Demo Request",
            None,
            f"{form.first_name} {form.last_name}"
        )
        
        return {
            "success": True,
            "message": "Demo request submitted successfully. We'll contact you shortly to schedule your demo."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing form: {str(e)}")

@router.post("/talk-to-sales")
async def talk_to_sales(
    form: TalkToSalesForm,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit talk to sales form"""
    try:
        # Save to database
        form_data = {
            "name": form.name,
            "email": form.email,
            "phone": form.phone,
            "company": form.company,
            "message": form.message,
            "current_system": form.current_system,
            "warehouses": form.warehouses,
            "users": form.users,
            "requirements": form.requirements,
            "timeline": form.timeline
        }
        get_db_service().save_talk_to_sales_form(db, form_data)
        
        # Export to Excel in background
        background_tasks.add_task(get_excel_service().export_all_forms, db)
        
        # Prepare notification data with all fields
        notification_data = {
            **form_data,
            "current_system": form.current_system or "",
            "warehouses": str(form.warehouses) if form.warehouses else "",
            "users": str(form.users) if form.users else "",
            "requirements": form.requirements or "",
            "timeline": form.timeline or "",
            "submitted_at": datetime.now().isoformat()
        }
        
        # Send notification to admin
        background_tasks.add_task(
            get_email_service().send_form_notification,
            "Talk to Sales",
            notification_data
        )
        
        # Send confirmation to user
        background_tasks.add_task(
            get_email_service().send_confirmation_email,
            form.email,
            "Sales Inquiry",
            None,
            form.name
        )
        
        return {
            "success": True,
            "message": "Your message has been sent. Our sales team will contact you shortly."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing form: {str(e)}")

