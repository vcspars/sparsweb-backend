import smtplib
import os
import base64
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from typing import Optional, List
from pathlib import Path

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("EMAIL_HOST")
        # Handle EMAIL_PORT with default fallback
        email_port_str = os.getenv("EMAIL_PORT", "587")
        try:
            self.smtp_port = int(email_port_str)
        except (ValueError, TypeError):
            self.smtp_port = 587  # Default to 587 if invalid
        self.use_tls = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
        self.username = os.getenv("EMAIL_HOST_USER")
        # Remove spaces from password (Gmail app passwords should not have spaces)
        password = os.getenv("EMAIL_HOST_PASSWORD")
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
      <div>{dot}&nbsp;<a href="mailto:info@sparsus.com"
            style="color:#337AB7;text-decoration:none;">info@sparsus.com</a></div>
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
        subject = f"Thank you for your {form_type} request - SPARS"
        logo_path = self._get_logo_path()
        logo_cid = None
        embedded_images = {}
        
        if logo_path:
            logo_cid = "spars_logo"
            embedded_images[logo_cid] = logo_path
        
        signature = self._get_signature_block(logo_cid)
        user_name = name or "Valued Customer"
        
        # For Demo Request, don't include the "personalized demo" line since they already requested one
        demo_line = ""
        if form_type.lower() != "demo request":
            demo_line = """    <p>
      If you'd like a <strong>personalized demo</strong> or have any questions,
      simply reply to this e-mail.
    </p>

"""
        
        html_body = f"""\
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
  <body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;margin:0;padding:20px;max-width:600px;margin:0 auto;">
    <p>Dear {user_name},</p>

    <p>
      Thank you for your interest in <strong>SPARS – Ultimate ERP Solution
      for the Home Furnishing Industry</strong>.
    </p>

    <p>
      We have received your {form_type} request and will get back to you shortly.
    </p>

{demo_line}    <p style="margin-top:18px;margin-bottom:0;">
      Best regards,<br><br><strong>Team&nbsp;SPARS</strong><br>
    </p>

    {signature}
  </body>
</html>
"""
        
        # For Demo Request, don't include the "personalized demo" line in text version
        demo_text = ""
        if form_type.lower() != "demo request":
            demo_text = "\nIf you'd like a personalized demo or have any questions, simply reply to this e-mail.\n"
        
        text_body = f"""Dear {user_name},

Thank you for your interest in SPARS – Ultimate ERP Solution for the Home Furnishing Industry.

We have received your {form_type} request and will get back to you shortly.{demo_text}
Best regards,
Team SPARS

Magnum Opus System Corp. – USA
+1 (646) 775-2716
www.sparsus.com
112 West 34 St. 18th Floor, New York, NY 10120
info@sparsus.com
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
info@sparsus.com
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
info@sparsus.com
"""
        
        return await self.send_email(to_email, subject, text_body, html_body, attachments, embedded_images)

