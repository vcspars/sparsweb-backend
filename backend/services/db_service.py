from sqlalchemy.orm import Session
from database import (
    NewsletterSubscription,
    ContactForm,
    BrochureForm,
    ProductProfileForm,
    TalkToSalesForm
)

class DatabaseService:
    @staticmethod
    def save_newsletter(db: Session, email: str):
        """Save newsletter subscription to database"""
        subscription = NewsletterSubscription(email=email)
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription

    @staticmethod
    def save_contact_form(db: Session, form_data: dict):
        """Save contact form to database"""
        contact = ContactForm(
            first_name=form_data.get("first_name"),
            last_name=form_data.get("last_name"),
            email=form_data.get("email"),
            phone=form_data.get("phone"),
            company=form_data.get("company"),
            company_size=form_data.get("company_size"),
            message=form_data.get("message"),
            demo_date=form_data.get("demo_date"),
            current_system=form_data.get("current_system"),
            warehouses=form_data.get("warehouses"),
            users=form_data.get("users"),
            requirements=form_data.get("requirements"),
            timeline=form_data.get("timeline")
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact

    @staticmethod
    def save_brochure_form(db: Session, form_data: dict):
        """Save brochure form to database"""
        brochure = BrochureForm(
            first_name=form_data.get("first_name"),
            last_name=form_data.get("last_name"),
            email=form_data.get("email"),
            company=form_data.get("company"),
            phone=form_data.get("phone"),
            job_role=form_data.get("job_role"),
            agreed_to_marketing=form_data.get("agreed_to_marketing", False)
        )
        db.add(brochure)
        db.commit()
        db.refresh(brochure)
        return brochure

    @staticmethod
    def save_product_profile_form(db: Session, form_data: dict):
        """Save product profile form to database"""
        profile = ProductProfileForm(
            first_name=form_data.get("first_name"),
            last_name=form_data.get("last_name"),
            email=form_data.get("email"),
            phone=form_data.get("phone"),
            job_title=form_data.get("job_title"),
            company_name=form_data.get("company_name"),
            industry=form_data.get("industry"),
            company_size=form_data.get("company_size"),
            website=form_data.get("website"),
            address=form_data.get("address"),
            current_system=form_data.get("current_system"),
            warehouses=form_data.get("warehouses"),
            users=form_data.get("users"),
            requirements=form_data.get("requirements"),
            timeline=form_data.get("timeline")
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def save_talk_to_sales_form(db: Session, form_data: dict):
        """Save talk to sales form to database"""
        sales = TalkToSalesForm(
            first_name=form_data.get("first_name"),
            last_name=form_data.get("last_name"),
            email=form_data.get("email"),
            phone=form_data.get("phone"),
            company=form_data.get("company"),
            company_size=form_data.get("company_size"),
            additional_information=form_data.get("additional_information"),
            current_system=form_data.get("current_system"),
            warehouses=form_data.get("warehouses"),
            users=form_data.get("users"),
            requirements=form_data.get("requirements"),
            timeline=form_data.get("timeline")
        )
        db.add(sales)
        db.commit()
        db.refresh(sales)
        return sales

