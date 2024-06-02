from django.db import models
from django.contrib.auth.models import User


class Stock(models.Model):
    symbol = models.CharField(max_length=80, unique=True)
    instructors = models.TextField()
    analysis = models.TextField()
    RANK_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('HOLD', 'Hold')
    ]
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    rank = models.CharField(max_length=4, choices=RANK_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.symbol} - {self.rank}"


class LMT(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} have {self.stock.symbol}"

    @property
    def net_worth(self):
        return (self.current_price - self.cost) * self.quantity
