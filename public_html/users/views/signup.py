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
from users.serializers import UserSignupSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import hashlib
import logging
from users.utils.users_utils import generate_otp, generate_schema_name

logger = logging.getLogger(__name__)


import logging

logger = logging.getLogger(__name__)

class SignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user_exists = users.objects.filter(email=email).exists()
            if user_exists:
                return Response(
                    {"detail": "User already exists. Please login."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                gen_otp = generate_otp()

                user = users.objects.create(
                    name=serializer.validated_data['name'],
                    email=email,
                    is_verified=False,
                    otp=gen_otp,
                    country=serializer.validated_data['country'],
                )
                user.save()

                schema_name = generate_schema_name(user.id)
                user.user_schema = schema_name
                user.save()

                send_otp_email(email, gen_otp, serializer.validated_data['name'])

                return Response({"detail": "OTP sent to your email."}, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.exception("Signup error")  # 👈 full traceback in logs
                return Response(
                    {"detail": f"Internal error: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

