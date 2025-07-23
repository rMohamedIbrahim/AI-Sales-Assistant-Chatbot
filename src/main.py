"""
Main application entry point for the VoiceBot system.
Configures FastAPI application with middleware, routes, and startup/shutdown events.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.api import voice_routes, booking_routes, service_routes
from src.core.config import get_settings
from src.infrastructure.database import db_service
from src.infrastructure.middleware import MonitoringMiddleware, RateLimitMiddleware
from src.infrastructure.logging import logger
from prometheus_client import start_http_server
import uvicorn
import asyncio
import os
from pathlib import Path

settings = get_settings()

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

    # Add middleware
    app.add_middleware(MonitoringMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers with versioning
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

    # Mount static files for frontend
    frontend_path = Path(__file__).parent.parent / "frontend"
    if frontend_path.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
        logger.info(f"Mounted static files from: {frontend_path}")
    else:
        logger.warning(f"Frontend directory not found: {frontend_path}")

    # Add chat endpoint for the frontend
    @app.post("/chat")
    async def chat_endpoint(request: dict):
        """Simple chat endpoint for frontend"""
        try:
            message = request.get("message", "")
            if not message:
                raise HTTPException(status_code=400, detail="Message is required")
            
            # Simple response logic for demo
            response = get_demo_response(message)
            return {"response": response}
        except Exception as e:
            logger.error(f"Chat endpoint error: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_demo_response(message: str) -> str:
        """Generate demo responses for the chat"""
        msg = message.lower()
        
        if any(word in msg for word in ['bike', 'motorcycle', 'scooter', 'under', 'lakh']):
            return "🏍️ We have excellent bikes under 1 lakh! Popular models: Honda CB Shine (₹72,000), Bajaj Pulsar 125 (₹94,000), TVS Raider 125 (₹85,000). All with great mileage and warranty. Which model interests you?"
        elif any(word in msg for word in ['test ride', 'book', 'appointment']):
            return "📅 I'd be happy to book a test ride! Please share: Name, Contact, Preferred date/time. Available Mon-Sat, 10 AM-6 PM. Which bike would you like to test?"
        elif any(word in msg for word in ['emi', 'finance', 'loan', 'payment']):
            return "💳 Flexible EMI from ₹2,500/month! We work with all major banks. For ₹1L bike: EMI starts ₹3,000 for 36 months. Lower rates for salaried professionals. Need EMI calculation for specific model?"
        elif any(word in msg for word in ['service', 'maintenance', 'repair']):
            return "🔧 Service packages: Basic (₹800), Complete (₹1,500), Premium (₹2,500). Includes oil change, brake check, 20-point inspection. First service FREE! Which package interests you?"
        elif any(word in msg for word in ['price', 'cost', 'rate']):
            return "💰 Our competitive pricing: Entry bikes from ₹55,000, Premium from ₹85,000, Sports from ₹1.2L. Special discounts available! Looking for any specific category?"
        elif any(word in msg for word in ['hello', 'hi', 'hey']):
            return "👋 Welcome to VoiceBot Enterprise! I'm your AI sales assistant for two-wheelers. I can help with bike selection, pricing, test rides, EMI options, and service bookings. How can I assist you today?"
        else:
            return "🤖 Thank you for your interest! I can help with: 🏍️ Bike information & pricing, 📅 Test ride bookings, 💳 EMI calculations, 🔧 Service packages. What would you like to know?"

    @app.on_event("startup")
    async def startup_event():
        """
        Initialize services on application startup
        """
        try:
            # Initialize database connection
            await db_service.connect()
            
            # Start Prometheus metrics server if enabled
            if settings.ENABLE_METRICS:
                start_http_server(settings.PROMETHEUS_PORT)
                logger.info(f"Metrics server started on port {settings.PROMETHEUS_PORT}")
                
            logger.info("Application startup completed")
        except Exception as e:
            logger.error(f"Application startup failed: {str(e)}")
            raise

    @app.on_event("shutdown")
    async def shutdown_event():
        """
        Cleanup services on application shutdown
        """
        try:
            # Close database connection
            await db_service.close()
            logger.info("Application shutdown completed")
        except Exception as e:
            logger.error(f"Application shutdown failed: {str(e)}")
            raise

    @app.get("/")
    async def root():
        """Serve the enterprise frontend"""
        frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
        if frontend_path.exists():
            return FileResponse(str(frontend_path))
        return {
            "message": "Two-Wheeler Sales VoiceBot API",
            "version": settings.API_VERSION,
            "docs_url": "/api/docs",
            "frontend": "Frontend files not found"
        }

    @app.get("/health")
    async def health_check():
        """
        Health check endpoint for monitoring
        """
        try:
            # Check database connection (SQLite doesn't need ping)
            db_health = await db_service.health_check()
            return {
                "status": "healthy",
                "services": {
                    "api": "up",
                    "database": "up" if db_health else "down"
                }
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "services": {
                    "api": "up",
                    "database": "down"
                },
                "error": str(e)
            }

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=4,
        log_level=settings.LOG_LEVEL.lower()
    )
