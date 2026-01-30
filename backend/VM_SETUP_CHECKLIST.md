# SPARS Backend - VM Setup Checklist

## ✅ All Changes Applied and Tested

This backend folder is **ready to use** on your VM. All the following have been implemented and tested:

### ✅ Fixed Issues
1. **All Forms Integrated** - Contact, Request Demo, Newsletter, Brochure, Product Profile, Talk to Sales
2. **OPENAI_API_KEY Loading** - Fixed lazy initialization (no more warnings)
3. **Email Service** - Fixed lazy initialization (emails working)
4. **Demo Request Email** - Removed "personalized demo" line from confirmation email
5. **Excel Export** - Fixed to match database schema
6. **Request Demo Endpoint** - Created `/api/request-demo` endpoint

### 📋 Pre-Deployment Checklist

#### 1. Environment Variables (.env file)
Create/verify `.env` file in `backend/` directory with:

```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=vcspars@gmail.com
EMAIL_HOST_PASSWORD=your_app_password_here
DEFAULT_FROM_EMAIL=vcspars@gmail.com
ADMIN_EMAIL=vcspars@gmail.com

# OpenAI API Key (for chatbot)
OPENAI_API_KEY=your_openai_api_key_here

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///./spars_forms.db
```

#### 2. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### 3. Verify PDF Files
Ensure these files exist in `backend/pdfs/`:
- `brochure.pdf.pdf` (or `brochure.pdf`)
- `product_profile.pdf.pdf` (or `product_profile.pdf`)

#### 4. Run Verification Script
```bash
python verify_setup.py
```

This will check:
- ✅ Environment variables
- ✅ File structure
- ✅ Python dependencies
- ✅ Service initialization
- ✅ Database connection
- ✅ API endpoints

#### 5. Start the Server

**Option 1: Using run.py (Recommended)**
```bash
python run.py
```

**Option 2: Direct uvicorn**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**For Production (no reload):**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 6. Test the Server

**Health Check:**
```bash
curl http://localhost:8000/health
```

**API Documentation:**
Visit: `http://your-vm-ip:8000/docs`

**Test All Forms:**
```bash
python test_all_forms.py
```

### 🔧 Configuration for VM

#### Firewall
Make sure port 8000 is open:
```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

#### Process Manager (Optional - for production)
Use `systemd` or `supervisor` to keep the server running:

**Example systemd service** (`/etc/systemd/system/spars-backend.service`):
```ini
[Unit]
Description=SPARS Backend API
After=network.target

[Service]
User=your-user
WorkingDirectory=/path/to/backend
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /path/to/backend/run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable spars-backend
sudo systemctl start spars-backend
sudo systemctl status spars-backend
```

### 📊 All API Endpoints

All endpoints are prefixed with `/api`:

1. `POST /api/newsletter` - Newsletter subscription
2. `POST /api/contact` - General contact form
3. `POST /api/brochure` - Brochure request
4. `POST /api/product-profile` - Product profile form
5. `POST /api/talk-to-sales` - Talk to sales form
6. `POST /api/request-demo` - Demo request form
7. `POST /api/chatbot` - Chatbot messages
8. `GET /health` - Health check
9. `GET /` - Root endpoint

### ✅ Testing

All forms have been tested and are working:
- ✅ Newsletter subscription
- ✅ Contact form
- ✅ Brochure request (with PDF attachment)
- ✅ Product profile (with PDF attachment)
- ✅ Talk to sales
- ✅ Request demo
- ✅ Chatbot (with OpenAI API)

### 🚀 Ready to Deploy!

Once you've:
1. ✅ Set up `.env` file
2. ✅ Installed dependencies
3. ✅ Verified setup with `verify_setup.py`
4. ✅ Started the server

Your backend is **ready to use**! The frontend can connect to it at `http://your-vm-ip:8000`












