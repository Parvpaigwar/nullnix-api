from django.http import JsonResponse, HttpResponse
import jwt
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from users.models import users
import json
from django.utils import timezone
import time
import copy

class CaptureRequestBodyMiddleware(MiddlewareMixin):
    """
    Middleware to capture and store the raw request body for logging purposes
    """
    def process_request(self, request):
        # Skip for GET requests as they don't have a body
        if request.method == 'GET':
            return None
            
        # Store the original request body
        if hasattr(request, 'body'):
            request._body = copy.copy(request.body)
        return None

class UserMiddleware(MiddlewareMixin):
    # Public endpoints that don't require authentication
    PUBLIC_ENDPOINTS = {
        "api/users/login/",
        "api/users/signup/", 
        "api/users/verify/",
        "users/handle-invitation/",
        "users/invitation-details/",
        "users/forget-password/",
        #Pricing
        "webhooks/stripe/",
        "webhooks/razorpay/",
        "google-auth",
        # GIS DATA
        "gisdata/countries/",
        "gisdata/admin-level/search/",
        "gisdata/admin-level/layers/",
        "gisdata/admin-level/datatable/",
        "gisdata/other/layers/",
        "gisdata/other/datatable/",
        # External API USER
        "v1/external",
        #Story
        "story/calculate-map-bbox/",
        "story/get-story-details-list",
        "story/get-categories/",
        "story/get-location-types/",
        "story/get-story-location-details/",
        "story/get-default-location-types/",
        "story/get-feature-details/",
        "story/get-nearby-locations/",
        "story/get-isochron-buffers/",
        "story/get-feature-details/",
        #MAPS
        "maps/details/",
        #LAYERS
        "layers/map-layers/",
        "invitation-info/",
        "verify-user/",
        "is-verified/",
        #Pricing
        "pricing/public-product-plans/",
        "pricing/webhooks/revenuecat/",
    }

    def __init__(self, get_response):
        self.get_response = get_response
        self.async_mode = False

    def get_app_name_from_url(self, path):
        # Extract app name from URL path
        # Remove leading and trailing slashes and get first segment
        parts = path.strip('/').split('/')
        return parts[0] if parts else 'unknown'

    def get_api_name_from_url(self, path):
        # Extract API name from URL path (typically the last segment)
        parts = path.strip('/').split('/')
        return parts[-1] if len(parts) > 1 else parts[0] if parts else 'unknown'

    def get_device_type(self, user_agent):
        # Simple device type detection
        user_agent = user_agent.lower() if user_agent else ''
        if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
            return 'mobile'
        elif 'tablet' in user_agent or 'ipad' in user_agent:
            return 'tablet'
        else:
            return 'desktop'

    def get_request_body(self, request):
        """Get the raw request body in a consistent way"""
        # Try to get the stored raw body if available
        if hasattr(request, '_body') and request._body:
            try:
                return request._body.decode('utf-8')
            except (UnicodeDecodeError, AttributeError):
                pass
                
        # Otherwise try to get it from request.body
        if hasattr(request, 'body'):
            try:
                return request.body.decode('utf-8')
            except (UnicodeDecodeError, AttributeError):
                pass
                
        # If all else fails, try to get data from POST or a placeholder
        try:
            return json.dumps(request.POST.dict()) if request.POST else '{}'
        except:
            return '{}'

    def log_error(self, request, response_data, status_code=500):
        try:
            # Get user ID from token if available
            userid = 0
            if hasattr(request, 'user_payload'):
                userid = request.user_payload.get('id', 0)
                
            # Skip logging for anonymous users or 401 unauthorized responses
            if userid == 0 or status_code == 401:
                return

            # For now, just print the error (you can implement database logging later)
            print(f"Error Log - User: {userid}, Status: {status_code}, Path: {request.path}")
            print(f"Response: {response_data}")
            
            # TODO: Implement database logging when error_log model is available
            # error_log.objects.create(...)
            
        except Exception as e:
            print(f"Error while logging: {str(e)}")

    def log_activity(self, request, response_data, duration_ms, status_code=200):
        try:
            # Skip GET requests
            if request.method == 'GET':
                return
                
            # Get user ID from token if available
            userid = 0
            if hasattr(request, 'user_payload'):
                userid = request.user_payload.get('id', 0)
                
            # Skip logging for anonymous users or 401 unauthorized responses
            if userid == 0 or status_code == 401:
                return

            # For now, just print the activity (you can implement database logging later)
            print(f"Activity Log - User: {userid}, Method: {request.method}, Path: {request.path}")
            print(f"Duration: {duration_ms}ms, Status: {status_code}")
            
            # TODO: Implement database logging when activity_log model is available
            # activity_log.objects.create(...)
            
        except Exception as e:
            print(f"Error while logging activity: {str(e)}")

    def __call__(self, request):
        # Start timer for request duration
        start_time = time.time()
        
        response = self.process_request(request)
        if response is None:
            response = self.get_response(request)
            
        # Calculate request duration in milliseconds
        duration_ms = int((time.time() - start_time) * 1000)
        # Store duration in request object for logging
        request.duration_ms = duration_ms
        
        # Define status codes to consider as "success" or "expected" statuses that don't need error logging
        success_status_codes = [200, 201, 202, 204, 402, 429]  # OK, Created, Accepted, No Content, Payment Required, Too Many Requests
        expected_status_codes = []  # Empty now as 402 and 429 are moved to success_status_codes
        
        # Log successful responses (status code in success_status_codes) for non-GET requests
        try:
            if hasattr(response, 'status_code') and response.status_code in success_status_codes:
                try:
                    # For JsonResponse or REST framework Response
                    if isinstance(response, (JsonResponse, Response)):
                        response_data = json.loads(response.content.decode('utf-8'))
                    # For StreamingHttpResponse - don't try to access content
                    elif hasattr(response, 'streaming_content'):
                        response_data = {
                            "message": "Success",
                            "status": "PASS",
                            "data": "Streaming response - content not available"
                        }
                    # For regular HttpResponse
                    else:
                        response_data = {
                            "message": "Success",
                            "status": "PASS",
                            "data": str(response.content[:100]) + "..." if len(response.content) > 100 else str(response.content)
                        }
                    # Wrap the logging call in try-except to prevent any logging issues affecting the response
                    try:
                        # Only log non-GET requests as activity
                        if request.method != 'GET':
                            self.log_activity(request, response_data, duration_ms, response.status_code)
                    except Exception as e:
                        print(f"Error in activity logging: {str(e)}")
                except Exception as e:
                    print(f"Error processing response for logging: {str(e)}")
        except Exception as e:
            print(f"Error in response handling: {str(e)}")
        
        # Log any response that's not a success and not in the expected status codes list
        try:
            if (hasattr(response, 'status_code') and 
                response.status_code not in success_status_codes):
                try:
                    # For JsonResponse or REST framework Response
                    if isinstance(response, (JsonResponse, Response)):
                        response_data = json.loads(response.content.decode('utf-8'))
                    # For StreamingHttpResponse - don't try to access content
                    elif hasattr(response, 'streaming_content'):
                        response_data = {
                            "message": "Streaming response error",
                            "status": "FAIL",
                            "data": "Streaming response - content not available"
                        }
                    # For regular HttpResponse
                    else:
                        response_data = {
                            "message": response.reason_phrase if hasattr(response, 'reason_phrase') else str(response.content),
                            "status": "FAIL",
                            "data": str(response.content)
                        }
                    # Wrap the logging call in try-except to prevent any logging issues affecting the response
                    try:
                        self.log_error(request, response_data, response.status_code)
                    except Exception as e:
                        print(f"Error in error logging: {str(e)}")
                except Exception as e:
                    # If we can't decode the response, create a basic error log
                    response_data = {
                        "message": "Unknown error",
                        "status": "FAIL",
                        "data": f"Status code: {response.status_code}"
                    }
                    try:
                        self.log_error(request, response_data, response.status_code)
                    except Exception as e:
                        print(f"Error in fallback error logging: {str(e)}")
        except Exception as e:
            print(f"Error in error response handling: {str(e)}")
        
        return response

    def get_token(self, request, api_req):
        """Extract token from request based on endpoint type"""
        token = None
        token = request.headers.get('Authorization')

        # Remove Bearer prefix if present
        if token and token.startswith('Bearer '):
            token = token[7:]
        
        return token

    def process_request(self, request):
        try:
            # Skip if superadmin API
            if request.path.startswith('/superadmin/'):
                return None

            # Check if this is a public endpoint - more precise matching
            request_path = request.path.strip('/')
            
            # Direct path matching for public endpoints
            if request_path in self.PUBLIC_ENDPOINTS:
                return None
                
            # Also check the original PUBLIC_ENDPOINTS logic
            for endpoint in self.PUBLIC_ENDPOINTS:
                endpoint_clean = endpoint.strip('/')
                if request_path == endpoint_clean or request_path.startswith(endpoint_clean + '/'):
                    return None

            # Get token
            token = self.get_token(request, str(request))
            if not token:
                return JsonResponse({
                    "message": "Missing token",
                    "status": "FAIL",
                    "data": "Token required"
                }, status=status.HTTP_401_UNAUTHORIZED)

            try:
                # Validate user token
                payload = jwt.decode(
                    token, 
                    settings.JWT_USER_SECRET, 
                    algorithms=["HS256"]
                )

                if payload.get('role') != 'user':
                    return JsonResponse({
                        "message": "Not a user token",
                        "status": "FAIL",
                        "data": "Invalid token type"
                    }, status=status.HTTP_401_UNAUTHORIZED)

                # Store the validated user info in request for views to use
                request.user_payload = payload

                # Verify user and company association
                user_exists = users.objects.filter(
                    id=payload['id'],
                    email=payload['email']
                ).exists()


                if not (user_exists):
                    return JsonResponse({
                        "message": "Invalid user association",
                        "status": "FAIL",
                        "data": "User or company not found"
                    }, status=status.HTTP_401_UNAUTHORIZED)

                return None

            except jwt.ExpiredSignatureError:
                return JsonResponse({
                    "message": "Token has expired",
                    "status": "FAIL",
                    "data": "Token expired"
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            except jwt.InvalidTokenError as e:
                return JsonResponse({
                    "message": "Invalid token",
                    "status": "FAIL",
                    "data": str(e)
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            except Exception as e:
                return JsonResponse({
                    "message": "Token validation error",
                    "status": "FAIL",
                    "data": str(e)
                }, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return JsonResponse({
                "message": "Authentication error",
                "status": "FAIL",
                "data": str(e)
            }, status=status.HTTP_401_UNAUTHORIZED) 