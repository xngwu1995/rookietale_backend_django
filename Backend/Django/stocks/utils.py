from datetime import datetime
import json
import yfinance as yf
import numpy as np
import pandas_ta as ta
from django.core.cache import cache
from stocks.models import Stock, StrategyOptionData
import random


class StockScreening:
    def __init__(self):
        self.stock_list = list(Stock.objects.values_list('ticker', flat=True))
        self.results = []
        self.cache_key = f"stock_options_result_{datetime.now().strftime('%Y-%m-%d')}"

    def get_results(self):
        cached_results = cache.get(self.cache_key)
        if cached_results is not None:
            return cached_results
        return self.run_screening()

    def run_screening(self):
        stock_list = list(Stock.objects.values_list('ticker', flat=True))

        for stock_symbol in stock_list:
            self.process_screen(stock_symbol)
        if self.results:
            StrategyOptionData.objects.bulk_create(self.results)
        return self.results

    def process_screen(self, ticker):
        try:
            print(f"Processing {ticker}...")
            stock = yf.Ticker(ticker)

            # Get current price
            current_price = self.get_current_price(stock)
            if current_price is None:
                return

            # Get options data
            if not self.get_options_data(stock, ticker):
                return

            # Get historical data and average volume
            hist, avg_volume = self.get_historical_data(stock, ticker)
            if hist is None:
                return

            # Calculate historical volatility
            hist_volatility = self.calculate_historical_volatility(hist)

            # Get fundamental factors
            financial_data = self.get_fundamental_factors(stock, ticker)
            if financial_data is None:
                return

            # Get technical indicators
            sma50, sma200, rsi = self.get_technical_indicators(hist)

            # Apply screening criteria
            criteria = self.apply_screening_criteria(avg_volume, hist_volatility, financial_data, sma50, sma200, rsi)

            # Evaluate criteria and store results
            self.evaluate_criteria(criteria, ticker, current_price, avg_volume, hist_volatility, financial_data, sma50, sma200, rsi)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    def get_current_price(self, stock):
        try:
            return stock.history(period='1d')['Close'].iloc[-1]
        except Exception:
            print("Unable to fetch current price. Skipping.")
            return None

    def get_options_data(self, stock, ticker):
        try:
            options_volume, open_interest, implied_volatility = 0, 0, []
            expirations = stock.options
            if not expirations:
                print(f"No options data for {ticker}. Skipping.")
                return False

            nearest_exp = expirations[0]  # Considering only the nearest expiration
            opt = stock.option_chain(nearest_exp)
            calls, puts = opt.calls, opt.puts

            options_volume += calls['volume'].sum() + puts['volume'].sum()
            open_interest += calls['openInterest'].sum() + puts['openInterest'].sum()
            implied_volatility.extend(calls['impliedVolatility'].dropna().tolist())
            implied_volatility.extend(puts['impliedVolatility'].dropna().tolist())

            self.options_volume = options_volume
            self.open_interest = open_interest
            self.avg_implied_volatility = np.mean(implied_volatility) if implied_volatility else None
            return True
        except Exception as e:
            print(f"Error fetching options data for {ticker}: {e}")
            return False

    def get_historical_data(self, stock, ticker):
        try:
            hist = stock.history(period='1y')
            hist.dropna(subset=['Close'], inplace=True)
            if hist.empty:
                print(f"No historical data for {ticker}. Skipping.")
                return None, None
            avg_volume = hist['Volume'].mean()
            return hist, avg_volume
        except Exception as e:
            print(f"Error fetching historical data for {ticker}: {e}")
            return None, None

    def calculate_historical_volatility(self, hist):
        hist['Returns'] = hist['Close'].pct_change()
        return hist['Returns'].std() * np.sqrt(252)  # 252 trading days in a year

    def get_fundamental_factors(self, stock, ticker):
        try:
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            if financials.empty or balance_sheet.empty:
                print(f"Incomplete fundamental data for {ticker}. Skipping.")
                return None

            recent_revenue_growth = self.calculate_revenue_growth(financials, ticker)
            total_debt, total_equity = self.get_debt_and_equity(balance_sheet)
            debt_to_equity = total_debt / total_equity if total_equity != 0 else np.nan
            net_income = financials.loc['Net Income'].iloc[0] if 'Net Income' in financials.index else np.nan

            return {
                'recent_revenue_growth': recent_revenue_growth,
                'debt_to_equity': debt_to_equity,
                'net_income': net_income
            }
        except Exception as e:
            print(f"Error fetching fundamental data for {ticker}: {e}")
            return None

    def calculate_revenue_growth(self, financials, ticker):
        try:
            revenues = financials.loc['Total Revenue'].dropna()
            if len(revenues) < 2:
                print(f"Not enough revenue data for {ticker}. Skipping.")
                return None
            return (revenues.iloc[0] - revenues.iloc[1]) / revenues.iloc[1]
        except Exception:
            return None

    def get_debt_and_equity(self, balance_sheet):
        debt_labels = ['Total Debt', 'Long Term Debt', 'Long Term Debt & Capital Lease Obligation']
        equity_labels = ['Total Stockholder Equity', 'Total Shareholder Equity', 'Total Equity Gross Minority Interest']
        total_debt = self.get_financial_value(balance_sheet, debt_labels)
        total_equity = self.get_financial_value(balance_sheet, equity_labels)
        return total_debt, total_equity

    def get_financial_value(self, data, labels):
        for label in labels:
            if label in data.index:
                return data.loc[label].iloc[0]
        return np.nan

    def get_technical_indicators(self, hist):
        hist['SMA50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA200'] = hist['Close'].rolling(window=200).mean()
        hist['RSI'] = ta.rsi(hist['Close'], length=14)
        return hist['SMA50'].iloc[-1], hist['SMA200'].iloc[-1], hist['RSI'].iloc[-1]

    def apply_screening_criteria(self, avg_volume, hist_volatility, financial_data, sma50, sma200, rsi):
        return {
            'Options Volume': (self.options_volume > 10_000, 1),
            'Open Interest': (self.open_interest > 10_000, 1),
            'Average Volume': (avg_volume > 1_000_000, 2),
            'Historical Volatility': (hist_volatility > 0.3, 1),
            'Implied Volatility': (self.avg_implied_volatility is not None and self.avg_implied_volatility > 0.3, 2),
            'Revenue Growth': (financial_data['recent_revenue_growth'] is not None and financial_data['recent_revenue_growth'] > 0, 3),
            'Debt to Equity': (financial_data['debt_to_equity'] is not None and not np.isnan(financial_data['debt_to_equity']) and financial_data['debt_to_equity'] < 1.0, 2),
            'Net Income': (financial_data['net_income'] is not None and not np.isnan(financial_data['net_income']) and financial_data['net_income'] > 0, 3),
            'Trend': (sma50 > sma200, 2),
            'RSI': (rsi < 70, 1),
        }

    def evaluate_criteria(self, criteria, ticker, current_price, avg_volume, hist_volatility, financial_data, sma50, sma200, rsi):
        total_score, criteria_values = 0, {}

        for criterion, (met, score) in criteria.items():
            if met:
                total_score += score
            criteria_values[criterion] = {
                'value': self.get_actual_value(criterion, current_price, avg_volume, hist_volatility, financial_data, sma50, sma200, rsi)
            }
        price_sma_diff = ((current_price - sma50) / sma50) * 100
        threshold = 2.0  # This can be adjusted based on preference
        if abs(price_sma_diff) <= threshold:
            # Proceed with the strategy as the price is close to the SMA
            if current_price > sma50:
                decision = 'Call'
            else:
                decision = 'Put'
        else:
            # The price is far from the SMA; exercise caution
            decision = 'Hold'

        # Check if all required data is present before appending to result
        if all(value is not None for value in [ticker, criteria_values, total_score, decision, price_sma_diff]):
            self.results.append(StrategyOptionData(
                stock=self.stock,
                criteria=json.dumps(criteria_values),
                total_score=total_score,
                decision=decision,
                weight=price_sma_diff
            ))

    def get_actual_value(self, criterion, current_price, avg_volume, hist_volatility, financial_data, sma50, sma200, rsi):
        values = {
            'Options Volume': self.options_volume,
            'Open Interest': self.open_interest,
            'Average Volume': avg_volume,
            'Historical Volatility': hist_volatility,
            'Implied Volatility': self.avg_implied_volatility,
            'Revenue Growth': financial_data['recent_revenue_growth'],
            'Debt to Equity': financial_data['debt_to_equity'],
            'Net Income': financial_data['net_income'],
            'Trend': {'SMA50': sma50, 'SMA200': sma200},
            'RSI': rsi,
            'Current Price': current_price
        }
        return values.get(criterion, None)


