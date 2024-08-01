import ast
import asyncio
import aiohttp
import openai
import certifi
import time
import ssl
from django.conf import settings
import logging

class ChatGPTApi:

    def __init__(self, model="gpt-4o"):
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

    def stock_analysis(self, data, stock_symbol, news):
        stock_news = news.get('stock_news')
        world_news = news.get('world_news')
        stock_news = "下一条新闻".join(stock_news)
        world_news = "下一条新闻".join(world_news)
        prompt = (
            f"以下是{stock_symbol}公司的相关信息"
            f"以下是最近几天的数据：{data}。"
            f"数据中四种信号的说明如下："
            f"Signal_0：根据SMA_7与SMA_25相对位置及价格相对于EMA_200的关系，生成看涨或看跌信号。"
            f"Signal_1：根据调整后的收盘价与布林带的关系及RSI值，识别极端的超买或超卖条件。"
            f"Signal_2：基于MACD信号线与价格相对于EMA_200的位置，判断市场动能的强弱。"
            f"Signal_3：综合三种Supertrend指标与价格相对于EMA_200的位置，判断市场趋势的强度。"
            f"以下是最近五天的几条和{stock_symbol}相关的新闻:{news}"
            f"以下是最近全国性的新闻消息{world_news}"
            f"基于以上信息，请您作为一位顶尖的股票交易员，结合全球大事，考虑美联储的计划，提供详细的股票分析报告，确保用户可以根据这份报告能做出正确的投资行为, 并且这份报告需要让读者知道止损区间，止损的百分比，获利止盈区间，获利止盈的百分比！"
        )
        return self.get_response_from_gpt(prompt)

    async def get_gpt_result(self, stock_symbol, session):
        prompt = f'''
        Stock Analysis Request: {stock_symbol}
        Objective:
        Provide a detailed analysis of {stock_symbol} stock to assess its investment potential.
        
        Financial Performance Analysis:

        Earnings Per Share (EPS):
        Current EPS (TTM)
        EPS growth rate for the last 3 years (CAGR)
        EPS estimates for the next two fiscal years
        Price-to-Earnings Ratio (P/E Ratio):
        Current P/E ratio
        Average P/E ratio for the semiconductor industry
        {stock_symbol}'s 5-year average P/E ratio
        Based on these values, is {stock_symbol} currently overvalued, undervalued, or fairly valued?
        Price/Earnings-to-Growth Ratio (PEG Ratio):
        Calculate PEG ratio using current P/E and estimated EPS growth rate.
        Interpret the PEG ratio: Is the stock's growth outlook justified by its current valuation?
        Dividend Yield:
        Current dividend yield
        Dividend payout ratio
        Average dividend yield for the semiconductor industry
        Assessment of dividend sustainability (consider company's free cash flow and earnings growth)
        
        Growth and Profitability Analysis:

        Revenue Growth:
        Quarterly and annual revenue growth rates for the last 2 years
        Key factors driving revenue growth (e.g., product segments, market trends)
        Future revenue growth projections (if available)
        Profit Margins:
        Gross profit margin, operating profit margin, and net profit margin for the last 3 years
        Compare {stock_symbol}'s margins to industry averages
        Analyze trends in profit margins (are they expanding or contracting?)
        Return on Equity (ROE):
        Calculate ROE for the last 3 years
        Compare {stock_symbol}'s ROE to industry averages
        Assess how effectively {stock_symbol} generates profit from shareholders' equity
        
        Financial Health and Risk Analysis:

        Market Capitalization:
        Current market capitalization
        Classification (large-cap, mega-cap, etc.)
        How does {stock_symbol}'s size affect its risk and growth potential?
        Debt-to-Equity Ratio:
        Current debt-to-equity ratio
        Compare to industry averages
        Evaluate {stock_symbol}'s financial leverage and debt burden
        Free Cash Flow (FCF):
        Free cash flow for the last 3 years
        FCF trends over time
        Potential uses of FCF (e.g., share buybacks, dividends, R&D)
        
        Qualitative Analysis:

        Competitive Advantage:
        Identify {stock_symbol}'s key competitive advantages (technology leadership, strong brand, etc.)
        Assess the durability of these advantages (are they likely to persist?)
        Management Quality:
        Evaluate the experience and track record of the leadership team
        Consider the effectiveness of their strategic decisions
        Industry Analysis:
        Provide an overview of the semiconductor industry
        Discuss major trends and risks (e.g., supply chain disruptions, technological shifts)
        Analyze {stock_symbol}'s competitive position within the industry
        
        Investment Recommendation:
        Based on the above analysis, provide a clear recommendation:

        Buy: If you believe {stock_symbol} is a strong investment, explain why, highlighting the key factors supporting your decision.
        Hold: If you believe the stock is fairly valued or has balanced risks and rewards, justify your neutral stance.
        Sell: If you believe the stock is overvalued or faces significant headwinds, present the reasons for selling.
        
        Additional Considerations:

        Risk Profile: Assess the overall risk level of investing in {stock_symbol}.
        Investment Horizon: Consider whether {stock_symbol} is more suitable for short-term, medium-term, or long-term investors.
        Alternative Investments: Briefly discuss other semiconductor stocks or relevant investment opportunities.
        
        Data Sources:

        Use reputable and current financial data sources (e.g., SEC filings, Yahoo Finance, financial news outlets). Ensure data is as of today's date.
        Cite your sources for transparency and credibility.
        '''
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}",
        }
        payload = {
            "model": self.model_name,
            "messages": [{'role': 'system', 'content': prompt}]
        }
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        try:
            async with session.post(url, headers=headers, json=payload, ssl=ssl_context) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][-1]['message']['content'] if result else None
                else:
                    self.logger.error(f"Error in get_response_from_gpt: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"Error in get_response_from_gpt: {e}")
            return None
    async def async_stocks_analysis(self, stock_symbols):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for stock_symbol in stock_symbols:
                tasks.append(asyncio.ensure_future(self.get_gpt_result(stock_symbol, session)))
            results = await asyncio.gather(*tasks)
        return results
