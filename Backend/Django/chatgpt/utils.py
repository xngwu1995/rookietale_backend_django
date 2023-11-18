import openai
from django.conf import settings
import logging

class ChatGPTApi:

    def __init__(self, model="gpt-3.5-turbo-16k"):
        self.openai_api_key = settings.CHAT_GPT_API_KEY
        openai.api_key = self.openai_api_key
        self.model_name = model
        self.logger = logging.getLogger(__name__)

    def get_response_from_gpt(self, prompt):
        """Sends text to GPT-3 and retrieves the response."""
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{'role': 'system', 'content': prompt}],
            )
            return response['choices'][-1]['message']['content'] if response else None
        except Exception as e:
            self.logger.error(f"Error in get_response_from_gpt: {e}")
            return None

    def format_prompt(self, requirements, content):
        """Combines different text inputs into a formatted prompt."""
        return f"{requirements}\n\n{content}"

    def process_text_and_get_response(self, requirements, content):
        """Processes the given text and returns the GPT-3 response."""
        formatted_prompt = self.format_prompt(requirements, content)
        return self.get_response_from_gpt(formatted_prompt)
