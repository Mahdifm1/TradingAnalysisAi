from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatMessage, Symbol
from .serializers import ChatMessageSerializer, UserMessageSerializer
from .services import ChatAIService
from accounts.permissions import IsUserVerified


class ChatConversationView(APIView):
    """
    Handles the entire chat conversation for a specific symbol.
    GET: Retrieves the chat history.
    POST: Submits a new message and gets an AI response.
    """
    permission_classes = [IsUserVerified]

    def get(self, request, symbol_name, format=None):
        """Returns the last 20 messages for the user and symbol."""
        try:
            symbol = Symbol.objects.get(name__iexact=symbol_name)
            messages = ChatMessage.objects.filter(
                user=request.user,
                symbol=symbol
            ).order_by('-created_at')[:20]  # Get the last 20 messages

            serializer = ChatMessageSerializer(reversed(messages), many=True)
            return Response(serializer.data)
        except Symbol.DoesNotExist:
            return Response({"error": "Symbol not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, symbol_name, format=None):
        """Receives a user message, gets an AI response, and saves both."""
        serializer = UserMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_message_text = serializer.validated_data.get('message')

        try:
            symbol = Symbol.objects.get(name__iexact=symbol_name)
        except Symbol.DoesNotExist:
            return Response({"error": "Symbol not found."}, status=status.HTTP_404_NOT_FOUND)

        # 1. Save the user's message
        ChatMessage.objects.create(
            user=request.user,
            symbol=symbol,
            message_text=user_message_text,
            owner=ChatMessage.MessageOwner.USER
        )

        # 2. Get history to provide context to the AI
        history = ChatMessage.objects.filter(
            user=request.user,
            symbol=symbol
        ).order_by('created_at')

        # 3. Get AI response
        service = ChatAIService(symbol_name=symbol.name, history=list(history))
        ai_response_text = service.get_ai_response(user_message_text)

        # 4. Save the AI's response
        ai_message = ChatMessage.objects.create(
            user=request.user,
            symbol=symbol,
            message_text=ai_response_text,
            owner=ChatMessage.MessageOwner.AI
        )

        # 5. Return the AI's response to the client
        response_serializer = ChatMessageSerializer(ai_message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
