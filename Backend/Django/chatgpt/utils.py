from copy import deepcopy
import openai
from django.conf import settings
import logging

class ChatGPTApi:

    def __init__(self, model="gpt-4-1106-preview"):
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

    def format_prompt(self, requirements, content, wordlimits, language):
        """
        Combines different text inputs into a formatted prompt.
        Adds language-specific word limit requirements to the prompt.
        """
        # Append the language-specific word limit requirements
        if language == "chinese":
            formatted_requirements = f"{requirements} 请确保至少有{wordlimits}个字。"
        elif language == "english":
            formatted_requirements = f"{requirements} The word count must not exceed {wordlimits}."
        else:
            formatted_requirements = requirements  # Fallback if language is not specified
        # Combine the formatted requirements with the content
        return f"{formatted_requirements}\n\n{content}"

    def process_text_and_get_response(self, requirements, content, wordlimits, language, outlines):
        """Processes the given text and returns the GPT-3 response."""
        if outlines:
            outlines = self.format_outlines(outlines)
            formatted_prompt = f"{requirements}, 以下是我提供的材料\n\n{content}"
            return self.write_long_essay(formatted_prompt, wordlimits, outlines)
        else:
            formatted_prompt = self.format_prompt(requirements, content, wordlimits, language)
        return self.get_response_from_gpt(formatted_prompt)

    def write_long_essay(self, init_requirements, wordlimits, outlines):
        conversation_history = []
        response = ''
        result = ''
        for outline in outlines:
            prompt = deepcopy(init_requirements) + response
            prompt += f"请完成大纲{outline}，字数不少于{wordlimits}字"
            # Add your prompt to the conversation history
            user_message = {'role': 'user', 'content': prompt}
            conversation_history.append(user_message)

            # Make the API request
            model_response = self.get_response_from_gpt(prompt)

            # Extract the model's response and add it to the conversation history
            if model_response:
                conversation_history.append({'role': 'assistant', 'content': model_response})
                response += "已完成大纲{model_response}" + model_response
                result += model_response
        return result

    def format_outlines(self, outlines):
        return list(outlines.values())