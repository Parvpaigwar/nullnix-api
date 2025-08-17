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
from .models import users
from .serializers import UserSignupSerializer, UserLoginSerializer, VerifyOtpSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import hashlib
from datetime import datetime
from users.utils.token_utilis import create_user_token


def generate_otp():
    return str(random.randint(100000, 999999))

def generate_schema_name(userid):
    """Generate encoded schema name for company using same pattern as original"""
    base = f"company_{userid}"
    encoded = hashlib.md5(base.encode()).hexdigest()
    return f"c{userid}{encoded[:8]}"  # Returns format like 'c123412345678'

class SignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user_exists = users.objects.filter(email=email).exists()
            if user_exists:
                return Response({"detail": "User already exists. Please login."}, status=status.HTTP_400_BAD_REQUEST)

            
            gen_otp = generate_otp()

            user = users.objects.create(
                name=serializer.validated_data['name'],
                email=email,
                is_verified=False,
                otp=gen_otp,
                country=serializer.validated_data['country'],  # Optional field
            )
            user.save()
                        
            # Generate schema after user creation to use user_id
            schema_name = generate_schema_name(user.id)
            user.user_schema = schema_name
            user.save()


            # # Send OTP Email
            # send_mail(
            #     'Your Nullnix Signup OTP',
            #     f'Your OTP code is {user.otp}',
            #     None,
            #     [user.email],
            #     fail_silently=False,
            # )
            # 4. Send OTP Email
            try:
                send_otp_email(email, gen_otp, serializer.validated_data['name'])
            except Exception as e:
                print(f"Error sending OTP email: {str(e)}")
                return Response({f"detail": f"Failed to send OTP email. error - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"detail": "OTP sent to your email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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

class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                user = users.objects.get(email=email)
            except users.DoesNotExist:
                return Response({"detail": "User not found. Please signup."}, status=status.HTTP_404_NOT_FOUND)

            if not user.is_verified:
                return Response({"detail": "User not verified. Please verify OTP first."}, status=status.HTTP_401_UNAUTHORIZED)

            # Hash the input password and compare with stored hash
            hashed_password = hashlib.sha1(password.encode()).hexdigest()
            if user.password != hashed_password:
                return Response({"detail": "Invalid password."}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate token
            token = create_user_token(user)
            
            # Serialize user data
            user_data = UserSerializer(user).data

            return Response({
                "detail": "Login successful.",
                "token": token,
                "user": user_data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
