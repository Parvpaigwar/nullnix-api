# Create your views here.
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import users
from users.serializers import UserLoginSerializer, UserSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import hashlib
from datetime import datetime
from users.utils.token_utilis import create_user_token
import logging


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
