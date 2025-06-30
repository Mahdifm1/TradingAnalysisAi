import json
import os
from openai import OpenAI, OpenAIError
import logging


class ChatAIService:
    """
    Handles conversations with the AI about a specific symbol,
    using the existing chat history as context.
    """

    def __init__(self, symbol_name: str, history: list):
        api_key = os.environ.get('LIARA_API_KEY')
        base_url = os.environ.get('LIARA_BASE_URL')

        if not api_key or not base_url:
            raise ValueError("LIARA_API_KEY and LIARA_BASE_URL must be set.")

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = "openai/gpt-4o-mini"
        self.symbol_name = symbol_name
        self.history = history

    def get_ai_response(self, user_message: str):
        """
        Gets a response from the AI based on the user's message and chat history.
        """
        system_prompt = self._build_system_prompt()
        messages = self._build_message_history(system_prompt, user_message)

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return completion.choices[0].message.content
        except OpenAIError as e:
            logging.error(f"An error occurred with the Chat AI API: {e}")
            return "Sorry, I'm having trouble connecting to my brain right now. Please try again later."

    def _build_system_prompt(self):
        return (
            f"You are a helpful and expert trading assistant AI. "
            f"The user is currently viewing the chart for the symbol '{self.symbol_name}'. "
            f"Your knowledge is up to date. Answer the user's questions concisely and directly "
            f"based on general market knowledge, technical analysis principles, and the context of the conversation. "
            f"Do not provide financial advice. Be friendly and professional."
        )

    def _build_message_history(self, system_prompt: str, user_message: str):
        messages = [{"role": "system", "content": system_prompt}]

        # Add past messages to the history
        for message in self.history:
            role = 'user' if message.owner == 'USER' else 'assistant'
            messages.append({"role": role, "content": message.message_text})

        # Add the new user message
        messages.append({"role": "user", "content": user_message})

        return messages