# 天干
HEAVENLY_STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
# 地支
EARTHLY_BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
# 五行
FIVE_ELEMENTS = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水',
    '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
    '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'
}

class TradingDayAnalyzer:
    @staticmethod
    def get_heavenly_stem_earthly_branch(year, month, day):
        """
        根据公历日期计算天干地支年、月、日柱。
        """
        # 这里只是示例，实际需要精确的农历转换和天干地支计算
        # 以下为简化的计算方法

        # 计算日差
        base_date = datetime(1900, 1, 31)
        delta_days = (datetime(year, month, day) - base_date).days

        # 天干地支周期为60
        gan_index = delta_days % 10
        zhi_index = delta_days % 12

        gan = HEAVENLY_STEMS[gan_index % 10]
        zhi = EARTHLY_BRANCHES[zhi_index % 12]

        return gan, zhi

    @staticmethod
    def calculate_five_elements(gan_zhi_list):
        """
        根据天干地支列表计算五行属性。
        """
        elements = []
        for gan_zhi in gan_zhi_list:
            gan, zhi = gan_zhi
            elements.append(FIVE_ELEMENTS[gan])
            elements.append(FIVE_ELEMENTS[zhi])
        return elements

    @staticmethod
    def analyze_fortune(user_elements, today_elements):
        """
        分析用户的五行与当天五行的生克关系，生成运势结果。
        """
        # 简化的生克关系：金生水，水生木，木生火，火生土，土生金
        generating = {'金': '水', '水': '木', '木': '火', '火': '土', '土': '金'}
        overcoming = {'金': '木', '木': '土', '土': '水', '水': '火', '火': '金'}

        score = 0

        for ue in user_elements:
            for te in today_elements:
                if generating[ue] == te:
                    score += random.randint(-10, 10)  # 生
                elif overcoming[ue] == te:
                    score -= random.randint(-10, 10)  # 克

        return score

    @staticmethod
    def is_good_day_to_trade(dob: str, gender: str) -> str:
        # Convert DOB to datetime object
        dob_date = datetime.strptime(dob, "%Y-%m-%d")
        today = datetime.now()

        # Get user's BaZi (Four Pillars)
        user_year_gz = TradingDayAnalyzer.get_heavenly_stem_earthly_branch(dob_date.year, dob_date.month, dob_date.day)
        user_month_gz = TradingDayAnalyzer.get_heavenly_stem_earthly_branch(dob_date.year, dob_date.month, 1)  # 简化处理
        user_day_gz = TradingDayAnalyzer.get_heavenly_stem_earthly_branch(dob_date.year, dob_date.month, dob_date.day)

        # Get today's GanZhi
        today_year_gz = TradingDayAnalyzer.get_heavenly_stem_earthly_branch(today.year, today.month, today.day)
        today_month_gz = TradingDayAnalyzer.get_heavenly_stem_earthly_branch(today.year, today.month, 1)  # 简化处理
        today_day_gz = TradingDayAnalyzer.get_heavenly_stem_earthly_branch(today.year, today.month, today.day)

        # Calculate user's Five Elements
        user_elements = TradingDayAnalyzer.calculate_five_elements([user_year_gz, user_month_gz, user_day_gz])

        # Calculate today's Five Elements
        today_elements = TradingDayAnalyzer.calculate_five_elements([today_year_gz, today_month_gz, today_day_gz])

        # Analyze fortune
        fortune_score = TradingDayAnalyzer.analyze_fortune(user_elements, today_elements)

        # Adjust score based on gender (示例调整，可以根据需要修改)
        if gender.lower() == "male":
            fortune_score += random.randint(-10, 10)
        elif gender.lower() == "female":
            fortune_score += random.randint(-10, 10)

        # Determine if today is a good day for trading
        if fortune_score > random.randint(0, 100):
            result = "根据古老的命理分析，今天是交易的好日子！"
        else:
            result = "根据古老的命理分析，今天可能不太适合交易。"

        # 可以加入更多的分析和解释
        return result
