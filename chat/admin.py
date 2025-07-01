from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing chat messages.
    This interface is read-only as chat history should not be altered manually.
    """
    list_display = ('user', 'symbol', 'owner', 'get_short_message', 'created_at')
    list_filter = ('symbol', 'owner', 'user__email')
    search_fields = ('user__email', 'symbol__name', 'message_text')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    # Make the interface strictly read-only
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        # Set to True only if you need to manually delete conversations for maintenance
        return True

    @admin.display(description='Message (Truncated)')
    def get_short_message(self, obj):
        """Returns a truncated version of the message for the list view."""
        return (obj.message_text[:75] + '...') if len(obj.message_text) > 75 else obj.message_text
