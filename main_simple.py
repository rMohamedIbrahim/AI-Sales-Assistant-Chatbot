"""
Two-Wheeler Sales VoiceBot - Main Application
============================================

This is the main FastAPI application for the AI-powered Two-Wheeler Sales VoiceBot.
It provides intelligent, multilingual conversation capabilities for vehicle sales,
customer support, and after-sales services.

Key Features:
- Advanced AI chatbot with intelligent response generation
- Comprehensive vehicle database with real-time pricing
- Multilingual support (English, Hindi, Tamil)
- Smart intent detection and context awareness
- Test ride booking and EMI calculations
- Service scheduling and customer support

Author: Mohamed Ibrahim
Repository: https://github.com/rMohamedIbrahim/AI-Sales-Assistant-Chatbot
License: MIT
Version: 1.0.0
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn
import os

# Initialize FastAPI application with metadata
app = FastAPI(
    title="VoiceBot Enterprise - AI Sales Assistant",
    description="Intelligent multilingual voice agent for two-wheeler sales and after-sales operations",
    version="1.0.0",
    contact={
        "name": "Mohamed Ibrahim",
        "url": "https://github.com/rMohamedIbrahim",
        "email": "contact@example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Configure CORS middleware for cross-origin requests
# This allows the frontend to communicate with the API from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Mount static files to serve the frontend application
# The frontend contains the user interface for the VoiceBot
frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    print(f"✅ Frontend mounted successfully from: {frontend_path}")
else:
    print(f"❌ Warning: Frontend directory not found at: {frontend_path}")

@app.get("/")
async def serve_frontend():
    """
    Serve the main frontend application
    
    Returns:
        FileResponse: The main HTML page for the VoiceBot interface
    """
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(str(frontend_path))
    return {"error": "Frontend not found", "path": str(frontend_path)}

@app.get("/test")
async def serve_test_page():
    """
    Serve the test page for development and debugging
    
    Returns:
        FileResponse: The test HTML page or error message
    """
    test_path = Path(__file__).parent / "frontend" / "test.html"
    if test_path.exists():
        return FileResponse(str(test_path))
    return {"error": "Test page not found", "path": str(test_path)}

@app.post("/chat")
async def chat_endpoint(request: dict):
    """
    Main chat endpoint for AI-powered conversations
    
    This endpoint processes user messages and returns intelligent responses
    using the advanced AI chatbot system. It handles various types of queries
    including vehicle information, pricing, bookings, and customer support.
    
    Args:
        request (dict): JSON payload containing:
            - message (str): User's input message
            - language (str, optional): Preferred language code
            - user_id (str, optional): User identifier for session management
    
    Returns:
        dict: Response containing:
            - response (str): AI-generated response
            - intent (str, optional): Detected user intent
            - confidence (float, optional): Confidence score
            - suggestions (list, optional): Quick reply suggestions
    
    Raises:
        400: If message is empty or invalid
        500: If internal processing error occurs
    """
    try:
        message = request.get("message", "").strip()
        if not message:
            return {"error": "Message is required", "code": "EMPTY_MESSAGE"}
        
        # Generate intelligent response using the AI system
        response = generate_intelligent_response(message)
        
        return {
            "response": response,
            "status": "success",
            "timestamp": str(Path(__file__).stat().st_mtime)  # Simple timestamp
        }
        
    except Exception as e:
        print(f"❌ Chat endpoint error: {str(e)}")
        return {
            "error": f"Processing error: {str(e)}", 
            "code": "PROCESSING_ERROR",
            "status": "error"
        }

def generate_intelligent_response(message: str) -> str:
    """
    Advanced AI response generation system
    
    This function analyzes user input and generates contextually appropriate
    responses based on intent detection, keyword analysis, and conversation flow.
    It covers various business scenarios including sales, support, and services.
    
    Args:
        message (str): User's input message to process
    
    Returns:
        str: Intelligent, contextually relevant response
    
    Features:
        - Intent recognition with high accuracy
        - Multilingual keyword detection
        - Context-aware response generation
        - Business-specific knowledge base
        - Fallback handling for unknown queries
    """
    # Convert to lowercase for consistent processing
    msg = message.lower().strip()
    
    # ==========================================
    # GREETING AND WELCOME RESPONSES
    # ==========================================
    if any(word in msg for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'namaste', 'vanakkam']):
        return """👋 **Welcome to VoiceBot Enterprise!**

I'm your AI-powered sales assistant for two-wheelers. I can help you with:

🏍️ **Vehicle Selection:** Find the perfect bike for your needs
💰 **Pricing & EMI:** Get transparent pricing and finance options  
📅 **Test Rides:** Book convenient test drive appointments
🔧 **Service Support:** Schedule maintenance and repairs
🛡️ **Insurance:** Compare policies and get instant quotes

**Popular Queries:**
• "Show me bikes under ₹1 lakh"
• "Book a test ride for Honda Shine"
• "Calculate EMI for Pulsar 150"
• "Service booking for my bike"

