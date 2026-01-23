# SPARS Backend Setup Guide

## Quick Start

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file:**
   ```bash
   # Copy the example file
   cp env.example .env
   
   # Or create manually with these values:
   ```
   
   Add your configuration to `.env`:
   ```env
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=vcspars@gmail.com
   EMAIL_HOST_PASSWORD=gaay fwrz ylqx zoen
   DEFAULT_FROM_EMAIL=vcspars@gmail.com
   ADMIN_EMAIL=vcspars@gmail.com
   
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Add PDF files:**
   - Place `SPARS_Brochure.pdf` in `backend/pdfs/`
   - Place `SPARS_Profile.pdf` in `backend/pdfs/`

5. **Run the server:**
   ```bash
   # Windows
   python run.py
   
   # Or directly with uvicorn
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Frontend Configuration

To connect your Vercel frontend to your local backend:

1. **Option 1: Use ngrok (Recommended for testing)**
   ```bash
   # Install ngrok: https://ngrok.com/
   ngrok http 8000
   ```
   This will give you a public URL like `https://abc123.ngrok.io`
   
   Update your frontend `.env` file:
   ```env
   VITE_API_URL=https://abc123.ngrok.io
   ```

2. **Option 2: Deploy backend to cloud**
   - Deploy to Heroku, Railway, Render, or similar
   - Update frontend `.env` with the deployed URL

3. **Option 3: Update Vercel environment variables**
   - Go to your Vercel project settings
   - Add environment variable: `VITE_API_URL` = your backend URL

## API Endpoints

All endpoints are prefixed with `/api`:

- `POST /api/newsletter` - Newsletter subscription
- `POST /api/contact` - Contact/Demo request
- `POST /api/brochure` - Brochure download request
- `POST /api/product-profile` - Product profile form
- `POST /api/talk-to-sales` - Talk to sales form
- `POST /api/chatbot` - Chatbot messages

## Testing

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## Troubleshooting

1. **Email not sending:**
   - Check your Gmail app password is correct
   - Ensure "Less secure app access" is enabled or use App Password
   - Check firewall/antivirus isn't blocking SMTP

2. **CORS errors:**
   - Backend is configured to allow all origins
   - If issues persist, check your backend is running and accessible

3. **Chatbot not working:**
   - Verify OPENAI_API_KEY is set in `.env`
   - Chatbot will use fallback responses if API key is missing

4. **PDF attachments not sending:**
   - Ensure PDF files exist in `backend/pdfs/`
   - Check file permissions

