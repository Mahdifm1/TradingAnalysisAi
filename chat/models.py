from django.db import models
from django.conf import settings
from market_data.models import Symbol


class ChatMessage(models.Model):
    """
    Represents a single message in a chat conversation between a user
    and the AI about a specific trading symbol.
    """

    class MessageOwner(models.TextChoices):
        USER = 'USER', 'User'
        AI = 'AI', 'AI'

    # The user who sent or received the message
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    # The symbol the conversation is about
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name='chat_messages')

    # Message details
    message_text = models.TextField()
    owner = models.CharField(max_length=10, choices=MessageOwner.choices)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner} message from {self.user.email} on {self.symbol.name}"

    class Meta:
        ordering = ['created_at']