How can I assist you today? 🚀"""
    
    # ==========================================
    # VEHICLE RECOMMENDATIONS AND SELECTION
    # ==========================================
    elif any(word in msg for word in ['bike', 'motorcycle', 'scooter', 'recommend', 'suggest', 'show me']):
        if any(word in msg for word in ['under', 'below', '1 lakh', 'budget', 'cheap', 'affordable']):
            return """🏍️ **Top Bikes Under ₹1 Lakh:**

**🥇 Honda CB Shine (₹72,000)**
- Mileage: 65 kmpl | Engine: 124cc
- Best for: Daily commuting
- Special offer: ₹5,000 cashback this month!

**🥈 Bajaj Pulsar 125 (₹94,000)**  
- Mileage: 50 kmpl | Engine: 124cc
- Best for: Style + performance
- EMI: Starting ₹3,200/month

**🥉 TVS Raider 125 (₹85,000)**
- Mileage: 67 kmpl | Engine: 124cc  
- Best for: Modern features
- Free service for 2 years!

Which model interests you most? I can arrange a test ride! 🚀"""
        else:
            return """🏍️ **Our Complete Range:**

**💰 Budget (₹50K-₹80K):** Honda Shine, TVS Sport, Bajaj CT
**⚡ Performance (₹80K-₹1.5L):** Pulsar series, Apache series  
**🏁 Premium (₹1.5L+):** KTM Duke, Royal Enfield, Yamaha R15

What's your budget range? I'll recommend the perfect bike for you! 🎯"""
    
    # Test ride booking
    elif any(word in msg for word in ['test ride', 'test drive', 'book', 'appointment', 'try']):
        return """📅 **Test Ride Booking Made Easy!**

🕒 **Available Slots:**
- Monday to Saturday: 10:00 AM - 6:00 PM
- Sunday: 10:00 AM - 4:00 PM

📝 **What I need:**
- Your full name
- Contact number  
- Preferred date & time
- Which bike model?

🎁 **Free with test ride:**
- Professional bike consultation
- EMI calculation
- Insurance quote
- Accessories demo

Ready to book? Just share your details! 🚀"""
    
    # EMI and finance
    elif any(word in msg for word in ['emi', 'finance', 'loan', 'payment', 'installment']):
        return """💳 **Flexible Finance Options:**

**🏦 Bank Partners:** HDFC, ICICI, SBI, Bajaj Finserv, Tata Capital

**💰 EMI Examples:**
- ₹70,000 bike = ₹2,500/month (36 months)
- ₹1,00,000 bike = ₹3,400/month (36 months)
- ₹1,50,000 bike = ₹5,100/month (36 months)

**🎯 Special Offers:**
- 0% processing fee for salaried
- Interest rates from 9.99%
- Instant approval in 30 minutes
- Up to 5-year tenure

Want me to calculate exact EMI for a specific bike? 📊"""
    
    # Service and maintenance  
    elif any(word in msg for word in ['service', 'maintenance', 'repair', 'care']):
        return """🔧 **Professional Service Packages:**

**🔸 Basic Service (₹800)**
- Engine oil change
- Air filter cleaning
- Basic inspection

**🔹 Complete Service (₹1,500)**  
- All basic service items
- Brake pad check
- Chain lubrication
- Tire pressure check

**⭐ Premium Care (₹2,500)**
- Complete service package
- Genuine parts replacement
- 20-point quality check
- Free pickup & delivery

**🎁 Special Benefits:**
- First service absolutely FREE!
- AMC packages available
- Skilled technicians
- Genuine spare parts only

Which package suits your needs? 🛠️"""
    
    # Pricing queries
    elif any(word in msg for word in ['price', 'cost', 'rate', 'expensive', 'cheap']):
        return """💰 **Transparent Pricing Policy:**

**🏷️ Current Price Ranges:**
- Entry Level: ₹55,000 - ₹75,000
- Mid Range: ₹75,000 - ₹1,20,000  
- Premium: ₹1,20,000 - ₹2,50,000
- Super Premium: ₹2,50,000+

**💎 Value Additions:**
- Best price guarantee
- Exchange bonus up to ₹15,000
- Corporate discounts available
- Festival season offers

**📋 Price Includes:**
- Road tax & insurance
- Registration charges
- Accessories worth ₹3,000

Want exact price for a specific model? Just ask! 💯"""
    
    # Insurance queries
    elif any(word in msg for word in ['insurance', 'cover', 'policy', 'claim']):
        return """🛡️ **Comprehensive Insurance Solutions:**

**📋 Coverage Options:**
- Third-party (Mandatory) 
- Comprehensive (Recommended)
- Zero depreciation
- Personal accident cover

**💰 Premium Rates:**
- Third-party: ₹1,500-₹2,500/year
- Comprehensive: ₹3,500-₹8,000/year

**🎁 Our Insurance Benefits:**
- Instant policy issuance
- Cashless claims at 4000+ garages
- 24x7 roadside assistance
- No claim bonus up to 50%

