import datetime
import finnhub
import numpy as np
from django.conf import settings
from yahoo_fin import stock_info as si
from chatgpt.utils import ChatGPTApi
from utils.strategy import Strategy


class StockSignal:
    def __init__(self):
        self.finnhub_client = finnhub.Client(api_key=settings.FINN_API_KEY)

    def apply_signal_val(self, df):
        # Apply multiple signal conditions and create signal columns using .loc for safe assignment
        df.loc[:, 'Signal_0'] = np.where(
            (df['SMA_7'] > df['SMA_25']) & (df['low'] > df['EMA_200']), 1,
            np.where((df['SMA_7'] < df['SMA_25']) & (df['high'] < df['EMA_200']), -1, 0)
        )

        df.loc[:, 'Signal_1'] = np.where(
            (df['adjclose'] < df['BBL_30_2.0']) & (df['rsi'] < 20), 1,
            np.where((df['adjclose'] > df['BBU_30_2.0']) & (df['rsi'] > 80), -1, 0)
        )

        df.loc[:, 'Signal_2'] = np.where(
            (df['MACDs_12_26_9'] > 0) & (df['low'] > df['EMA_200']), 1,
            np.where((df['MACDs_12_26_9'] < 0) & (df['high'] < df['EMA_200']), -1, 0)
        )

        df.loc[:, 'Signal_3'] = np.where(
            (df['Supertrend_12_3'] & df['Supertrend_11_2'] & df['Supertrend_10_1']) & (df['low'] > df['EMA_200']), 1,
            np.where((~df['Supertrend_12_3'] | ~df['Supertrend_11_2'] | ~df['Supertrend_10_1']) & (df['high'] < df['EMA_200']), -1, 0)
        )

        return df



    def get_all_historical_data(self, start_date, end_date, stock_symbols):
        data = dict()
        start = datetime.datetime(*map(int, start_date.split('-')))
        end = datetime.datetime(*map(int, end_date.split('-')))
        for stock_symbol in stock_symbols:
            data[stock_symbol] = si.get_data(stock_symbol, start_date=start, end_date=end)['close']
        return data

    def update_df_by_strategy(self, stock_symbol):
        end_date = datetime.datetime.now() + datetime.timedelta(days=1)
        start_date = datetime.datetime.now() - datetime.timedelta(days=300)
        df = si.get_data(stock_symbol, start_date=start_date, end_date=end_date)
        
        # Applying various strategies
        Strategy.macd(df)
        Strategy.rsi(df)
        Strategy.ema(df, periods=200)
        Strategy.ema(df, periods=20)
        Strategy.ema(df, periods=50)
        Strategy.ema(df, periods=100)
        Strategy.sma(df, periods=7)
        Strategy.sma(df, periods=25)
        Strategy.supertrend(df)
        Strategy.supertrend(df, periods=11, multiplier=2)
        Strategy.supertrend(df, periods=10, multiplier=1)
        Strategy.bollinger_bands(df)
        
        # Making a copy and applying signal values
        df1 = df[202:].copy()  # Make a copy here
        df = self.apply_signal_val(df1)
        df = df.drop(['ticker'], axis=1)
        
        # Calculating the signal value
        val = df.iloc[-1].Signal_0 + df.iloc[-1].Signal_1 + df.iloc[-1].Signal_2 + df.iloc[-1].Signal_3
        result = ''
        if val >= 2:
            result = 'Buy'
        elif val <= 0:
            result = 'Sell'
        else:
            result = 'Hold'
        
        # Formatting the DataFrame
        df.index.name = 'date'
        df_json = df.reset_index()
        df_json['date'] = df_json['date'].dt.strftime('%Y-%m-%d')
        json_str = df_json.to_json(orient='records')
        
        return json_str, result

    async def async_get_gpt_stocks_analysis(self, stock_symbol):
        chatgpt_api = ChatGPTApi()
        return await chatgpt_api.async_stocks_analysis(stock_symbol)

    def get_price(self, stock_symbol):
        df_val, rank = self.update_df_by_strategy(stock_symbol)
        # latest_price = si.get_live_price(stock_symbol)
        latest_price = 100
        return df_val, rank, latest_price

    async def get_signal(self, stock_symbol):
        gpt_result = await self.async_get_gpt_stocks_analysis(stock_symbol)
        return gpt_result

    def format_news(self, news_list):
        formated_news = []
        for news in news_list:
            headline = news['headline']
            summary = news['summary']
            if len(summary) < 10:
                continue
            formated_news.append("Headline:" + headline + "\n" + "Summary:" + summary)
        return formated_news

    def get_stock_news(self, stock_symbol):
        categories = ['general', 'forex', 'crypto', 'merger']
        from_date = datetime.datetime.now() - datetime.timedelta(days=5)
        to_date = datetime.datetime.now()
        stock_news = self.finnhub_client.company_news(stock_symbol, _from=from_date.strftime("%Y-%m-%d"), to=to_date.strftime("%Y-%m-%d"))
        formated_world_news = []
        for category in categories:
            category_news = self.finnhub_client.general_news(category, min_id=0)
            formated_world_news.extend(self.format_news(category_news))
        formated_stock_news = self.format_news(stock_news)

        return {'stock_news': formated_stock_news, 'world_news': formated_world_news}
        