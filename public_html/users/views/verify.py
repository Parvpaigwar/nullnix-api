from email import utils
from django.shortcuts import render 
from users.utils.email_utils import send_otp_email


# Create your views here.
from django.shortcuts import render

# Create your views here.
import random
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import users
from users.serializers import  VerifyOtpSerializer, UserSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import hashlib
from users.utils.token_utilis import create_user_token
import logging
logger = logging.getLogger(__name__)




class VerifyOTPView(APIView):
    def post(self, request):
        try:
            serializer = VerifyOtpSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'data': serializer.errors,
                    'status': 'FAIL',
                    'http_code': 400,
                    'message': 'Invalid input data'
                }, status=status.HTTP_400_BAD_REQUEST)

            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            password = serializer.validated_data['password']

            # Get user and verify OTP
            user = users.objects.get(email=email)
            
            if user.otp != otp:
                return Response({
                    'data': None,
                    'status': 'FAIL',
                    'http_code': 400,
                    'message': 'Invalid OTP'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Hash password using SHA1 (maintaining compatibility)
            hashed_password = hashlib.sha1(password.encode()).hexdigest()
            
            # Update user
            user.password = hashed_password
            user.is_verified = True
            user.save()

            # Generate token
            token = create_user_token(user)

            # Serialize user data
            user_data = UserSerializer(user).data

            return Response({
                'data': {
                    'token': token,
                    'user': user_data
                },
                'status': 'PASS',
                'http_code': 200,
                'message': 'Email verified and logged in successfully'
            })

        except users.DoesNotExist:
            return Response({
                'data': None,
                'status': 'FAIL',
                'http_code': 400,
                'message': 'User not found'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'data': str(e),
                'status': 'FAIL',
                'http_code': 400,
                'message': 'Error in verification'
            }, status=status.HTTP_400_BAD_REQUEST) 