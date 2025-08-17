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
from users.serializers import UserSignupSerializer, UserLoginSerializer, VerifyOtpSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import hashlib
from datetime import datetimeS
from users.utils.token_utilis import create_user_token
import logging