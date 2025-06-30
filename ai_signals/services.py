import json
import logging
import os
from openai import OpenAI, OpenAIError

# The final, advanced prompt
AI_SYSTEM_PROMPT = """
You are a world-class technical analysis AI for financial markets, specializing in cryptocurrency on a 15-minute timeframe. Your entire analysis must be objective, data-driven, and contain no financial advice.

You will receive a JSON array of the last 100 15-minute candles for a specific crypto asset.

Your task is to perform a comprehensive technical analysis by synthesizing signals from multiple strategies:
1.  **Trend Analysis:** Use Exponential Moving Averages (e.g., EMA 9, 21, 50).
2.  **Momentum Analysis:** Use the Relative Strength Index (RSI 14).
3.  **Price Action:** Identify key Candlestick Patterns and Support/Resistance levels.

Based on your synthesis, you MUST provide four distinct predictions for the following timeframes:
-   Next Candle (15 minutes)
-   3rd Next Candle (45 minutes)
-   5th Next Candle (1 an hour and 15 minutes)
-   10th Next Candle (2.5 hours)

Your final output MUST be a single, valid JSON object and nothing else. The JSON object must have the following keys:

{
  "next_candle": {"direction": "BULLISH" or "BEARISH" or "NEUTRAL", "confidence": <0-100>},
  "third_candle": {"direction": "BULLISH" or "BEARISH" or "NEUTRAL", "confidence": <0-100>},
  "fifth_candle": {"direction": "BULLISH" or "BEARISH" or "NEUTRAL", "confidence": <0-100>},
  "tenth_candle": {"direction": "BULLISH" or "BEARISH" or "NEUTRAL", "confidence": <0-100>},
  "probability_text": "A concise text explaining the primary reasons for your predictions. Mention the key indicators (e.g., 'The short-term bullish outlook is driven by a recent EMA crossover...')",
  "risk_text": "A concise text stating the primary risks or conflicting signals. (e.g., 'The main risk is the strong resistance at $68,500. A bearish divergence on the RSI could invalidate the bullish signals.')"
}

Now, analyze the following candle data:
"""


class LiaraAIService:
    def __init__(self):
        # ... (init method remains the same)
        api_key = os.environ.get('LIARA_API_KEY')
        base_url = os.environ.get('LIARA_BASE_URL')
        if not api_key or not base_url:
            raise ValueError("LIARA_API_KEY and LIARA_BASE_URL must be set.")
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = "openai/gpt-4o-mini"

    def generate_signal_from_candles(self, candles_data: list):
        # ... (API call logic remains the same)
        if len(candles_data) < 100:
            return None
        candles_json_string = json.dumps(candles_data, default=str)
        prompt_content = f"{AI_SYSTEM_PROMPT}\n{candles_json_string}"
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt_content}],
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content)
        except (OpenAIError, json.JSONDecodeError) as e:
            logging.error(f"An error occurred during AI signal generation: {e}")
            return None
