import jwt
from datetime import datetime, timedelta
from nullnix import settings
from users.models import users
from rest_framework.exceptions import AuthenticationFailed

def get_user_from_token(request):
    """
    Extract user information from JWT token
    Returns: user_obj
    """
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise AuthenticationFailed('No token provided')

        # Decode token
        token_data = jwt.decode(auth_header, settings.JWT_USER_SECRET, algorithms=["HS256"])
        
        # Get user
        user = users.objects.get(id=token_data['id'], email=token_data['email'])
            
        return user
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')
    except users.DoesNotExist:
        raise AuthenticationFailed('User not found')
    except Exception as e:
        raise AuthenticationFailed(str(e))

def create_user_token(user):
    """
    Create JWT token for user
    Args:
        user: users object
    Returns:
        str: JWT token
    """
    try:
        token = jwt.encode({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'login_methode': user.login_methode,
            'is_verified': user.is_verified,
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(days=365)
        }, settings.JWT_USER_SECRET, algorithm="HS256")
        
        return token
    except Exception as e:
        raise AuthenticationFailed(f'Error creating token: {str(e)}')