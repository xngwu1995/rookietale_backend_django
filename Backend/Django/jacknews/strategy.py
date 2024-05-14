import pandas as pd
import pandas_ta as ta
import numpy as np
from yahoo_fin import stock_info as si
import datetime


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
