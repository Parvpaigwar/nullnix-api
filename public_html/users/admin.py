from django.contrib import admin
from .models import users

# Register your models here.

@admin.register(users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'is_verified', 'login_methode', 'created_on')
    list_filter = ('is_verified', 'login_methode', 'country', 'created_on')
    search_fields = ('name', 'email', 'contact_no')
    readonly_fields = ('created_on', 'modified_on', 'user_schema')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'contact_no', 'country')
        }),
        ('Authentication', {
            'fields': ('password', 'is_verified', 'login_methode')
        }),
        ('System Fields', {
            'fields': ('user_schema', 'created_on', 'modified_on'),
            'classes': ('collapse',)
        }),
    )
