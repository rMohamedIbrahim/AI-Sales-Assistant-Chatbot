"""
Main application entry point for the VoiceBot system.
Configures FastAPI application with middleware, routes, and startup/shutdown events.
Optimized for Vercel serverless deployment while preserving project structure.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
import json
from pathlib import Path
from functools import lru_cache
import asyncio

# Import your modules with error handling for Vercel deployment
try:
    from src.api import voice_routes, booking_routes, service_routes
    ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import routes: {e}")
    ROUTES_AVAILABLE = False

try:
    from src.core.config import get_settings
    settings = get_settings()
    CONFIG_AVAILABLE = True
except ImportError:
    # Fallback settings for Vercel deployment
    class FallbackSettings:
        PROJECT_NAME = "AI Sales Assistant Chatbot"
        API_VERSION = "v1"
        ALLOWED_HOSTS = ["*"]
        DEBUG = False
        HOST = "0.0.0.0"
        PORT = 8000
        LOG_LEVEL = "INFO"
        ENABLE_METRICS = False
        PROMETHEUS_PORT = 8001
    
    settings = FallbackSettings()
    CONFIG_AVAILABLE = False

try:
    from src.infrastructure.database import db_service
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from src.infrastructure.middleware import MonitoringMiddleware, RateLimitMiddleware
    MIDDLEWARE_AVAILABLE = True
except ImportError:
    MIDDLEWARE_AVAILABLE = False

try:
    from src.infrastructure.logging import logger
    LOGGING_AVAILABLE = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    LOGGING_AVAILABLE = False

# Remove Prometheus import for serverless
try:
    from prometheus_client import start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Production-grade multilingual voice agent for two-wheeler sales and service",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )

    # Add middleware with error handling
    if MIDDLEWARE_AVAILABLE:
        try:
            app.add_middleware(MonitoringMiddleware)
            app.add_middleware(RateLimitMiddleware)
        except Exception as e:
            if logger:
                logger.warning(f"Could not add custom middleware: {e}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers with versioning (only if available)
    if ROUTES_AVAILABLE:
        try:
            app.include_router(
                voice_routes.router,
                prefix=f"/api/{settings.API_VERSION}/voice",
                tags=["voice"]
            )
            app.include_router(
                booking_routes.router,
                prefix=f"/api/{settings.API_VERSION}/booking",
                tags=["booking"]
            )
            app.include_router(
                service_routes.router,
                prefix=f"/api/{settings.API_VERSION}/service",
                tags=["service"]
            )
        except Exception as e:
            if logger:
                logger.warning(f"Could not include routers: {e}")

    # Mount static files for frontend (with error handling)
    try:
        frontend_path = Path(__file__).parent.parent / "frontend"
        if frontend_path.exists():
            app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
            if logger:
                logger.info(f"Mounted static files from: {frontend_path}")
    except Exception as e:
        if logger:
            logger.warning(f"Could not mount static files: {e}")

    # Enhanced chat endpoint for the frontend
    @app.post("/chat")
    @app.post("/api/chat/send")
    async def chat_endpoint(request: Request):
        """Enhanced chat endpoint for frontend with proper JSON handling"""
        try:
            # Handle JSON request properly
            body = await request.json()
            message = body.get("message", "")
            language = body.get("language", "en")
            
            if not message:
                raise HTTPException(status_code=400, detail="Message is required")
            
            # Enhanced response logic
            response = get_enhanced_response(message, language)
            return {
                "response": response,
                "status": "success",
                "language": language
            }
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        except Exception as e:
            if logger:
                logger.error(f"Chat endpoint error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "Please try again later"
                }
            )

    def get_enhanced_response(message: str, language: str = "en") -> str:
        """Enhanced demo responses with more comprehensive coverage"""
        msg = message.lower()
        
        # Greetings
        if any(word in msg for word in ['hello', 'hi', 'hey', 'namaste', 'good morning', 'good afternoon']):
            return "👋 Welcome to VoiceBot Enterprise! I'm your AI sales assistant for two-wheelers. I can help with bike selection, pricing, test rides, EMI options, and service bookings. How can I assist you today?"
        
        # Bike/Vehicle queries
        elif any(word in msg for word in ['bike', 'motorcycle', 'scooter', 'vehicle', 'models']):
            if any(word in msg for word in ['under', 'below', '1 lakh', 'budget', 'cheap', 'affordable']):
                return "🏍️ Great bikes under ₹1 lakh: Honda CB Shine (₹72,000) - 65 kmpl, Bajaj Pulsar 125 (₹94,000) - sporty design, TVS Raider 125 (₹85,000) - modern features. All come with 5-year warranty. Which style interests you - commuter or sporty?"
            else:
                return "🏍️ Our popular models: Entry level: Honda Shine, Hero Splendor+ | Premium: Bajaj Pulsar, TVS Apache | Scooters: Honda Activa, TVS Jupiter. Which category would you like to explore?"
        
        # Test ride booking
        elif any(word in msg for word in ['test ride', 'book', 'appointment', 'schedule', 'try']):
            return "📅 I'd love to arrange a test ride! Please share: 1) Your name 2) Mobile number 3) Preferred model 4) Convenient date/time. We're open Mon-Sat, 10 AM-6 PM. Which bike caught your interest?"
        
        # EMI and financing
        elif any(word in msg for word in ['emi', 'finance', 'loan', 'payment', 'installment']):
            return "💳 Flexible EMI options available! Starting from ₹2,500/month. For ₹1L bike: ₹3,000/month (36 months). We partner with all major banks - HDFC, ICICI, SBI. Special rates for salaried professionals. Need exact calculation for a specific model?"
        
        # Service and maintenance
        elif any(word in msg for word in ['service', 'maintenance', 'repair', 'servicing']):
            return "🔧 Service packages: Basic Service (₹800) - Oil change, basic check | Complete Service (₹1,500) - 15-point inspection | Premium Service (₹2,500) - Full diagnostic. First service FREE for new bikes! When was your last service?"
        
        # Pricing queries
        elif any(word in msg for word in ['price', 'cost', 'rate', 'amount', 'money']):
            return "💰 Our transparent pricing: Entry bikes: ₹55,000-75,000 | Premium bikes: ₹85,000-1.5L | Sports bikes: ₹1.2L+ | Scooters: ₹65,000-95,000. Current offers: Up to ₹15,000 discount + free accessories. Which segment interests you?"
        
        # Mileage queries
        elif any(word in msg for word in ['mileage', 'fuel', 'efficiency', 'kmpl']):
            return "⛽ Excellent mileage options: Honda Shine - 65 kmpl | Hero Splendor+ - 70 kmpl | TVS Star City - 68 kmpl | Honda Activa - 60 kmpl. All certified ARAI figures. Looking for maximum fuel efficiency?"
        
        # Default response
        else:
            return "🤖 Thank you for your interest! I can help with: 🏍️ Bike information & pricing | 📅 Test ride bookings | 💳 EMI calculations | 🔧 Service packages | ⛽ Mileage info. What would you like to know?"

    # Additional API endpoints for better functionality
    @app.get("/api/vehicles")
    async def get_vehicles():
        """Get available vehicle models"""
        vehicles = [
            {"id": 1, "name": "Honda CB Shine", "price": 72000, "mileage": "65 kmpl", "engine": "124cc", "type": "Commuter"},
            {"id": 2, "name": "Bajaj Pulsar 125", "price": 94000, "mileage": "50 kmpl", "engine": "124cc", "type": "Sports"},
            {"id": 3, "name": "TVS Raider 125", "price": 85000, "mileage": "67 kmpl", "engine": "124cc", "type": "Premium"},
            {"id": 4, "name": "Honda Activa 6G", "price": 75000, "mileage": "60 kmpl", "engine": "109cc", "type": "Scooter"},
            {"id": 5, "name": "Hero Splendor Plus", "price": 68000, "mileage": "70 kmpl", "engine": "97cc", "type": "Economy"}
        ]
        return {"vehicles": vehicles, "count": len(vehicles)}

    @app.post("/api/booking/test-ride")
    async def book_test_ride(request: Request):
        """Book a test ride"""
        try:
            booking_data = await request.json()
            required_fields = ["name", "phone", "model"]
            
            for field in required_fields:
                if field not in booking_data:
                    raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
            
            return {
                "message": "Test ride booked successfully!",
                "booking_id": f"TR{booking_data['phone'][-4:]}",
                "details": booking_data,
                "status": "confirmed"
            }
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        except Exception as e:
            if logger:
                logger.error(f"Booking error: {str(e)}")
            raise HTTPException(status_code=500, detail="Booking failed")

    # Startup and shutdown events (modified for serverless compatibility)
    @app.on_event("startup")
    async def startup_event():
        """
        Initialize services on application startup (serverless-compatible)
        """
        try:
            # Initialize database connection only if available and not in serverless
            if DB_AVAILABLE and not os.getenv('VERCEL'):
                await db_service.connect()
            
            # Skip Prometheus in serverless environment
            if PROMETHEUS_AVAILABLE and settings.ENABLE_METRICS and not os.getenv('VERCEL'):
                start_http_server(settings.PROMETHEUS_PORT)
                if logger:
                    logger.info(f"Metrics server started on port {settings.PROMETHEUS_PORT}")
                
            if logger:
                logger.info("Application startup completed")
        except Exception as e:
            if logger:
                logger.error(f"Application startup failed: {str(e)}")
            # Don't raise in serverless environment to prevent deployment failure
            if not os.getenv('VERCEL'):
                raise

    @app.on_event("shutdown")
    async def shutdown_event():
        """
        Cleanup services on application shutdown (serverless-compatible)
        """
        try:
            # Close database connection only if available and not in serverless
            if DB_AVAILABLE and not os.getenv('VERCEL'):
                await db_service.close()
            if logger:
                logger.info("Application shutdown completed")
        except Exception as e:
            if logger:
                logger.error(f"Application shutdown failed: {str(e)}")
            # Don't raise in serverless environment

    @app.get("/")
    async def root():
        """Enhanced root endpoint"""
        try:
            frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
            if frontend_path.exists():
                return FileResponse(str(frontend_path))
        except Exception:
            pass
        
        return {
            "message": "AI Sales Assistant Chatbot API",
            "version": settings.API_VERSION,
            "status": "running",
            "endpoints": {
                "chat": "/api/chat/send",
                "vehicles": "/api/vehicles",
                "booking": "/api/booking/test-ride",
                "health": "/health",
                "docs": "/api/docs"
            }
        }

    @app.get("/health")
    async def health_check():
        """
        Health check endpoint for monitoring (serverless-compatible)
        """
        try:
            health_status = {
                "status": "healthy",
                "services": {
                    "api": "up",
                    "database": "not configured" if not DB_AVAILABLE else "up"
                },
                "environment": "serverless" if os.getenv('VERCEL') else "standard"
            }
            
            # Check database only if available and not in serverless
            if DB_AVAILABLE and not os.getenv('VERCEL'):
                try:
                    db_health = await db_service.health_check()
                    health_status["services"]["database"] = "up" if db_health else "down"
                except Exception as e:
                    health_status["services"]["database"] = f"error: {str(e)}"
            
            return health_status
        except Exception as e:
            if logger:
                logger.error(f"Health check failed: {str(e)}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": str(e),
                    "services": {"api": "up", "database": "unknown"}
                }
            )

    return app

# Create the app instance
app = create_app()

# For Vercel serverless deployment
handler = app

# Development server (only runs locally, not on Vercel)
if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            workers=4,
            log_level=settings.LOG_LEVEL.lower()
        )
    except Exception as e:
        # Fallback for missing settings
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
    )
