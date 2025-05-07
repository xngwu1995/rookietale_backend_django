import pandas as pd
import numpy as np
import datetime
import yfinance as yf
from yahoo_fin import stock_info as si
from pandas import DataFrame, Series
from numpy import ndarray
from stocks.api.serializers import StrategyStockSerializer
from utils.finviz.screener import Screener # type: ignore
from scipy.signal import argrelextrema # type: ignore
from typing import List, Tuple, Dict, Optional
from stocks.models import Stock, StrategyData
from django.core.cache import cache

from utils.utils import today_date


class Strategy:
    def macd(df):
        '''
        Added mcad, mcad_h, mcad_s into the df
        '''
        # # Calculate MACD values using the pandas_ta library
        df.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)
        return df
    
    def rsi(df: pd.DataFrame, window_length: int = 14, price: str = 'close'):
        """
        An optimized implementation of the Relative Strength Index (RSI) calculation.
        This version uses vectorized operations for faster computation.

        Args:
            df: pandas.DataFrame - a Pandas DataFrame object.
            window_length: int - the period over which the RSI is calculated. Default is 14.
            price: str - the column name from which the RSI values are calculated. Default is 'close'.

        Returns:
            DataFrame object with an additional 'rsi' column.
        """
        # Calculate price differences
        delta = df[price].diff()

        # Make the gains (positive gains) and losses (negative gains) Series
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)

        # Calculate the EWMA (Exponential Weighted Moving Average) of gains and losses
        avg_gain = gain.ewm(alpha=1/window_length, min_periods=window_length).mean()
        avg_loss = loss.ewm(alpha=1/window_length, min_periods=window_length).mean()

        # Calculate the RSI based on EWMA
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # Append the RSI to the DataFrame
        df['rsi'] = rsi

        return df

    
    def ema(df, periods=10):
        df.ta.ema(close='close', length=periods, append=True)
        return df

    def sma(df, periods=10):
        # column_name = 'SMA_' + str(periods)
        # df[column_name] = df['close'].rolling(window=periods).mean()
        df.ta.sma(close='close', length=periods, append=True)
        return df

    def wma(df):
        pass

    def supertrend(df, periods=12, multiplier=3):
        
        high = df['high']
        low = df['low']
        close = df['close']
        
        # calculate ATR
        price_diffs = [high - low, 
                    high - close.shift(), 
                    close.shift() - low]
        true_range = pd.concat(price_diffs, axis=1)
        true_range = true_range.abs().max(axis=1)
        # default ATR calculation in supertrend indicator
        atr = true_range.ewm(alpha=1/periods,min_periods=periods).mean() 
        # df['atr'] = df['tr'].rolling(atr_period).mean()
        
        # HL2 is simply the average of high and low prices
        hl2 = (high + low) / 2
        # upperband and lowerband calculation
        # notice that final bands are set to be equal to the respective bands
        final_upperband = upperband = hl2 + (multiplier * atr)
        final_lowerband = lowerband = hl2 - (multiplier * atr)
        
        # initialize Supertrend column to True
        supertrend = [True] * len(df)
        
        for i in range(1, len(df.index)):
            curr, prev = i, i-1
            
            # if current close price crosses above upperband
            if close[curr] > final_upperband[prev]:
                supertrend[curr] = True
            # if current close price crosses below lowerband
            elif close[curr] < final_lowerband[prev]:
                supertrend[curr] = False
            # else, the trend continues
            else:
                supertrend[curr] = supertrend[prev]
                
                # adjustment to the final bands
                if supertrend[curr] == True and final_lowerband[curr] < final_lowerband[prev]:
                    final_lowerband[curr] = final_lowerband[prev]
                if supertrend[curr] == False and final_upperband[curr] > final_upperband[prev]:
                    final_upperband[curr] = final_upperband[prev]

            # to remove bands according to the trend direction
            if supertrend[curr] == True:
                final_upperband[curr] = np.nan
            else:
                final_lowerband[curr] = np.nan
        name = 'Supertrend_' + str(periods) + '_' + str(multiplier)
        df[name] = supertrend
        # df['Final Lowerband'] = final_lowerband
        # df['Final Upperband'] = final_upperband
        return df
    
    def bollinger_bands(df, periods=30, std=2):
        df.ta.bbands(close='close', length=periods, std=std, append=True)
        return df


class Analysis:
    def supervanous():
        stocks = si.get_day_gainers(datetime.datetime.now())
        return list(stocks[stocks['Volume']>2000000]['Symbol'])

    def superlosses():
        stocks = si.get_day_losers('2022-12-30')
        print(stocks)
        return list(stocks[stocks['Volume']>2000000]['Symbol'])

    def superactivate():
        stocks = si.get_day_most_active()
        print(stocks)


