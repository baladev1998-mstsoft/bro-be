import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = (time.time() - start_time) * 1000
            formatted_process_time = f"{process_time:.2f}ms"
            
            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {formatted_process_time}",
                extra={
                    "context": {
                        "file": __file__,
                        "line": 23, # Approximate line number
                        "function": "dispatch",
                        "module": "middleware"
                    },
                    "duration": formatted_process_time
                }
            )
            
            return response
        except Exception as e:
            # Exception logging is handled by global exception handler, 
            # but we can log the duration here if needed.
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"- Duration: {process_time:.2f}ms"
            )
            raise e
