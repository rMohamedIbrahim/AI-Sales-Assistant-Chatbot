"""
Middleware implementation for request handling, authentication, and monitoring.
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.config import get_settings
from src.infrastructure.logging import logger
from src.domain.exceptions import RateLimitExceededError
import time
import uuid
from prometheus_client import Counter, Histogram

settings = get_settings()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'voicebot_request_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'voicebot_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

class MonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        # Start timing
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(time.time() - start_time)
            
            # Add correlation ID to response headers
            response.headers['X-Correlation-ID'] = correlation_id
            
            return response
            
        except Exception as e:
            logger.exception(
                "Request processing failed",
                extra={
                    'correlation_id': correlation_id,
                    'url': str(request.url),
                    'method': request.method,
                    'error': str(e)
                }
            )
            raise

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Get client IP safely
        client_ip = getattr(request.client, 'host', '127.0.0.1') if request.client else '127.0.0.1'
        current_time = time.time()
        
        # Clean up old requests
        self.cleanup_old_requests(current_time)
        
        # Check rate limit
        if self.is_rate_limited(client_ip, current_time):
            raise RateLimitExceededError()
        
        # Process request
        response = await call_next(request)
        
        return response

    def cleanup_old_requests(self, current_time: float):
        """Remove requests older than the rate limit period"""
        cutoff = current_time - settings.RATE_LIMIT_PERIOD
        
        for ip in list(self.requests.keys()):
            self.requests[ip] = [
                timestamp for timestamp in self.requests[ip]
                if timestamp > cutoff
            ]
            if not self.requests[ip]:
                del self.requests[ip]

    def is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if client has exceeded rate limit"""
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        self.requests[client_ip].append(current_time)
        
        return len(self.requests[client_ip]) > settings.RATE_LIMIT_CALLS
