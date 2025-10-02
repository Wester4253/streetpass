from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
import asyncio

class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute=60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        now = time.time()
        
        # Clean old requests
        self.requests[client_ip] = [req_time for req_time in self.requests[client_ip]
                                  if now - req_time < 60]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return Response(
                content="Too many requests",
                status_code=429,
                headers={"Retry-After": "60"}
            )
        
        # Add current request
        self.requests[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        return response