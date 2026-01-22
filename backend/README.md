# SPARS Backend API

FastAPI backend for SPARS website forms and chatbot functionality.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the `backend` directory (copy from `.env.example`):
```bash
cp .env.example .env
```

3. Update the `.env` file with your configuration:
   - Email credentials (already provided)
   - OpenAI API key for chatbot functionality

4. Add PDF files to `backend/pdfs/`:
   - `brochure.pdf` - SPARS brochure PDF
   - `product_profile.pdf` - Product profile PDF

## Running the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Forms
- `POST /api/newsletter` - Newsletter subscription
- `POST /api/contact` - Contact/Demo request form
- `POST /api/brochure` - Brochure download request
- `POST /api/product-profile` - Product profile form
- `POST /api/talk-to-sales` - Talk to sales form

### Chatbot
- `POST /api/chatbot` - Chat with AI assistant

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

## CORS Configuration

The backend is configured to accept requests from all origins. For production, you may want to restrict this in `main.py` to specific domains.

## Notes

- All email sending is done asynchronously using background tasks
- PDF attachments are sent via email when available
- Chatbot uses OpenAI GPT-3.5-turbo with fallback responses if API key is not set
- Make sure to add your PDF files (`brochure.pdf` and `product_profile.pdf`) to the `backend/pdfs/` directory

## Frontend Integration

Update your frontend forms to point to your backend URL. For example:

```typescript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Newsletter subscription
await fetch(`${API_URL}/api/newsletter`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com' })
});

// Contact form
await fetch(`${API_URL}/api/contact`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ /* form data */ })
});
```

If your backend is running on your local PC and frontend is on Vercel, you'll need to:
1. Use a service like ngrok to expose your local backend, OR
2. Deploy the backend to a cloud service (Heroku, Railway, Render, etc.)

