import pandas as pd
import numpy as np
from yahoo_fin import stock_info as si
import datetime
import os
from yahoo_fin import stock_info as si
from pandas import DataFrame, Series
from numpy import ndarray
from utils.finviz.screener import Screener # type: ignore
from scipy.signal import argrelextrema # type: ignore
from typing import List, Tuple, Dict, Optional
from stocks.models import Stock, StockHistoryData


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


class VCP_Strategy:

    def __init__(self) -> None:
        self.ticker_list: List[str]
        self.rs_dict: Dict[str, int]
        self.df_spx: Dict[str, float]
        self.ticker_list, self.rs_dict, self.df_spx = self.get_init_data()
        self.radar: DataFrame = DataFrame({
            'Ticker': [],
            'Num_of_contraction': [],
            'Max_contraction': [],
            'Min_contraction': [],
            'Weeks_of_contraction': [],
            'RS_rating': []
        })

    def get_init_data(self):
        # Define file paths
        ticker_csv = 'tickers.csv'
        rs_csv = 'rs_ratings.csv'
        spx_csv = 'spx_data.csv'
        filters = ['cap_smallover','sh_avgvol_o100','sh_price_o2','ta_sma200_sb50','ta_sma50_pa']
        # Load data if CSV files exist, otherwise fetch and save the data
        if os.path.exists(ticker_csv):
            ticker_table = pd.read_csv(ticker_csv)
            ticker_list = ticker_table['Ticker'].to_list()
        else:
            # Fetch and save ticker data
            stock_list = Screener(filters=filters, table='Performance', order='asc', rows=960)
            ticker_table = pd.DataFrame(stock_list.data)
            ticker_list = ticker_table['Ticker'].to_list()
            ticker_table.to_csv(ticker_csv, index=False)

        if os.path.exists(rs_csv):
            rs_table = pd.read_csv(rs_csv)
            rs_list = rs_table['Ticker'].to_list()
        else:
            # Fetch and save RS data
            performance_table = Screener(table='Performance', order='-perf52w', rows=3000)
            rs_table = pd.DataFrame(performance_table.data)
            rs_list = rs_table['Ticker'].to_list()
            rs_table.to_csv(rs_csv, index=False)

        rs_dict = {value: index for index, value in enumerate(rs_list)}
        end_date = pd.to_datetime('today')
        start_date = end_date - pd.DateOffset(years=2)
        df_spx = si.get_data(ticker='^GSPC', start_date=start_date, end_date=end_date)

        return ticker_list, rs_dict, df_spx

    # determine whether MA200 is uptrend or not
    def trend_value(self, nums: List[float]) -> float:
        summed_nums: float = sum(nums)
        multiplied_data: float = 0
        summed_index: float = 0 
        squared_index: float = 0

        for index, num in enumerate(nums):
            index += 1
            multiplied_data += index * num
            summed_index += index
            squared_index += index**2

        numerator: float = (len(nums) * multiplied_data) - (summed_nums * summed_index)
        denominator: float = (len(nums) * squared_index) - summed_index**2
        if denominator != 0:
            return numerator / denominator
        else:
            return 0

    # determine whether the ticker fulfills trend template
    def trend_template(self, df: DataFrame) -> DataFrame:
        # calculate moving averages
        df['MA_50'] = round(df['Close'].rolling(window=50).mean(), 2)
        df['MA_150'] = round(df['Close'].rolling(window=150).mean(), 2)
        df['MA_200'] = round(df['Close'].rolling(window=200).mean(), 2)
        
        if len(df.index) > 5 * 52:
            df['52_week_low'] = df['Low'].rolling(window = 5*52).min()
            df['52_week_high'] = df['High'].rolling(window = 5*52).max()
        else:
            df['52_week_low'] = df['Low'].rolling(window = len(df.index)).min()
            df['52_week_high'] = df['High'].rolling(window = len(df.index)).max()
        
        # condition 1&5: Price is above both 150MA and 200MA & above 50MA
        df['condition_1'] = (df['Close'] > df['MA_150']) & (df['Close'] > df['MA_200']) & (df['Close'] > df['MA_50'])
        
        # condition 2&4: 150MA is above 200MA & 50MA is above both
        df['condition_2'] = (df['MA_150'] > df['MA_200']) & (df['MA_50'] > df['MA_150'])
        
        # condition 3: 200MA is trending up for at least 1 month
        slope: Series = df['MA_200'].rolling(window = 20).apply(self.trend_value, raw=True)
        df['condition_3'] = slope > 0.0
        
        # condition 6: Price is at least 30% above 52 week low
        df['condition_6'] = df['Low'] > (df['52_week_low'] * 1.3)
        
        # condition 7: Price is at least 25% of 52 week high
        df['condition_7'] = df['High'] > (df['52_week_high'] * 0.75)
        
        # condition 9 (additional): The relative strength line, which compares a stock's price performance to that of the S&P 500.
        # An upward trending RS line tells you the stock is outperforming the general market.
        df['RS'] = df['Close'] / self.df_spx['close']
        slope_rs: Series = df['RS'].rolling(window = 20).apply(self.trend_value, raw=True)
        df['condition_8'] = slope > 0.0
        df['condition_9'] = slope_rs > 0.0
        
        df['Pass'] = df[
            ['condition_1','condition_2','condition_3','condition_6','condition_7','condition_8', 'condition_9']
        ].all(axis='columns')
        
        return df

    # determine local maxima and minima
    def local_high_low(self, df: DataFrame) -> Tuple[List[int], List[int]]:
        local_high: ndarray = argrelextrema(df['High'].to_numpy(),np.greater,order=10)[0]
        local_low: ndarray = argrelextrema(df['Low'].to_numpy(),np.less,order=10)[0]
        
        # eliminate for consecutive highs or lows
        # create adjusted local highs and lows
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
        
        # add any remaining elements from local_high or local_low
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

    # measure the depth of contractions
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

    # measure number of contractions
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

    # measure depth of maximum and minimum contraction
    def max_min_contraction(self, contraction: List[float], num_of_contractions: int) -> Tuple[float, float]:
        max_contraction = contraction[num_of_contractions - 1]
        min_contraction = contraction[0]
        return max_contraction, min_contraction

    # measure days of contraction
    def weeks_of_contraction(self, df: DataFrame, local_high: List[int], num_of_contractions: int) -> float:
        week_of_contraction: float = (len(df.index) - local_high[::-1][num_of_contractions - 1]) / 5
        return week_of_contraction

    # determine whether the ticker has VCP
    def vcp(self, df: DataFrame) -> Tuple[int, float, float, float, int]:
        # prepare data for contractions measurement
        local_high: List[int]
        local_low: List[int]
        local_high, local_low = self.local_high_low(df)

        contraction: List[float] = self.contractions(df, local_high, local_low)
        
        # calculate no. of contractions
        num_of_contraction: int = self.num_of_contractions(contraction)
        if 2 <= num_of_contraction <= 4:
            flag_num = 1
        else:
            flag_num = 0
        
        # calculate depth of contractions
        max_c: float = 0.0
        min_c: float = 0.0
        flag_max: int = 1
        flag_min: int = 0

        max_c, min_c = self.max_min_contraction(contraction, num_of_contraction)
        if max_c > 50:
            flag_max = 0

        if min_c <= 15:
            flag_min = 1

        # calculate weeks of contractions
        week_of_contraction: float = self.weeks_of_contraction(df, local_high, num_of_contraction)
        flag_week: int = 0
        if week_of_contraction >= 2:
            flag_week = 1
        
        df['30_day_avg_volume'] = round(df['Volume'].rolling(window = 30).mean(),2)
        df['5_day_avg_volume'] = round(df['Volume'].rolling(window = 5).mean(),2)
        # criteria_2: Volume contraction
        flag_vol: int = 0
        df['vol_contraction'] = df['5_day_avg_volume'] < df['30_day_avg_volume']
        if df['vol_contraction'][-1] == 1:
            flag_vol = 1
            
        # criteria 3: Not break out yet
        flag_consolidation: int = 0
        if df['High'].iloc[-1] < df['High'].iloc[local_high[-1]]:
            flag_consolidation = 1
        
        flag_final: int = 0
        if flag_num == 1 & flag_max == 1 & flag_min == 1 & flag_week == 1 & flag_vol == 1 & flag_consolidation == 1:
            flag_final = 1
        
        return num_of_contraction, max_c, min_c, week_of_contraction, flag_final

    # calculate RS rating
    def rs_rating(self, ticker: str) -> int:
        total_stocks: int = 478 * 20
        ticker_index: Optional[int] = self.rs_dict.get(ticker)
        rs: int = 0
        if ticker_index:
            rs = int(round((total_stocks - ticker_index) / total_stocks * 100, 0))
        return rs

    def get_ticker_history(self, stock_ticker: str, period: int = 2) -> pd.DataFrame:
        # Calculate the start date based on the period in years
        end_date = pd.to_datetime('today')
        start_date = end_date - pd.DateOffset(years=period)

        # Query the Stock and StockHistoryData tables
        stock = Stock.objects.get(ticker=stock_ticker)
        history_data = StockHistoryData.objects.filter(
            stock=stock,
            date__range=[start_date, end_date]
        ).values(
            'date', 'open_val', 'high', 'low', 'close_val', 'adj_close_val', 'volume'
        ).order_by('date')

        # Convert the queryset to a DataFrame
        ticker_history = pd.DataFrame.from_records(history_data)
        ticker_history.set_index('date', inplace=True)
        ticker_history.index = pd.to_datetime(ticker_history.index)

        # Rename columns to match the yfinance format
        ticker_history.rename(columns={
            'open_val': 'Open',
            'high': 'High',
            'low': 'Low',
            'close_val': 'Close',
            'adj_close_val': 'Adj Close',
            'volume': 'Volume'
        }, inplace=True)

        return ticker_history

    def execute(self) -> None:
        for ticker_string in self.ticker_list:
            try:
                ticker_history = self.get_ticker_history(stock_ticker=ticker_string, period=2) # Get the data of stocks
                trend_template_screener = self.trend_template(ticker_history) # Determine whether the stocks is in Stage 2
                if trend_template_screener['Pass'][-1] == 1 and trend_template_screener['Pass'][-2] == 1:
                    print(f'{ticker_string} is in Stage 2')
                    vcp_screener = list(self.vcp(ticker_history)) # Determine whether the stocks is in Stage 2
                    rs = self.rs_rating(ticker_string) # Calculate RS rating
                    if vcp_screener[-1] == 1 and rs >= 70:
                        vcp_screener.insert(0, ticker_string)
                        vcp_screener.insert(-1, rs)
                        self.radar.loc[len(self.radar)] = vcp_screener[0:6] # Store the results to the dataframe
                        print(f'{ticker_string} has a VCP')
                    else:
                        print(f'{ticker_string} does not have a VCP')
                else:
                    print(f'{ticker_string} is not in Stage 2')
            except Exception as err:
                print(f'Get Error {err}')
        print('Finished!!!')
        print(f'{len(self.radar)} stocks pass')

        print(self.radar)