from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import Throttled
from ..models import users
from ..serializers import ForgetPasswordSerializer
from ..utils.users_utils import generate_otp
from ..utils.email_utils import send_otp_email
from ..utils.rate_limit import check_rate_limit

class ForgetPasswordView(APIView):
    def post(self, request):
        try:
            # Get email from request data first
            
            serializer = ForgetPasswordSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'data': {
                        'email': request.data.get('email', ''),
                        'message': 'OTP sent successfully'
                    },
                    'status': 'PASS',
                    'http_code': 200,
                    'message': 'Please check your email for OTP'
                }, status=status.HTTP_200_OK)

            # Use validated email from serializer
            email = serializer.validated_data['email']
            
            # Check rate limit
            try:
                check_rate_limit(email)
            except Throttled as e:
                return Response({
                    'data': e.detail,
                    'status': 'FAIL',
                    'http_code': 429,
                    'message': 'Too many attempts'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Get user and update OTP
            try:
                user = users.objects.get(email=email)
                otp = generate_otp()
                user.otp = otp
                user.save()

                # Send OTP Email with forget password template
                email_sent = send_otp_email(email, otp, user.name, email_type='forget_password')

                if not email_sent:
                    return Response({
                        'data': None,
                        'status': 'FAIL',
                        'http_code': 400,
                        'message': 'Failed to send OTP email'
                    }, status=status.HTTP_400_BAD_REQUEST)

                return Response({
                    'data': {
                        'email': email,
                        'message': 'OTP sent successfully'
                    },
                    'status': 'PASS',
                    'http_code': 200,
                    'message': 'Please check your email for OTP'
                }, status=status.HTTP_200_OK)

            except users.DoesNotExist:
                # Return success response even if user doesn't exist
                return Response({
                    'data': {
                        'email': email,
                        'message': 'OTP sent successfully'
                    },
                    'status': 'PASS',
                    'http_code': 200,
                    'message': 'Please check your email for OTP'
                }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'data': str(e),
                'status': 'FAIL',
                'http_code': 400,
                'message': 'Error in forget password'
            }, status=status.HTTP_400_BAD_REQUEST) 