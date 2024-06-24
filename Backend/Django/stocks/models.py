from django.db import models


class Stock(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    company = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    country = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.ticker


class StockHistoryData(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField()
    open_val = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close_val = models.FloatField()
    adj_close_val = models.FloatField()
    volume = models.BigIntegerField()

    def __str__(self) -> str:
        return f"{self.stock.ticker} - {self.date}"
