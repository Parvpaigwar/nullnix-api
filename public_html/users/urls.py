from django.urls import path
from .views.login import LoginView
from .views.signup import SignupView 
from .views.verify import VerifyOTPView
from .views.google_auth import GoogleAuthView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("verify/", VerifyOTPView.as_view(), name="verify-otp"),
    path("login/", LoginView.as_view(), name="login"),
    path("google-auth/", GoogleAuthView.as_view(), name="google-auth"),
]
