from django.db import models
from django.contrib.auth.models import User
import yfinance as yf
from django.core.cache import cache


class Stock(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    company = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    country = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.ticker


class StrategyData(models.Model):
    VCP = 'VCP'
    STRATEGY_CHOICES = [
        (VCP, 'VCP'),
    ]

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    strategy = models.CharField(max_length=3, choices=STRATEGY_CHOICES, default=VCP)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f"{self.stock.ticker} - {self.created_at.strftime('%Y-%m-%d')}"


class AIAnalysisData(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    openai = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TradeRecord(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    cost = models.DecimalField(max_digits=10, decimal_places=5)
    quantity = models.DecimalField(max_digits=10, decimal_places=5)
    strategy = models.CharField(max_length=50)
    reason = models.CharField(max_length=50)
    created_date = models.DateField()
    active = models.BooleanField(default=True)
    sell_reason = models.CharField(max_length=255, blank=True, null=True)
    sell_price = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    sell_date = models.DateField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['stock']),
            models.Index(fields=['user']),
        ]
        ordering = ('-created_date',)

    def __str__(self):
        return f"{self.stock} - {self.quantity} @ {self.cost}"

    @property
    def revenue(self):
        if self.sell_price and self.sell_date:
            return (self.sell_price - self.cost) * self.quantity
        return None
    
    @property
    def closed(self):
        stock_highest_value_key = f"highest_{self.stock.ticker}_lastmonth"
        highest_price = cache.get(stock_highest_value_key, None)
        if not highest_price:
            stock_data = yf.download(self.stock.ticker, period="1mo", interval="1d")
            highest_price = stock_data['High'].max()
            cache.set(stock_highest_value_key, highest_price)

        if highest_price:
            return highest_price * 0.95
        return None