# Define the VCP (Volatility Contraction Pattern) Strategy class
class VCP_Strategy:
    # Constructor to initialize the object
    def __init__(self) -> None:
        # Define attributes to store stock data and today's date
        self.ticker_list: List[str]
        self.rs_dict: Dict[str, int]
        self.df_spx: Dict[str, float]
        self.today = today_date()
        
        # Define cache key for VCP data to avoid recalculating if already stored
        vcp_cache_key = f"vcp_{self.today}"
        self.ticker_list, self.rs_dict, self.df_spx = cache.get(vcp_cache_key, (None, None, None))
        
        # If data is not available in cache, fetch initial data and store it in cache
        if self.ticker_list is None:
            self.ticker_list, self.rs_dict, self.df_spx = self.get_init_data()
            cache.set(vcp_cache_key, (self.ticker_list, self.rs_dict, self.df_spx))

        # Initialize a DataFrame to store VCP screening results
        self.radar: DataFrame = DataFrame({
            'Ticker': [],
            'Num_of_contraction': [],
            'Max_contraction': [],
            'Min_contraction': [],
            'Weeks_of_contraction': [],
            'RS_rating': []
        })

    # Method to get initial stock data for screening
    def get_init_data(self):
        # Filters to fetch stocks that meet basic volume and price criteria
        filters = ['cap_smallover','sh_avgvol_o100','sh_price_o2','ta_sma200_sb50','ta_sma50_pa']

        # Fetch and save ticker data based on filters (using FinViz screener)
        stock_list = Screener(filters=filters, table='Performance', order='asc', rows=960)
        ticker_table = pd.DataFrame(stock_list.data)
        ticker_list = ticker_table['Ticker'].to_list()

        # Fetch RS (Relative Strength) data and create a dictionary for ranking stocks
        performance_table = Screener(table='Performance', order='-perf52w', rows=3000)
        rs_table = pd.DataFrame(performance_table.data)
        rs_list = rs_table['Ticker'].to_list()
        rs_dict = {value: index for index, value in enumerate(rs_list)}

        # Fetch S&P 500 data for comparing relative strength
        end_date = pd.to_datetime('today')
        start_date = end_date - pd.DateOffset(years=2)
        df_spx = si.get_data(ticker='^GSPC', start_date=start_date, end_date=end_date)

        return ticker_list, rs_dict, df_spx

    # Method to calculate the trend value of moving averages (MA200)
    def trend_value(self, nums: List[float]) -> float:
        # Calculate slope of the given data (used to determine trend direction)
        summed_nums: float = sum(nums)
        multiplied_data: float = 0
        summed_index: float = 0
        squared_index: float = 0

        for index, num in enumerate(nums):
            index += 1
            multiplied_data += index * num
            summed_index += index
            squared_index += index**2

        # Calculate the slope of the trend line using least squares method
        numerator: float = (len(nums) * multiplied_data) - (summed_nums * summed_index)
        denominator: float = (len(nums) * squared_index) - summed_index**2
        if denominator != 0:
            return numerator / denominator
        else:
            return 0

    # Method to apply the trend template and check if stock meets criteria for Stage 2
    def trend_template(self, df: DataFrame) -> DataFrame:
        # Calculate moving averages: MA_50, MA_150, MA_200
        df['MA_50'] = round(df['Close'].rolling(window=50).mean(), 2)
        df['MA_150'] = round(df['Close'].rolling(window=150).mean(), 2)
        df['MA_200'] = round(df['Close'].rolling(window=200).mean(), 2)
        
        # Calculate 52-week high and low
        if len(df.index) > 5 * 52:
            df['52_week_low'] = df['Low'].rolling(window = 5*52).min()
            df['52_week_high'] = df['High'].rolling(window = 5*52).max()
        else:
            df['52_week_low'] = df['Low'].rolling(window = len(df.index)).min()
            df['52_week_high'] = df['High'].rolling(window = len(df.index)).max()
        
        # Define multiple conditions that need to be met for Stage 2 (Uptrend)
        df['condition_1'] = (df['Close'] > df['MA_150']) & (df['Close'] > df['MA_200']) & (df['Close'] > df['MA_50'])
        df['condition_2'] = (df['MA_150'] > df['MA_200']) & (df['MA_50'] > df['MA_150'])
        slope: Series = df['MA_200'].rolling(window = 20).apply(self.trend_value, raw=True)
        df['condition_3'] = slope > 0.0
        df['condition_6'] = df['Low'] > (df['52_week_low'] * 1.3)
        df['condition_7'] = df['High'] > (df['52_week_high'] * 0.75)
        df['RS'] = df['Close'] / self.df_spx['close']
        slope_rs: Series = df['RS'].rolling(window = 20).apply(self.trend_value, raw=True)
        df['condition_8'] = slope > 0.0
        df['condition_9'] = slope_rs > 0.0
        
        # If all conditions are met, mark as 'Pass'
        df['Pass'] = df[
            ['condition_1','condition_2','condition_3','condition_6','condition_7','condition_8', 'condition_9']
        ].all(axis='columns')
        
        return df

    # Find local maxima and minima in price data to identify potential contraction points
    def local_high_low(self, df: DataFrame) -> Tuple[List[int], List[int]]:
        # Identify local highs and lows (turning points)
        local_high: ndarray = argrelextrema(df['High'].to_numpy(),np.greater,order=10)[0]
        local_low: ndarray = argrelextrema(df['Low'].to_numpy(),np.less,order=10)[0]
        
        # Eliminate consecutive highs or lows by selecting significant points
        i: int = 0
        j: int = 0
        adjusted_local_high: List[int] = []
        adjusted_local_low: List[int] = []
        
        while i < len(local_high) and j < len(local_low):
            if local_high[i] < local_low[j]:
                while i < len(local_high):
                    if local_high[i] < local_low[j]:
                        i += 1
                    else:
                        adjusted_local_high.append(local_high[i - 1])
                        break
            elif local_high[i] > local_low[j]:
                while j < len(local_low):
                    if local_high[i] > local_low[j]:
                        j += 1
                    else:
                        adjusted_local_low.append(local_low[j - 1])
                        break
            else:
                i += 1
                j += 1
        
        # Add remaining elements from local_high or local_low
        if i < len(local_high):
            adjusted_local_high.pop(-1)
            while i < len(local_high):
                if local_high[i] > local_low[j-1]:
                    i += 1
                else:
                    adjusted_local_high.append(local_high[i-1])
                    break
            adjusted_local_high.append(local_high[-1])
            adjusted_local_low.append(local_low[j-1])
        
        if j < len(local_low):
            adjusted_local_low.pop(-1)
            while j < len(local_low):
                if local_high[i-1] > local_low[j]:
                    j += 1
                else:
                    adjusted_local_low.append(local_low[j-1])
                    break
            adjusted_local_low.append(local_low[-1])
            adjusted_local_high.append(local_high[i-1])
        return adjusted_local_high, adjusted_local_low

    # Calculate the depth of contractions between local highs and lows
    def contractions(self, df: DataFrame, local_high: List[int], local_low: List[int]) -> List[float]:
        local_high = local_high[::-1]
        local_low = local_low[::-1]
        
        i: int = 0
        j: int = 0
        contraction: List[float] = []
        
        while i < len(local_low) and j < len(local_high):
            if local_low[i] > local_high[j]:
                high_value = df['High'].iloc[local_high[j]]
                low_value = df['Low'].iloc[local_low[i]]
                contraction_value = round((high_value - low_value) / high_value * 100, 2)
                contraction.append(contraction_value)
                i += 1
                j += 1
            else:
                j += 1
        return contraction

    # Method to count the number of contractions
    def num_of_contractions(self, contraction: List[float]) -> int:
        new_c: float = 0.0
        num_of_contraction: int = 0
        for c in contraction:
            if c > new_c:
                num_of_contraction += 1
                new_c = c
            else:
                break
        return num_of_contraction

    # Method to calculate the depth of maximum and minimum contractions
    def max_min_contraction(self, contraction: List[float], num_of_contractions: int) -> Tuple[float, float]:
        max_contraction = contraction[num_of_contractions - 1]
        min_contraction = contraction[0]
        return max_contraction, min_contraction

    # Calculate the weeks of contraction based on price action
    def weeks_of_contraction(self, df: DataFrame, local_high: List[int], num_of_contractions: int) -> float:
        week_of_contraction: float = (len(df.index) - local_high[::-1][num_of_contractions - 1]) / 5
        return week_of_contraction

    # Main VCP method to determine if a stock follows the VCP pattern
    def vcp(self, df: DataFrame) -> Tuple[int, float, float, float, int]:
        # Identify local highs and lows
        local_high: List[int]
        local_low: List[int]
        local_high, local_low = self.local_high_low(df)

        # Calculate the contraction values
        contraction: List[float] = self.contractions(df, local_high, local_low)
        
        # Calculate number of contractions and determine if they meet criteria
        num_of_contraction: int = self.num_of_contractions(contraction)
        if 2 <= num_of_contraction <= 4:
            flag_num = 1
        else:
            flag_num = 0
        
        # Calculate depth of contractions
        max_c: float = 0.0
        min_c: float = 0.0
        flag_max: int = 1
        flag_min: int = 0

        max_c, min_c = self.max_min_contraction(contraction, num_of_contraction)
        if max_c > 50:
            flag_max = 0

        if min_c <= 15:
            flag_min = 1

        # Calculate weeks of contractions and determine if they meet criteria
        week_of_contraction: float = self.weeks_of_contraction(df, local_high, num_of_contraction)
        flag_week: int = 0
        if week_of_contraction >= 2:
            flag_week = 1
        
        # Determine volume contraction
        df['30_day_avg_volume'] = round(df['Volume'].rolling(window = 30).mean(),2)
        df['5_day_avg_volume'] = round(df['Volume'].rolling(window = 5).mean(),2)
        flag_vol: int = 0
        df['vol_contraction'] = df['5_day_avg_volume'] < df['30_day_avg_volume']
        if df['vol_contraction'][-1] == 1:
            flag_vol = 1
            
        # Ensure the stock is still consolidating (hasn't broken out yet)
        flag_consolidation: int = 0
        if df['High'].iloc[-1] < df['High'].iloc[local_high[-1]]:
            flag_consolidation = 1
        
        # Final check: Ensure all criteria are met for VCP
        flag_final: int = 0
        if flag_num == 1 & flag_max == 1 & flag_min == 1 & flag_week == 1 & flag_vol == 1 & flag_consolidation == 1:
            flag_final = 1
        
        return num_of_contraction, max_c, min_c, week_of_contraction, flag_final

    # Method to calculate the RS (Relative Strength) rating of a stock
    def rs_rating(self, ticker: str) -> int:
        total_stocks: int = 478 * 20
        ticker_index: Optional[int] = self.rs_dict.get(ticker)
        rs: int = 0
        if ticker_index:
            rs = int(round((total_stocks - ticker_index) / total_stocks * 100, 0))
        return rs

    # Method to get historical data for a given stock ticker
    def get_ticker_history(self, stock_ticker: str, period: int = 2) -> pd.DataFrame:
        end_date = pd.to_datetime('today')
        start_date = end_date - pd.DateOffset(years=period)

        # Cache the data for faster access
        cache_key = f"{stock_ticker}_{self.today}"
        data = cache.get(cache_key, None)
        if not isinstance(data, pd.DataFrame):
            try:
                data = si.get_data(stock_ticker, start_date=start_date, end_date=end_date)
                if data is None or data.empty:
                    print(f"Failed to get data for {stock_ticker}.")
                    return pd.DataFrame()
                cache.set(f"{cache_key}", data)
            except Exception as e:
                print(f"Error occurred while fetching data for {stock_ticker}: {e}")
                return pd.DataFrame()

        history_data = data.dropna()
        if history_data.empty:
            return pd.DataFrame()

        # Rename columns to match desired format
        history_data.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'adjclose': 'Adj Close',
            'volume': 'Volume'
        }, inplace=True)
        
        return history_data

    # Main method to execute the VCP strategy and screen stocks
    def execute(self) -> None:
        for ticker_string in self.ticker_list:
            try:
                # Get historical data for the ticker
                ticker_history = self.get_ticker_history(ticker_string)
                if ticker_history.empty:
                    continue
                # Determine if the stock is in a Stage 2 uptrend
                trend_template_screener = self.trend_template(ticker_history)
                if trend_template_screener['Pass'][-1] == 1 and trend_template_screener['Pass'][-2] == 1:
                    print(f'{ticker_string} is in Stage 2')
                    # Determine if the stock forms a valid VCP pattern
                    vcp_screener = list(self.vcp(ticker_history))
                    rs = self.rs_rating(ticker_string)
                    if vcp_screener[-1] == 1 and rs >= 75:
                        vcp_screener.insert(0, ticker_string)
                        vcp_screener.insert(-1, rs)
                        self.radar.loc[len(self.radar)] = vcp_screener[0:6]
                        print(f'{ticker_string} has a VCP')
                    else:
                        print(f'{ticker_string} does not have a VCP')
                else:
                    print(f'{ticker_string} is not in Stage 2')
            except Exception as err:
                print(f'Get Error {err}')
        
        # Save the screening results in the database
        for index, row in self.radar.iterrows():
            stock: Stock = Stock.objects.get(ticker=row['Ticker'])
            obj = StrategyData.objects.create(
                stock=stock,
                strategy='VCP',
            )


def get_upcoming_earning_date(stock_ticker):
    stock = yf.Ticker(stock_ticker)
    earnings_dates = stock.earnings_dates
    today = pd.Timestamp('now').tz_localize('UTC')
    upcoming_earnings_date = earnings_dates[earnings_dates.index > today].index.min()
    return upcoming_earnings_date #Timestamp('2024-08-01 16:00:00-0400', tz='America/New_York')
