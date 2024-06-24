from django.core.management.base import BaseCommand
from utils.finviz.screener import Screener
from stocks.models import Stock
from typing import List


class Command(BaseCommand):
    help: str = 'Import stock data into the Stock model using bulk create'

    def handle(self, *args, **kwargs) -> None:
        stock_list: Screener = Screener()
        all_stocks_data: List = stock_list.data
        stock_objects: List = []

        for stock_data in all_stocks_data:
            ticker: str = stock_data['Ticker']
            company: str = stock_data['Company']
            sector: str = stock_data['Sector']
            industry: str = stock_data['Industry']
            country:str = stock_data['Country']
            
            stock_objects.append(Stock(
                ticker=ticker,
                company=company,
                sector=sector,
                industry=industry,
                country=country
            ))
        
        Stock.objects.bulk_create(stock_objects, ignore_conflicts=True)
        
        self.stdout.write(self.style.SUCCESS('Successfully imported stock data using bulk create'))
