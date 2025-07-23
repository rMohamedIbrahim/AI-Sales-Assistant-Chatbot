# Free API Setup Guide for Two-Wheeler Sales VoiceBot

This guide provides step-by-step instructions for setting up all the free APIs used in this project.

## 🔧 APIs and Services Setup

### 1. Google Speech Recognition API (FREE)

**Service**: Google Speech-to-Text (Free tier)
**Usage**: Speech recognition for voice input
**Setup**: No API key required for basic usage!

```python
# Already configured in the project
# Uses SpeechRecognition library with Google's free service
# Limitations: Rate limited, requires internet connection
```

**Links**:

- Documentation: https://cloud.google.com/speech-to-text/docs
- Python Library: https://pypi.org/project/SpeechRecognition/

### 2. Google Text-to-Speech (gTTS) - FREE

**Service**: Google Text-to-Speech
**Usage**: Convert text to speech audio
**Setup**: No API key required!

```python
# Already configured in the project
# Uses gTTS library
# Limitations: Requires internet connection
```

**Links**:

- Documentation: https://gtts.readthedocs.io/
- PyPI: https://pypi.org/project/gTTS/

### 3. Gmail SMTP (FREE)

**Service**: Gmail SMTP for email notifications
**Usage**: Send booking confirmations and service notifications
**Setup Required**: Yes

#### Step-by-step Setup:

1. **Create Gmail Account** (if you don't have one):

   - Go to: https://accounts.google.com/signup
   - Create a new Gmail account

2. **Enable 2-Factor Authentication**:

   - Go to: https://myaccount.google.com/security
   - Turn on 2-Step Verification

3. **Generate App Password**:

   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password

4. **Update .env file**:

```env
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_16_character_app_password
ENABLE_EMAIL_NOTIFICATIONS=true
```

**Links**:

- Gmail Setup: https://support.google.com/accounts/answer/185833
- App Passwords: https://support.google.com/accounts/answer/185833

### 4. SQLite Database (FREE)

**Service**: Local SQLite database
**Usage**: Store customer data, bookings, services
**Setup**: Already configured (file-based, no server needed)

```python
# Already configured in the project
# Uses aiosqlite for async operations
# Database file: ./data/voicebot.db
```

### 5. Offline Text-to-Speech (pyttsx3) - FREE

**Service**: Local TTS engine
**Usage**: Offline text-to-speech backup
**Setup**: No configuration needed

```python
# Already configured in the project
# Works offline without internet
# Uses system TTS engines
```

**Links**:

- Documentation: https://pyttsx3.readthedocs.io/

## 🌐 Optional Free API Upgrades

### 1. OpenAI API (FREE Tier)

**Service**: Advanced NLP and conversation handling
**Usage**: Better conversation management
**Free Tier**: $5 credit for new users

#### Setup:

1. Go to: https://platform.openai.com/signup
2. Get API key from: https://platform.openai.com/api-keys
3. Add to .env:

```env
OPENAI_API_KEY=your_openai_api_key
```

### 2. Hugging Face (FREE)

**Service**: Free AI models for NLP
**Usage**: Sentiment analysis, language detection
**Setup**: Create account and get API key

#### Setup:

1. Go to: https://huggingface.co/join
2. Get token from: https://huggingface.co/settings/tokens
3. Add to .env:

```env
HUGGINGFACE_API_KEY=your_hf_token
```

### 3. MongoDB Atlas (FREE Tier)

**Service**: Cloud database (alternative to SQLite)
**Usage**: Cloud-based database storage
**Free Tier**: 512MB storage

#### Setup:

1. Go to: https://www.mongodb.com/cloud/atlas/register
2. Create free cluster
3. Get connection string
4. Add to .env:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/dbname
```

### 4. Twilio (FREE Trial)

**Service**: SMS notifications (alternative to email)
**Usage**: SMS notifications
**Free Trial**: $15 credit

#### Setup:

1. Go to: https://www.twilio.com/try-twilio
2. Get Account SID and Auth Token
3. Add to .env:

```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number
```

### 5. Redis Cloud (FREE Tier)

**Service**: In-memory caching
**Usage**: Session management and caching
**Free Tier**: 30MB storage

#### Setup:

1. Go to: https://redis.com/try-free/
2. Create database
3. Get connection details
4. Add to .env:

```env
REDIS_URL=redis://username:password@host:port
```

## 🔑 Current Configuration

The project is configured to work with these FREE services:

✅ **No API Keys Required**:

- Google Speech Recognition (built into SpeechRecognition library)
- Google Text-to-Speech (gTTS)
- SQLite Database
- Offline TTS (pyttsx3)
- Local file caching

⚙️ **API Keys Required** (but free):

- Gmail SMTP (use your Gmail credentials)

## 🚀 Quick Start

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Update .env with your Gmail credentials**:

```env
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

3. **Run the application**:

```bash
uvicorn src.main:app --reload
```

4. **Test the API**:
   - Go to: http://localhost:8000/docs
   - Try the voice endpoints

## 🔒 Security Notes

1. **Never commit API keys to git**
2. **Use environment variables for all secrets**
3. **Enable 2FA on all accounts**
4. **Regularly rotate API keys**
5. **Monitor usage to avoid hitting limits**

## 📊 Free Tier Limitations

| Service           | Limitation     | Workaround               |
| ----------------- | -------------- | ------------------------ |
| Google Speech API | Rate limited   | Add retry logic          |
| gTTS              | Rate limited   | Use offline TTS fallback |
| Gmail SMTP        | 500 emails/day | Use multiple accounts    |
| SQLite            | Single file    | Regular backups          |

## 🆘 Troubleshooting

### Common Issues:

1. **Speech Recognition not working**:

   - Install pyaudio: `pip install pyaudio`
   - Check internet connection
   - Verify audio file format

2. **Email sending fails**:

   - Verify Gmail app password
   - Check 2FA is enabled
   - Test SMTP settings

3. **Database errors**:
   - Ensure data directory exists
   - Check file permissions
   - Verify SQLite installation

## 📞 Support

If you need help setting up any of these services:

1. Check the official documentation links provided
2. Search for setup tutorials on YouTube
3. Check Stack Overflow for common issues
4. Review the project's error logs

## 🎯 Next Steps

Once you have the basic setup working:

1. Test all endpoints using the Swagger UI at `/docs`
2. Upload test audio files
3. Verify email notifications
4. Monitor logs for errors
5. Consider upgrading to paid tiers for production use

---

**Note**: All links and instructions were current as of July 2025. Some services may have changed their signup process or pricing.
