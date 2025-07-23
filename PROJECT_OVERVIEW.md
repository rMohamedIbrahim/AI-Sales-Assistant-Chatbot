# 🎯 Two-Wheeler Sales VoiceBot - Complete Project Guide

## 🏗️ Project Architecture

```
VoiceBot Project/
├── 📱 Frontend (Web Interface)
│   ├── index.html          # Main web interface
│   ├── styles.css          # Styling
│   ├── script.js           # JavaScript functionality
│   └── assets/             # Images, icons
│
├── 🔧 Backend (FastAPI)
│   ├── src/
│   │   ├── main.py              # 🚀 MAIN ENTRY POINT
│   │   ├── main_minimal.py      # Currently running version
│   │   ├── api/                 # API Routes
│   │   │   ├── voice_routes.py  # Speech endpoints
│   │   │   ├── booking_routes.py# Booking management
│   │   │   └── service_routes.py# Service endpoints
│   │   ├── services/            # Business Logic
│   │   │   ├── speech_service.py# 🎤 Speech processing
│   │   │   ├── voice_service.py # Voice operations
│   │   │   └── notification_service.py
│   │   ├── models/              # Data Models
│   │   │   ├── schemas.py       # API schemas
│   │   │   └── database.py      # DB models
│   │   ├── core/                # Configuration
│   │   │   └── config.py        # Settings
│   │   └── infrastructure/      # External services
│   │       ├── database.py      # Database connection
│   │       ├── logging.py       # Logging setup
│   │       └── middleware.py    # Request middleware
│   │
├── 🗃️ Data Storage
│   ├── data/
│   │   ├── voicebot.db         # SQLite database
│   │   ├── audio/              # Audio files
│   │   └── .cache/             # Cache storage
│   │
├── ⚙️ Configuration
│   ├── .env                    # Environment variables
│   ├── requirements.txt        # Python dependencies
│   └── .venv/                  # Virtual environment
│
└── 📋 Documentation
    ├── README.md
    ├── SETUP_SUCCESS.md
    └── FIXES_COMPLETED.md
```

## 🎯 What This Project Does

### **Core Functionality:**

1. **🎤 Speech Recognition** - Converts customer voice to text (Google Free API)
2. **🔊 Text-to-Speech** - Responds with voice (gTTS + pyttsx3)
3. **🌐 Multi-language Support** - English, Hindi, Tamil, Telugu, Marathi, Gujarati, Bengali
4. **📱 Web Interface** - User-friendly browser interface
5. **📊 Customer Management** - Store customer data and interactions
6. **📧 Notifications** - Email alerts and updates
7. **📈 Analytics** - Track conversations and sentiment

### **Business Use Case:**

- **Target**: Two-wheeler dealerships (bikes, scooters)
- **Purpose**: Automated sales assistant for customer inquiries
- **Features**: Product info, price quotes, booking appointments, service reminders

## 🚀 How to Start the Project

### **Step 1: Activate Environment**

```bash
.venv\Scripts\Activate.ps1
```

### **Step 2: Start Backend Server**

```bash
python -m uvicorn src.main_minimal:app --reload --host 0.0.0.0 --port 8000
```

### **Step 3: Access the Application**

- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Frontend**: (We'll create this next!)

## 📊 Main Files Explained

### **🚀 src/main.py** - The Heart of the Application

- FastAPI app initialization
- Route registration
- Middleware setup
- Database connections

### **🎤 src/services/speech_service.py** - Voice Processing Engine

- Google Speech Recognition integration
- Text-to-speech conversion
- Language detection
- Audio file handling

### **⚙️ .env** - Configuration Center

- API keys and secrets
- Database settings
- Email configuration
- Feature toggles

### **📋 requirements.txt** - Dependencies

- All Python packages needed
- Versions for compatibility

## 🔄 Data Flow

```
Customer Speaks → Microphone → Speech Recognition →
Text Processing → Business Logic → Database →
Response Generation → Text-to-Speech → Speaker
```

## 🌟 Key Features

1. **Free APIs Only** - No paid services required
2. **Offline Capability** - Works without internet for basic features
3. **Multi-device Compatible** - Web browser access
4. **Real-time Processing** - Instant voice responses
5. **Scalable Architecture** - Easy to extend and modify
