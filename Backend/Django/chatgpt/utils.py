import ast
import openai
from django.conf import settings
import logging

class ChatGPTApi:

    def __init__(self, model="gpt-3.5-turbo-0125"):
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

    def process_text_and_get_response(self, requirements, content, wordlimits, language):
        """Processes the given text and returns the GPT-3 response."""
        formatted_prompt = self.format_prompt(requirements, content, wordlimits, language)
        return self.get_response_from_gpt(formatted_prompt)

    def write_long_essay(self, requirements, content, wordlimits):
        prompt = f"请直接生成一个python列表，其中{requirements}的各个部分的内容和预计字数,背景资料{content},总字数{wordlimits}，每个列表元素都应该是一个字典，具有‘内容’和‘字数’两个键值对。请不要包含任何介绍或总结性的语句，我需要这个列表可以直接用于我的代码。"
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[{'role': 'system', 'content': prompt}],
        )
        result = response['choices'][-1]['message']['content']
        formated_list = self.extract_list(result)

        report = ""
        # Loop through each part and use OpenAI to generate content
        for part in formated_list:
            part_content = part['内容']  # This is the content for the API call
            word_count = part['字数']  # This guides the model's output length
            # Create a prompt that builds upon the accumulated report
            prompt = (
                f"请根据文章需求, 自身背景资料, 和已完成内容，直接继续撰写以下部分，无需任何额外的引言或结尾:"
                f"\n\n个人需求: \n{requirements}， \n\n文章背景资料: \n{content}, \n\n已完成内容：\n{report}\n\n"
                f"接下来部分：\n【标题】{part_content}\n【要求】直接撰写此部分，字数不能少于{word_count}字。请确保内容一定是中文"
            )

            # Call OpenAI API to generate the content
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{'role': 'system', 'content': prompt}],
            )

            # Append the generated content to the list
            result = response['choices'][-1]['message']['content'] if response else ""
            report += result
        return report

    def extract_list(self, result):
        start = result.find('[')
        end = result.rfind(']') + 1
        return ast.literal_eval(result[start:end])

    def format_outlines(self, outlines):
        return list(outlines.values())