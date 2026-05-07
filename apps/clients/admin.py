from django.contrib import admin

from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'company', 'created_at')
    list_filter = ('company',)
    search_fields = ('first_name', 'last_name', 'email')
