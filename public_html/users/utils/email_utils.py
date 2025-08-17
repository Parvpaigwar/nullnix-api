from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_otp_email(email, otp, username='', email_type='verification'):
    try:
        if email_type == 'verification':
            subject = 'NULLNIX Email Verification'
            template = 'emails/verification_otp.html'
        else:  # forget password
            subject = 'NULLNIX Password Reset'
            template = 'emails/forget_password_otp.html'
        
        print(f"Attempting to send email to: {email}")
        print(f"Using template: {template}")
        
        # Context for email template
        context = {
            'username': username or email,
            'otp': otp
        }
        
        print(f"Email context: {context}")
        
        # Get HTML content from template
        html_content = render_to_string(template, context)
        text_content = strip_tags(html_content)
        
        print("Email content generated successfully")
        
        # Create email message
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [email]
        )
        msg.attach_alternative(html_content, "text/html")
        
        print("Email message created, attempting to send...")
        
        # Send email
        msg.send()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False 

def send_company_invitation_email(email, company_name, inviter_name, token):
    subject = f'Invitation to join {company_name}'
    template = 'emails/company_invitation.html'
    
    context = {
        'company_name': company_name,
        'inviter_name': inviter_name,
        'invitation_link': f"{settings.FRONTEND_URL}/accept-invitation/{token}"
    }
    
    html_content = render_to_string(template, context)
    text_content = strip_tags(html_content)
    
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending invitation email: {str(e)}")
        return False 

def send_map_share_email(map_id, email, map_name, shared_by, user_type, token=None, invitation_url=None):
    """
    Send email notification for map sharing
    
    Args:
        email: Recipient email
        map_name: Name of the shared map
        shared_by: Name of user who shared the map
        user_type: Role assigned to user (EDITOR/CONTRIBUTOR/VIEWER)
        token: Optional invitation token for new users
        invitation_url: Complete invitation URL for new users
    """
    try:
        subject = f'Map Shared: {map_name}'
        template = 'emails/map_share.html'
        
        # Use the provided invitation_url if available, otherwise construct it from token
        if invitation_url:
            link = invitation_url
        elif token:
            link = f"{settings.FRONTEND_URL}/{map_id}/invite/{token}"
        else:
            link = None
        
        context = {
            'map_name': map_name,
            'shared_by': shared_by,
            'user_type': user_type,
            'invitation_link': link
        }
        
        html_content = render_to_string(template, context)
        text_content = strip_tags(html_content)
        
        from django.core.mail import get_connection
        connection = get_connection(
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            fail_silently=False,
        )
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            connection=connection
        )
        msg.attach_alternative(html_content, "text/html")
        
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending map share email: {str(e)}")
        return False 









# 