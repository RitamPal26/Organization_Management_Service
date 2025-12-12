from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self, calls: int = 100, period: int = 60):
        """
        Rate limiter: allows 'calls' requests per 'period' seconds
        """
        self.calls = calls
        self.period = period
        self.storage: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, key: str) -> Tuple[bool, int]:
        """Check if request is allowed, return (allowed, remaining_calls)"""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.period)
        
        # Remove old entries
        self.storage[key] = [ts for ts in self.storage[key] if ts > cutoff]
        
        # Check if limit exceeded
        if len(self.storage[key]) >= self.calls:
            return False, 0
        
        # Add current request
        self.storage[key].append(now)
        remaining = self.calls - len(self.storage[key])
        return True, remaining

# Global rate limiter instance
rate_limiter = RateLimiter(calls=100, period=60)  # 100 requests per minute


async def check_rate_limit(request: Request):
    """Dependency to check rate limit"""
    client_ip = request.client.host
    allowed, remaining = rate_limiter.is_allowed(client_ip)
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )
    
    return remaining
