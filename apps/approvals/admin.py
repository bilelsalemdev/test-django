from django.contrib import admin

from .models import Approval


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'content_type', 'object_id', 'reviewed_by', 'created_at')
    list_filter = ('status', 'content_type')
    readonly_fields = ('content_type', 'object_id', 'created_at', 'updated_at')
