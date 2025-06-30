from rest_framework import serializers
from .models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['owner', 'message_text', 'created_at']


class UserMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
