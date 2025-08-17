import random
import hashlib
import logging

logger = logging.getLogger(__name__)



def generate_otp():
    return str(random.randint(100000, 999999))

def generate_schema_name(userid):
    """Generate encoded schema name for company using same pattern as original"""
    base = f"company_{userid}"
    encoded = hashlib.md5(base.encode()).hexdigest()
    return f"c{userid}{encoded[:8]}"  # Returns format like 'c123412345678'