from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from market_data.models import Symbol
from .models import ChatMessage

User = get_user_model()


class ComprehensiveChatTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='chatuser@example.com', password='pw')
        self.symbol = Symbol.objects.create(name='CHAT-COIN', is_active=True)
        # Authenticate the client for all tests in this class
        self.client.force_authenticate(user=self.user)

    def test_get_empty_chat_history(self):
        """Test retrieving a chat history when no messages exist."""
        url = f'/api/chat/conversation/{self.symbol.name}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    @patch('chat.services.ChatAIService.get_ai_response')
    def test_post_message_and_get_history(self, mock_get_ai_response):
        """Test the full conversation flow: POSTing a message and then GETting the history."""
        # --- Step 1: POST a new message ---
        mock_get_ai_response.return_value = "This is the AI's answer."
        url = f'/api/chat/conversation/{self.symbol.name}/'
        data = {'message': 'What is the trend for this symbol?'}

        response_post = self.client.post(url, data, format='json')

        # Assert the AI's response is returned correctly
        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_post.data['owner'], 'AI')
        self.assertEqual(response_post.data['message_text'], "This is the AI's answer.")

        # Assert that both user and AI messages are saved in the database
        self.assertEqual(ChatMessage.objects.count(), 2)
        user_msg = ChatMessage.objects.get(owner='USER')
        ai_msg = ChatMessage.objects.get(owner='AI')
        self.assertEqual(user_msg.message_text, data['message'])
        self.assertEqual(ai_msg.message_text, "This is the AI's answer.")

        # --- Step 2: GET the conversation history ---
        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_get.data), 2)
        # Check if the order is correct (user message first, then AI)
        self.assertEqual(response_get.data[0]['owner'], 'USER')
        self.assertEqual(response_get.data[1]['owner'], 'AI')

    def test_chat_unauthenticated(self):
        """Ensure unauthenticated users cannot access the chat API."""
        # Create a new client that is not authenticated
        unauthenticated_client = APIClient()
        url = f'/api/chat/conversation/{self.symbol.name}/'

        get_response = unauthenticated_client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_401_UNAUTHORIZED)

        post_response = unauthenticated_client.post(url, {'message': 'test'}, format='json')
        self.assertEqual(post_response.status_code, status.HTTP_401_UNAUTHORIZED)