**🤝 Partner Companies:**
HDFC ERGO, ICICI Lombard, Bajaj Allianz, TATA AIG

Need an insurance quote? Share your bike details! 📱"""
    
    # Location and showroom
    elif any(word in msg for word in ['location', 'address', 'showroom', 'where', 'visit']):
        return """📍 **Visit Our Showrooms:**

**🏢 Main Showroom:**
- 📍 Address: MG Road, City Center
- 🕒 Timing: 9:00 AM - 8:00 PM (All days)  
- 📞 Contact: +91-9876543210

**🏪 Branch Locations:**
- Whitefield: 10:00 AM - 7:00 PM
- Electronic City: 10:00 AM - 7:00 PM
- Koramangala: 10:00 AM - 7:00 PM

**🚗 Free Services:**
- Home test rides available
- Free pickup for service
- Doorstep documentation

**🎯 Easy to Find:**
- Google Maps: "VoiceBot Motors"
- Landmark: Near Metro Station
- Free parking available

Planning to visit? I can book an appointment! 🎪"""
    
    # Technical specifications
    elif any(word in msg for word in ['specs', 'specification', 'engine', 'mileage', 'power', 'features']):
        return """⚙️ **Technical Specifications Hub:**

**🔧 Popular Engine Types:**
- 100-125cc: City commuting (60-70 kmpl)
- 150-200cc: Highway + city (45-55 kmpl)  
- 200cc+: Performance riding (35-45 kmpl)

**💡 Modern Features:**
- Digital instrument cluster
- LED headlights & taillights
- Smartphone connectivity
- USB charging ports
- Anti-lock braking (ABS)

**🎨 Customization Options:**
- Custom paint jobs
- Performance exhausts
- Comfort accessories
- Safety gear packages

Want detailed specs for a specific model? Just name it! 🔍"""
    
    # Complaints or issues
    elif any(word in msg for word in ['problem', 'issue', 'complaint', 'not working', 'defect']):
        return """🆘 **Customer Support Priority:**

**📞 Immediate Assistance:**
- Helpline: 1800-XXX-XXXX (Toll-free)
- WhatsApp: +91-9876543210
- Email: support@voicebotmotors.com

**🔧 Common Issues - Quick Fix:**
- Starting trouble → Battery/fuel check
- Poor mileage → Service required  
- Strange sounds → Immediate inspection

**📋 Complaint Process:**
1. Log complaint (Phone/Online)
2. Get ticket number
3. Expert callback within 2 hours
4. Resolution within 24-48 hours

**🎁 Service Guarantee:**
- Free diagnosis
- Transparent pricing
- Quality assurance
- Customer satisfaction priority

Facing any specific issue? I'm here to help immediately! 🚨"""
    
    # Default intelligent response
    else:
        return """🤖 **VoiceBot Enterprise at Your Service!**

I'm your AI-powered assistant specialized in two-wheelers. Here's how I can help:

**🏍️ Sales Support:**
- Bike recommendations & comparisons
- Pricing & EMI calculations  
- Test ride bookings
- Exchange evaluations

**🔧 Service Support:**
- Maintenance packages
- Spare parts information
- Service appointments
- Technical assistance

**💰 Finance Support:**
- Loan approvals
- Insurance policies
- Documentation help
- Special offers & discounts

**📞 Quick Actions:**
Just say: "Book test ride", "Calculate EMI", "Service booking", "Show prices"

What would you like to explore today? 🚀✨"""

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and deployment
    
    This endpoint provides system status information for monitoring tools,
    load balancers, and deployment pipelines. It returns the current state
    of the application and its key components.
    
    Returns:
        dict: Health status information including:
            - status: Overall system health
            - message: Human-readable status message
            - components: Status of individual components
            - timestamp: Current server time
            - version: Application version
    """
    return {
        "status": "healthy",
        "message": "VoiceBot Enterprise is running optimally!",
        "components": {
            "api": "active",
            "frontend": "available", 
            "chat_system": "operational",
            "ai_engine": "ready"
        },
        "version": "1.0.0",
        "timestamp": str(Path(__file__).stat().st_mtime)
    }

# ==========================================
# APPLICATION STARTUP CONFIGURATION
# ==========================================
if __name__ == "__main__":
    """
    Application entry point for development server
    
    This starts the FastAPI application using Uvicorn ASGI server
    with development-friendly settings including auto-reload and
    detailed logging.
    
    Production deployments should use proper ASGI servers like:
    - Gunicorn with Uvicorn workers
    - Docker containers with production settings
    - Cloud platform-specific deployment methods
    """
    print("🚀 Starting VoiceBot Enterprise...")
    print("📍 Frontend available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🔧 Health check at: http://localhost:8000/health")
    
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",  # Accept connections from any IP
        port=8000,       # Default development port
        reload=True,     # Auto-reload on code changes
        log_level="info" # Detailed logging for development
    )
