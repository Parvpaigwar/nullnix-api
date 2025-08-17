from huggingface_hub import login
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import logging
from django.conf import settings

from ..models import users
from ..serializers import UserSerializer
from users.utils.users_utils import generate_otp, generate_schema_name
from users.utils.token_utilis import create_user_token
logger = logging.getLogger(__name__)

class GoogleAuthView(APIView):
    def get(self, request):
        try:
            access_token = request.query_params.get('access_token')
            if not access_token:
                return Response({
                    'data': None,
                    'status': 'FAIL',
                    'http_code': 400,
                    'message': 'access_token is required in query parameters'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get user info from Google
            headers = {'Authorization': f'Bearer {access_token}'}
            google_response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers=headers
            )
            
            if google_response.status_code != 200:
                return Response({
                    'data': None,
                    'status': 'FAIL',
                    'http_code': 400,
                    'message': 'Invalid Google access token'
                }, status=status.HTTP_400_BAD_REQUEST)

            google_data = google_response.json()
            email = google_data['email']
            name = google_data.get('name', '')
            
            is_new_user = False
            # Check if user exists
            try:
                user = users.objects.get(email=email)
                # If user exists but not verified, verify them
                if not user.is_verified:
                    user.is_verified = True
                    user.save()
                    is_new_user = True
                
                # Update login method if it was NORMAL
                if user.login_methode == 'NORMAL':
                    user.login_methode = 'GOOGLE'
                    user.save()

            except users.DoesNotExist:
                # Create new user
                user = users.objects.create(
                    name=name,
                    email=email,
                    is_verified=False,
                    otp=0,
                    country='',
                    login_method='GOOGLE'
                )
                user.save()
                schema_name = generate_schema_name(user.id)
                user.user_schema = schema_name
                user.save()
                is_new_user = True
            # Generate JWT token with company_id from company_users
            token = create_user_token(user)

            # If token is bytes, decode to string
            if isinstance(token, bytes):
                token = token.decode('utf-8')

            # Serialize user data
            user_data = UserSerializer(user).data

            return Response({
                'data': {
                    'token': token,
                    'user': user_data
                },
                'status': 'PASS',
                'http_code': 200,
                'message': 'Successfully logged in with Google'
            })

        except Exception as e:
            return Response({
                'data': str(e),
                'status': 'FAIL',
                'http_code': 400,
                'message': 'Error in Google authentication'
            }, status=status.HTTP_400_BAD_REQUEST) 
        