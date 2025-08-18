from django.core.cache import cache
from rest_framework.exceptions import Throttled
from datetime import datetime, timedelta

def check_rate_limit(email, max_attempts=3, timeout_minutes=30):
    """
    Check if user has exceeded rate limit for forget password attempts
    
    Args:
        email: User's email
        max_attempts: Maximum number of attempts allowed
        timeout_minutes: Timeout period in minutes
    """
    cache_key = f"forget_password_{email}"
    attempts = cache.get(cache_key, {"count": 0, "first_attempt": None})

    # Reset attempts if timeout has passed
    if attempts["first_attempt"] and datetime.now() - attempts["first_attempt"] > timedelta(minutes=timeout_minutes):
        attempts = {"count": 0, "first_attempt": None}

    # Update attempts
    if attempts["count"] >= max_attempts:
        time_passed = datetime.now() - attempts["first_attempt"]
        minutes_left = timeout_minutes - (time_passed.total_seconds() / 60)
        raise Throttled(
            detail={
                "message": f"Too many attempts. Please try again after {int(minutes_left)} minutes.",
                "minutes_left": int(minutes_left)
            }
        )

    # Increment attempt count
    if attempts["count"] == 0:
        attempts["first_attempt"] = datetime.now()
    attempts["count"] += 1
    
    # Set cache with timeout
    cache.set(cache_key, attempts, timeout=timeout_minutes * 60) 