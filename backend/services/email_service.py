import smtplib
import os
import base64
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from typing import Optional, List, Callable
from pathlib import Path
from datetime import datetime

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("EMAIL_HOST", "sparserp@gmail.com")
        # Handle EMAIL_PORT with default fallback
        email_port_str = os.getenv("EMAIL_PORT", "587")
        try:
            self.smtp_port = int(email_port_str)
        except (ValueError, TypeError):
            self.smtp_port = 587  # Default to 587 if invalid
        self.use_tls = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
        self.username = os.getenv("EMAIL_HOST_USER","sparserp@gmail.com")
        # Remove spaces from password (Gmail app passwords should not have spaces)
        password = os.getenv("EMAIL_HOST_PASSWORD","ofszvacrvupeptgt")
        self.password = password.replace(" ", "") if password else ""
        self.from_email = os.getenv("DEFAULT_FROM_EMAIL")
        self.admin_email = os.getenv("ADMIN_EMAIL")
        
        # Debug: Print configuration (without sensitive data)
        print(f"Email Service Config: Host={self.smtp_host}, Port={self.smtp_port}, TLS={self.use_tls}, User={self.username}, From={self.from_email}")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        embedded_images: Optional[dict] = None
    ) -> bool:
        """Send an email asynchronously"""
        try:
            msg = MIMEMultipart("related")  # Use "related" to support embedded images
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject

            # Create alternative part for text/html
            msg_alternative = MIMEMultipart("alternative")
            msg.attach(msg_alternative)

            # Add text and HTML parts
            if html_body:
                text_part = MIMEText(body, "plain")
                html_part = MIMEText(html_body, "html")
                msg_alternative.attach(text_part)
                msg_alternative.attach(html_part)
            else:
                msg_alternative.attach(MIMEText(body, "plain"))
            
            # Add embedded images (like logo)
            if embedded_images:
                for cid, image_path in embedded_images.items():
                    if os.path.exists(image_path):
                        try:
                            with open(image_path, "rb") as img_file:
                                img = MIMEImage(img_file.read())
                                img.add_header("Content-ID", f"<{cid}>")
                                img.add_header("Content-Disposition", "inline", filename=os.path.basename(image_path))
                                msg.attach(img)
                                print(f"Embedded image: {image_path} as {cid}")
                        except Exception as e:
                            print(f"Error embedding image {image_path}: {e}")

            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, "rb") as attachment:
                                part = MIMEBase("application", "octet-stream")
                                part.set_payload(attachment.read())
                                encoders.encode_base64(part)
                                # Clean filename (remove double extensions)
                                filename = os.path.basename(file_path)
                                if filename.endswith('.pdf.pdf'):
                                    filename = filename.replace('.pdf.pdf', '.pdf')
                                part.add_header(
                                    "Content-Disposition",
                                    f"attachment; filename={filename}"
                                )
                                part.add_header("Content-Type", "application/pdf")
                                msg.attach(part)
                                print(f"Attached PDF: {filename}")
                        except Exception as e:
                            print(f"Error attaching file {file_path}: {e}")
                    else:
                        print(f"Attachment file not found: {file_path}")

            # Validate configuration before attempting connection
            if not self.smtp_host:
                raise ValueError("EMAIL_HOST is not set in environment variables")
            if not self.username:
                raise ValueError("EMAIL_HOST_USER is not set in environment variables")
            if not self.password:
                raise ValueError("EMAIL_HOST_PASSWORD is not set in environment variables")
            
            # Send email
            # Use SSL for port 465, or STARTTLS for port 587
            print(f"Attempting to connect to {self.smtp_host}:{self.smtp_port} (SSL: {self.smtp_port == 465})")
            
            if self.smtp_port == 465:
                # Use SSL connection for port 465 (required for Render and other cloud platforms)
                print("Using SMTP_SSL for port 465")
                try:
                    server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30)
                    print("Connected successfully, attempting login...")
                    server.login(self.username, self.password)
                    print("Login successful, sending message...")
                    server.send_message(msg)
                    server.quit()
                    print("Email sent successfully via SMTP_SSL")
                except Exception as ssl_error:
                    print(f"SMTP_SSL error: {str(ssl_error)}")
                    try:
                        server.quit()
                    except:
                        pass
                    raise
            else:
                # Use STARTTLS for port 587 (for local development)
                print(f"Using SMTP with STARTTLS for port {self.smtp_port}")
                try:
                    server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
                    print("Connected successfully, starting TLS...")
                    if self.use_tls:
                        server.starttls()
                    print("TLS started, attempting login...")
                    server.login(self.username, self.password)
                    print("Login successful, sending message...")
                    server.send_message(msg)
                    server.quit()
                    print("Email sent successfully via SMTP STARTTLS")
                except Exception as tls_error:
                    print(f"SMTP STARTTLS error: {str(tls_error)}")
                    try:
                        server.quit()
                    except:
                        pass
                    raise

            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    async def send_form_notification(
        self,
        form_type: str,
        form_data: dict,
        recipient_email: Optional[str] = None
    ) -> bool:
        """Send notification email to admin about form submission"""
        recipient = recipient_email or self.admin_email
        
        subject = f"New {form_type} Form Submission - SPARS"
        
        # Create HTML email body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">New {form_type} Form Submission</h2>
                <div style="background-color: #f9fafb; padding: 20px; border-radius: 8px; margin-top: 20px;">
                    <h3 style="color: #1f2937; margin-top: 0;">Form Details:</h3>
                    <table style="width: 100%; border-collapse: collapse;">
        """
        
        for key, value in form_data.items():
            if value:  # Only include non-empty fields
                formatted_key = key.replace("_", " ").title()
                html_body += f"""
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 8px 0; font-weight: bold; width: 40%;">{formatted_key}:</td>
                            <td style="padding: 8px 0;">{value}</td>
                        </tr>
                """
        
        html_body += """
                    </table>
                </div>
                <p style="margin-top: 20px; color: #6b7280; font-size: 14px;">
                    This is an automated notification from the SPARS website.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"New {form_type} Form Submission\n\n"
        for key, value in form_data.items():
            if value:
                formatted_key = key.replace("_", " ").title()
                text_body += f"{formatted_key}: {value}\n"
        
        return await self.send_email(recipient, subject, text_body, html_body, None, {})

    def _get_logo_path(self) -> Optional[str]:
        """Get logo file path"""
        
        # Try multiple possible paths (checking both old src/assets and new public/assets locations)
        possible_paths = [
            Path(__file__).parent.parent.parent / "public" / "assets" / "spars-logo.png",  # New Next.js location
            Path(__file__).parent.parent / "public" / "assets" / "spars-logo.png",
            Path(__file__).parent.parent.parent / "src" / "assets" / "spars-logo.png",  # Old location (for backward compatibility)
            Path(__file__).parent.parent / "src" / "assets" / "spars-logo.png",
            Path(__file__).parent / "assets" / "spars-logo.png",
        ]
        
        for logo_path in possible_paths:
            if logo_path.exists():
                return str(logo_path)
        
        # If logo not found, return None
        print("Warning: SPARS logo not found. Email will be sent without logo.")
        print(f"Checked paths: {[str(p) for p in possible_paths]}")
        return None

    def _get_signature_block(self, logo_cid: Optional[str] = None) -> str:
        """Get responsive signature block"""
        dot = '<span style="color:#337AB7;font-size:17px;line-height:0;">•</span>'
        
        # Logo HTML - use CID reference if logo exists
        logo_html = ""
        if logo_cid:
            logo_html = f"""
    <td style="padding-right:10px;">
      <img src="cid:{logo_cid}" alt="SPARS"
           height="32" style="height:32px;width:auto;display:block;max-width:100%;">
    </td>
"""
        else:
            # If no logo, add a text placeholder
            logo_html = '<td style="padding-right:10px;"><strong style="color:#337AB7;font-size:18px;">SPARS</strong></td>'
        
        return f"""
<table role="presentation" cellpadding="0" cellspacing="0"
       style="margin-top:12px;font-size:14px;max-width:480px;width:100%;">
  <tr style="vertical-align:top;">
{logo_html}

    <td style="border-left:1px solid #ccc;width:1px;"></td>
    <td style="width:10px;"></td>

    <td style="font-family:Arial,sans-serif;color:#000;line-height:1.35;">
      <div>{dot}&nbsp;Magnum&nbsp;Opus&nbsp;System&nbsp;Corp.&nbsp;–&nbsp;USA</div>
      <div>{dot}&nbsp;+1&nbsp;(646)&nbsp;775-2716</div>
      <div>{dot}&nbsp;<a href="https://www.sparsus.com"
            style="color:#337AB7;text-decoration:none;">www.sparsus.com</a></div>
      <div>{dot}&nbsp;112&nbsp;West&nbsp;34&nbsp;St.&nbsp;18<sup>th</sup>&nbsp;Floor,&nbsp;New&nbsp;York,&nbsp;NY&nbsp;10120</div>
      <div>{dot}&nbsp;<a href="mailto:sales@sparsus.com"
            style="color:#337AB7;text-decoration:none;">sales@sparsus.com</a></div>
    </td>
  </tr>
</table>
"""

    async def send_confirmation_email(
        self,
        to_email: str,
        form_type: str,
        attachments: Optional[List[str]] = None,
        name: Optional[str] = None
    ) -> bool:
        """Send confirmation email to user"""
        logo_path = self._get_logo_path()
        logo_cid = None
        embedded_images = {}
        
        if logo_path:
            logo_cid = "spars_logo"
            embedded_images[logo_cid] = logo_path
        
        signature = self._get_signature_block(logo_cid)
        
        # Capitalize first letter of name (and each word for full names)
        user_name = name or "Valued Customer"
        if user_name:
            # Capitalize first letter of each word
            user_name = " ".join(word.capitalize() for word in user_name.split())
        
        # Determine form type and set appropriate content
        form_type_lower = form_type.lower()
        
        if "newsletter" in form_type_lower:
            # Newsletter Subscription
            subject = "Thank you for subscribing to SPARS Newsletter"
            html_body = f"""\
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
  <body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;margin:0;padding:20px;max-width:600px;margin:0 auto;">
    <p>Dear <strong>{user_name}</strong>,</p>

    <p>
      Thank you for your interest in <strong>SPARS – the Ultimate ERP Solution for the Home Furnishing Industry</strong>.
    </p>

    <p>
      You have been successfully subscribed to our newsletter. You'll now receive updates, insights, and product news from SPARS.
    </p>

    <p>
      If you'd like a <strong>personalized demo</strong> or have any questions, feel free to reply to this email—we'd be happy to assist you.
    </p>

    <p style="margin-top:18px;margin-bottom:0;">
      Best regards,<br><br><strong>Team&nbsp;SPARS</strong><br>
    </p>

    {signature}
  </body>
</html>
"""
            text_body = f"""Dear {user_name},

Thank you for your interest in SPARS – the Ultimate ERP Solution for the Home Furnishing Industry.

You have been successfully subscribed to our newsletter. You'll now receive updates, insights, and product news from SPARS.

If you'd like a personalized demo or have any questions, feel free to reply to this email—we'd be happy to assist you.

Best regards,

Team SPARS

Magnum Opus System Corp. – USA
+1 (646) 775-2716
www.sparsus.com
112 West 34 St. 18th Floor, New York, NY 10120
sales@sparsus.com
"""
        
        elif "sales" in form_type_lower:
            # Talk to Sales - Check this BEFORE "contact" or "inquiry" to avoid matching "Sales Inquiry"
            subject = "Thank You for Contacting SPARS Sales Team"
            html_body = f"""\
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
  <body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;margin:0;padding:20px;max-width:600px;margin:0 auto;">
    <p>Dear <strong>{user_name}</strong>,</p>

    <p>
      Thank you for your interest in <strong>SPARS – the Ultimate ERP Solution for the Home Furnishing Industry</strong>.
    </p>

    <p>
      We have received your request to connect with our sales team. One of our representatives will get in touch with you shortly to discuss your requirements.
    </p>

    <p>
      If you'd like a <strong>personalized demo</strong> or have any questions in the meantime, feel free to reply to this email.
    </p>

    <p style="margin-top:18px;margin-bottom:0;">
      Best regards,<br><br><strong>Team&nbsp;SPARS</strong><br>
    </p>

    {signature}
  </body>
</html>
"""
            text_body = f"""Dear {user_name},

Thank you for your interest in SPARS – the Ultimate ERP Solution for the Home Furnishing Industry.

We have received your request to connect with our sales team. One of our representatives will get in touch with you shortly to discuss your requirements.

If you'd like a personalized demo or have any questions in the meantime, feel free to reply to this email.

Best regards,

Team SPARS

Magnum Opus System Corp. – USA
+1 (646) 775-2716
www.sparsus.com
112 West 34 St. 18th Floor, New York, NY 10120
sales@sparsus.com
"""
        
        elif "demo" in form_type_lower:
            # Demo Request
            subject = "Thank You for Requesting a Demo – SPARS"
            html_body = f"""\
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
  <body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;margin:0;padding:20px;max-width:600px;margin:0 auto;">
    <p>Dear <strong>{user_name}</strong>,</p>

    <p>
      Thank you for your interest in <strong>SPARS – the Ultimate ERP Solution for the Home Furnishing Industry</strong>.
    </p>

    <p>
      We have received your demo request. Our team will contact you shortly to schedule the demo and share further details.
    </p>

    <p style="margin-top:18px;margin-bottom:0;">
      Best regards,<br><br><strong>Team&nbsp;SPARS</strong><br>
    </p>

    {signature}
  </body>
</html>
"""
            text_body = f"""Dear {user_name},

Thank you for your interest in SPARS – the Ultimate ERP Solution for the Home Furnishing Industry.

We have received your demo request. Our team will contact you shortly to schedule the demo and share further details.

Best regards,

Team SPARS

Magnum Opus System Corp. – USA
+1 (646) 775-2716
www.sparsus.com
112 West 34 St. 18th Floor, New York, NY 10120
sales@sparsus.com
"""
        
        elif "contact" in form_type_lower or ("inquiry" in form_type_lower and "sales" not in form_type_lower):
            # Contact Us
            subject = "Thank You for Contacting SPARS - We've Received Your Inquiry"
            html_body = f"""\
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
  <body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;margin:0;padding:20px;max-width:600px;margin:0 auto;">
    <p>Dear <strong>{user_name}</strong>,</p>

    <p>
      Thank you for your interest in <strong>SPARS – the Ultimate ERP Solution for the Home Furnishing Industry</strong>.
    </p>

    <p>
      We have received your inquiry submitted through our website. Our team will review it and get back to you shortly.
    </p>

    <p>
      If you'd like a <strong>personalized demo</strong> or have any additional questions, feel free to reply to this email.
    </p>

    <p style="margin-top:18px;margin-bottom:0;">
      Best regards,<br><br><strong>Team&nbsp;SPARS</strong><br>
    </p>

    {signature}
  </body>
</html>
"""
            text_body = f"""Dear {user_name},

Thank you for your interest in SPARS – the Ultimate ERP Solution for the Home Furnishing Industry.

We have received your inquiry submitted through our website. Our team will review it and get back to you shortly.

If you'd like a personalized demo or have any additional questions, feel free to reply to this email.

Best regards,
Team SPARS

Magnum Opus System Corp. – USA
+1 (646) 775-2716
www.sparsus.com
112 West 34 St. 18th Floor, New York, NY 10120
sales@sparsus.com
"""
        
        else:
            # Default/fallback (shouldn't happen, but keeping for safety)
            subject = f"Thank you for your {form_type} request - SPARS"
            html_body = f"""\
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
  <body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;margin:0;padding:20px;max-width:600px;margin:0 auto;">
    <p>Dear <strong>{user_name}</strong>,</p>

    <p>
      Thank you for your interest in <strong>SPARS – the Ultimate ERP Solution for the Home Furnishing Industry</strong>.
    </p>

    <p>
      We have received your {form_type} request and will get back to you shortly.
    </p>

    <p style="margin-top:18px;margin-bottom:0;">
      Best regards,<br><br><strong>Team&nbsp;SPARS</strong><br>
    </p>

    {signature}
  </body>
</html>
"""
            text_body = f"""Dear {user_name},

Thank you for your interest in SPARS – the Ultimate ERP Solution for the Home Furnishing Industry.

We have received your {form_type} request and will get back to you shortly.

Best regards,

Team SPARS

Magnum Opus System Corp. – USA
+1 (646) 775-2716
www.sparsus.com
112 West 34 St. 18th Floor, New York, NY 10120
sales@sparsus.com
"""
        
        return await self.send_email(to_email, subject, text_body, html_body, attachments, embedded_images)

    async def send_brochure_email(
        self,
        to_email: str,
        name: str,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """Send brochure email with PDF attachment"""
        subject = "SPARS Product Brochure - Thank You for Your Interest"
        logo_path = self._get_logo_path()
        logo_cid = None
        embedded_images = {}
        
        if logo_path:
            logo_cid = "spars_logo"
            embedded_images[logo_cid] = logo_path
        
        signature = self._get_signature_block(logo_cid)
        
        html_body = f"""\
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
  <body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;margin:0;padding:20px;max-width:600px;margin:0 auto;">
    <p>Dear {name},</p>

    <p>
      Thank you for your interest in <strong>SPARS – Ultimate ERP Solution
      for the Home Furnishing Industry</strong>.
    </p>

    <p>
      Please find attached the <strong>product brochure</strong> with detailed
      information about our modules, capabilities, and integration options.
    </p>

    <p>
      If you'd like a <strong>personalized demo</strong> or have any questions,
      simply reply to this e-mail.
    </p>

    <p style="margin-top:18px;margin-bottom:0;">
      Best regards,<br><br><strong>Team&nbsp;SPARS</strong><br>
    </p>

    {signature}
  </body>
</html>
"""
        
        text_body = f"""Dear {name},

Thank you for your interest in SPARS – Ultimate ERP Solution for the Home Furnishing Industry.

Please find attached the product brochure with detailed information about our modules, capabilities, and integration options.

If you'd like a personalized demo or have any questions, simply reply to this e-mail.

Best regards,
Team SPARS

Magnum Opus System Corp. – USA
+1 (646) 775-2716
www.sparsus.com
112 West 34 St. 18th Floor, New York, NY 10120
sales@sparsus.com
"""
        
        return await self.send_email(to_email, subject, text_body, html_body, attachments, embedded_images)

    async def send_product_profile_email(
        self,
        to_email: str,
        name: str,
        pdf_url: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """Send product profile email with PDF"""
        subject = "SPARS Product Profile - Thank You for Your Interest"
        logo_path = self._get_logo_path()
        logo_cid = None
        embedded_images = {}
        
        if logo_path:
            logo_cid = "spars_logo"
            embedded_images[logo_cid] = logo_path
        
        signature = self._get_signature_block(logo_cid)
        
        download_section = ""
        if pdf_url:
            download_section = f"""
    <p>
      You can download the full&nbsp;PDF product profile here:<br>
      <a href="{pdf_url}" style="color:#337AB7;text-decoration:none;">
        Download SPARS Product Profile&nbsp;(PDF)
      </a>
    </p>
"""
        elif attachments:
            download_section = """
    <p>
      Please find attached the <strong>product profile</strong> with detailed
      information about our modules, capabilities, and integration options.
    </p>
"""
        
        html_body = f"""\
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
  <body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;margin:0;padding:20px;max-width:600px;margin:0 auto;">
    <p>Dear {name},</p>

    <p>
      Thank you for your interest in <strong>SPARS – Ultimate ERP Solution
      for the Home Furnishing Industry</strong>.
    </p>
{download_section}
    <p>
      If you'd like a <strong>personalized demo</strong> or have any questions,
      simply reply to this e-mail.
    </p>

    <p style="margin-top:18px;margin-bottom:0;">
      Best regards,<br><br><strong>Team&nbsp;SPARS</strong><br>
    </p>

    {signature}
  </body>
</html>
"""
        
        text_body = f"""Dear {name},

Thank you for your interest in SPARS – Ultimate ERP Solution for the Home Furnishing Industry.

Please find attached the product profile with detailed information about our modules, capabilities, and integration options.

If you'd like a personalized demo or have any questions, simply reply to this e-mail.

Best regards,
Team SPARS

Magnum Opus System Corp. – USA
+1 (646) 775-2716
www.sparsus.com
112 West 34 St. 18th Floor, New York, NY 10120
sales@sparsus.com
"""
        
        return await self.send_email(to_email, subject, text_body, html_body, attachments, embedded_images)

    def _format_datetime(self, dt_string: str) -> str:
        """Format ISO datetime string to readable format"""
        try:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return dt_string

    async def send_demo_request_sales_notification(self, form_data: dict) -> bool:
        """Send demo request notification to sales team"""
        sales_email = "sales@sparsus.com"
        subject = "New Demo Request Received – SPARS Website Form Submission"
        
        # Format submission date/time
        submitted_at = form_data.get("submitted_at", "")
        if submitted_at:
            submitted_at = self._format_datetime(submitted_at)
        
        # Build plain text email body with proper indentation
        body = f"""Hello SPARS Sales Team,

A new Demo Request has been submitted through the SPARS website.
Please review the prospect's details below and arrange the demo accordingly.

⏰ Demo Request Details
    First Name: {form_data.get("first_name", "")}
    Last Name: {form_data.get("last_name", "")}
    Email Address: {form_data.get("email", "")}
    Phone Number: {form_data.get("phone", "")}

    Company Name: {form_data.get("company_name", "")}
    Company Size: {form_data.get("company_size", "")}

📅 Preferred Demo Schedule
    Preferred Demo Date: {form_data.get("preferred_demo_date", "")}
    Preferred Demo Time: {form_data.get("preferred_demo_time", "")}

📄 Additional Information
    {form_data.get("additional_information", "")}

📋 Requirements
    Current ERP System (if any): {form_data.get("current_system", "")}
    Number of Warehouses: {form_data.get("warehouses", "")}
    Expected Number of Users: {form_data.get("users", "")}
    Specific Requirements or Challenges: {form_data.get("requirements", "")}
    Implementation Timeline: {form_data.get("timeline", "")}

🕐 Submission Information
    Date & Time: {submitted_at}
    Source: Website - Request a Demo Form

Please contact the prospect to confirm availability, align expectations, and schedule
the demo session.
If the demo is scheduled, kindly update the sales/demo tracker accordingly.

Best regards,
SPARS Website Notification System"""
        
        # Build HTML email body with proper formatting matching user email style
        html_body = f"""\
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
  <body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;margin:0;padding:20px;max-width:600px;margin:0 auto;">
    <p><strong>Hello SPARS Sales Team,</strong></p>

    <p>
      A new <strong>Demo Request</strong> has been submitted through the SPARS website.<br>
      Please review the prospect's details below and arrange the demo accordingly.
    </p>

    <p>
      <strong>⏰ Demo Request Details</strong><br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>First Name:</strong> {form_data.get("first_name", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Last Name:</strong> {form_data.get("last_name", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Email Address:</strong> {form_data.get("email", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Phone Number:</strong> {form_data.get("phone", "")}<br>
      <br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Company Name:</strong> {form_data.get("company_name", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Company Size:</strong> {form_data.get("company_size", "")}
    </p>

    <p>
      <strong>📅 Preferred Demo Schedule</strong><br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Preferred Demo Date:</strong> {form_data.get("preferred_demo_date", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Preferred Demo Time:</strong> {form_data.get("preferred_demo_time", "")}
    </p>

    <p>
      <strong>📄 Additional Information</strong><br>
      &nbsp;&nbsp;&nbsp;&nbsp;{form_data.get("additional_information", "")}
    </p>

    <p>
      <strong>📋 Requirements</strong><br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Current ERP System (if any):</strong> {form_data.get("current_system", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Number of Warehouses:</strong> {form_data.get("warehouses", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Expected Number of Users:</strong> {form_data.get("users", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Specific Requirements or Challenges:</strong> {form_data.get("requirements", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Implementation Timeline:</strong> {form_data.get("timeline", "")}
    </p>

    <p>
      <strong>🕐 Submission Information</strong><br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Date & Time:</strong> {submitted_at}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Source:</strong> Website - Request a Demo Form
    </p>

    <p>
      Please contact the prospect to confirm availability, align expectations, and schedule<br>
      the demo session.<br>
      If the demo is scheduled, kindly update the sales/demo tracker accordingly.
    </p>

    <p style="margin-top:18px;margin-bottom:0;">
      Best regards,<br><br><strong>SPARS Website Notification System</strong><br>
    </p>
  </body>
</html>"""
        
        return await self.send_email(sales_email, subject, body, html_body, None, {})

    async def send_contact_inquiry_sales_notification(self, form_data: dict) -> bool:
        """Send contact inquiry notification to sales team"""
        sales_email = "sales@sparsus.com"
        subject = "New General Inquiry Received – SPARS Website Form Submission"
        
        # Format submission date/time
        submitted_at = form_data.get("submitted_at", "")
        if submitted_at:
            submitted_at = self._format_datetime(submitted_at)
        
        # Build plain text email body with proper indentation
        body = f"""Hello SPARS Sales Team,

A new inquiry has been submitted through the 'General Inquiry Form' on the SPARS website.
Please review the details below and take the necessary action.

📄 Inquiry Details
    First Name: {form_data.get("first_name", "")}
    Last Name: {form_data.get("last_name", "")}
    Email: {form_data.get("email", "")}
    Phone: {form_data.get("phone", "")}
    Company Name: {form_data.get("company", "")}
    Company Size: {form_data.get("company_size", "")}
    Inquiry Type: {form_data.get("inquiry_type", "")}
    Message / Details Provided by User: {form_data.get("message", "")}

⏰ Submission Information
    Date & Time: {submitted_at}
    Source: Website – General Inquiry Form

Please assess the inquiry and route it to the relevant team (Sales, Support, Operations, or Management) for appropriate follow-up.
If this inquiry is already being handled, kindly update the internal tracker accordingly.

Best regards,
SPARS Website Notification System"""
        
        # Build HTML email body with proper formatting matching user email style
        html_body = f"""\
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
  <body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;margin:0;padding:20px;max-width:600px;margin:0 auto;">
    <p><strong>Hello SPARS Sales Team,</strong></p>

    <p>
      A new inquiry has been submitted through the '<strong>General Inquiry Form</strong>' on the SPARS website.<br>
      Please review the details below and take the necessary action.
    </p>

    <p>
      <strong>📄 Inquiry Details</strong><br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>First Name:</strong> {form_data.get("first_name", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Last Name:</strong> {form_data.get("last_name", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Email:</strong> {form_data.get("email", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Phone:</strong> {form_data.get("phone", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Company Name:</strong> {form_data.get("company", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Company Size:</strong> {form_data.get("company_size", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Inquiry Type:</strong> {form_data.get("inquiry_type", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Message / Details Provided by User:</strong> {form_data.get("message", "")}
    </p>

    <p>
      <strong>⏰ Submission Information</strong><br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Date & Time:</strong> {submitted_at}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Source:</strong> Website – General Inquiry Form
    </p>

    <p>
      Please assess the inquiry and route it to the relevant team (Sales, Support, Operations, or Management) for appropriate follow-up.<br>
      If this inquiry is already being handled, kindly update the internal tracker accordingly.
    </p>

    <p style="margin-top:18px;margin-bottom:0;">
      Best regards,<br><br><strong>SPARS Website Notification System</strong><br>
    </p>
  </body>
</html>"""
        
        return await self.send_email(sales_email, subject, body, html_body, None, {})

    async def send_talk_to_sales_notification(self, form_data: dict) -> bool:
        """Send talk to sales notification to sales team"""
        sales_email = "sales@sparsus.com"
        subject = "New Lead Received – Talk To Sales Form Submission"
        
        # Format submission date/time
        submitted_at = form_data.get("submitted_at", "")
        if submitted_at:
            submitted_at = self._format_datetime(submitted_at)
        
        # Build plain text email body with proper indentation
        body = f"""Hello Sales Team,

A new inquiry has been submitted through the 'Talk To Sales' form on the SPARS website. Please find the lead details below and follow up at the earliest.

▲ Lead Details
    Contact Information:
    First Name: {form_data.get("first_name", "")}
    Last Name: {form_data.get("last_name", "")}
    Email Address: {form_data.get("email", "")}
    Contact Number: {form_data.get("phone", "")}
    Company Name: {form_data.get("company", "")}
    Company Size: {form_data.get("company_size", "")}
    Additional Information: {form_data.get("additional_information", "")}

    Requirements:
    Current ERP System (if any): {form_data.get("current_system", "")}
    Number of Warehouses: {form_data.get("warehouses", "")}
    Expected Number of Users: {form_data.get("users", "")}
    Specific Requirements or Challenges: {form_data.get("requirements", "")}
    Implementation Time Line: {form_data.get("timeline", "")}

ⓘ Submission Details
    Date & Time: {submitted_at}
    Source: Website - Talk To Sales Form

Please review the information and reach out to the prospect for further discussion, demo scheduling, or requirement analysis.
If this lead is already in progress, kindly update the sales tracker accordingly.

Best regards,
SPARS Website Notification System"""
        
        # Build HTML email body with proper formatting matching user email style
        html_body = f"""\
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
  <body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;margin:0;padding:20px;max-width:600px;margin:0 auto;">
    <p><strong>Hello Sales Team,</strong></p>

    <p>
      A new inquiry has been submitted through the '<strong>Talk To Sales</strong>' form on the SPARS website. Please find the lead details below and follow up at the earliest.
    </p>

    <p>
      <strong>▲ Lead Details</strong><br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Contact Information:</strong><br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>First Name:</strong> {form_data.get("first_name", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Last Name:</strong> {form_data.get("last_name", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Email Address:</strong> {form_data.get("email", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Contact Number:</strong> {form_data.get("phone", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Company Name:</strong> {form_data.get("company", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Company Size:</strong> {form_data.get("company_size", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Additional Information:</strong> {form_data.get("additional_information", "")}<br>
      <br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Requirements:</strong><br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Current ERP System (if any):</strong> {form_data.get("current_system", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Number of Warehouses:</strong> {form_data.get("warehouses", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Expected Number of Users:</strong> {form_data.get("users", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Specific Requirements or Challenges:</strong> {form_data.get("requirements", "")}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Implementation Time Line:</strong> {form_data.get("timeline", "")}
    </p>

    <p>
      <strong>ⓘ Submission Details</strong><br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Date & Time:</strong> {submitted_at}<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<strong>Source:</strong> Website - Talk To Sales Form
    </p>

    <p>
      Please review the information and reach out to the prospect for further discussion, demo scheduling, or requirement analysis.<br>
      If this lead is already in progress, kindly update the sales tracker accordingly.
    </p>

    <p style="margin-top:18px;margin-bottom:0;">
      Best regards,<br><br><strong>SPARS Website Notification System</strong><br>
    </p>
  </body>
</html>"""
        
        return await self.send_email(sales_email, subject, body, html_body, None, {})

    def send_emails_concurrent(self, email_tasks: List[Callable]) -> List[bool]:
        """Send multiple emails concurrently using ThreadPoolExecutor"""
        def run_async_email(email_func):
            """Helper to run async email function in thread"""
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(email_func())
                loop.close()
                return result
            except Exception as e:
                print(f"Error in concurrent email sending: {str(e)}")
                return False
        
        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all email tasks
            future_to_task = {executor.submit(run_async_email, task): task for task in email_tasks}
            
            # Collect results as they complete
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Email task failed: {str(e)}")
                    results.append(False)
        
        return results

