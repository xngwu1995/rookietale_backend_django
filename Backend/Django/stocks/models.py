from django.db import models


class Stock(models.Model):
    ticker: str = models.CharField(max_length=10, unique=True)
    company: str = models.CharField(max_length=100)
    sector: str = models.CharField(max_length=100)
    industry: str = models.CharField(max_length=100)
    country: str = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.ticker
