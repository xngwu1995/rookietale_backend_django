from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

from utils.stock_info import StockSignal


class Stock(models.Model):
    symbol = models.CharField(max_length=80, unique=True)
    instructors = models.TextField()
    analysis = models.TextField()
    RANK_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('HOLD', 'Hold')
    ]
    current_price = models.DecimalField(max_digits=10, decimal_places=5)
    rank = models.CharField(max_length=4, choices=RANK_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    gpt_updated_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.symbol} - {self.rank}"

    @classmethod
    def get_or_create(cls, symbol, gpt_analysis=True):
        stock = Stock.objects.filter(symbol=symbol).first()
        now = datetime.now().strftime('%Y-%m-%d')
        SS = StockSignal()
        if stock:
            formated_updated_at = stock.updated_at.strftime('%Y-%m-%d')
            formated_gpt_updated_at = stock.gpt_updated_at.strftime('%Y-%m-%d')
            if not gpt_analysis and formated_updated_at < now:
                df_val, rank, current_price = SS.get_price(symbol)
                stock, _ = Stock.objects.update_or_create(
                    symbol=symbol,
                    defaults={
                        'instructors': df_val,
                        'rank': rank,
                        'current_price': current_price,
                    }
                )
                return stock
        if not stock or formated_gpt_updated_at < now:
            gpt_result, df_val, rank, current_price = SS.get_signal(symbol)
            stock, _ = Stock.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'instructors': df_val,
                    'analysis': gpt_result,
                    'rank': rank,
                    'current_price': current_price,
                    'gpt_updated_at': datetime.now(),
                }
            )
            return stock
        return stock

class LMT(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=5)
    cost = models.DecimalField(max_digits=10, decimal_places=5)

    def __str__(self):
        return f"{self.user.username} have {self.stock.symbol}"

    @property
    def net_worth(self):
        return (self.current_price - self.cost) * self.quantity
