import django
from rest_framework import serializers
from .models import users

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = ['name', 'email', "country"]

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True, min_length=6)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = [
            'id', 'name', 'email', 'login_methode', 'contact_no', 
            'country', 'user_schema', 'is_verified', 'created_on', 
            'modified_on',"otp"
        ]
        read_only_fields = ['id', 'created_on', 'modified_on']



class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        email = value.lower()
        # Don't raise error if user doesn't exist for security reasons
        # Just return the email - the view will handle the logic
        return email 