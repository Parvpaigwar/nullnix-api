from django.urls import path
from .views.login import LoginView
from .views.signup import SignupView 
from .views.verify import VerifyOTPView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("verify/", VerifyOTPView.as_view(), name="verify-otp"),
    path("login/", LoginView.as_view(), name="login"),
]
