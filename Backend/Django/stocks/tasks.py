import logging
import json
from celery import shared_task
from stocks.utils import StockScreening
from utils.strategy import VCP_Strategy
from stocks.models import Stock


logger = logging.getLogger(__name__)


@shared_task
def get_latest_vcp_strategy():
    logger.info("Starting get_latest_vcp_strategy task.")
    vcp_strategy = VCP_Strategy()
    vcp_strategy.execute()
    logger.info("Completed get_latest_vcp_strategy task.")


def insert_stock_data():
    with open('stocks_data.json', 'r') as json_file:
        stock_list = json.load(json_file)

    stocks = []
    for data in stock_list:
        stock = Stock(
            ticker=data['Ticker'],
            company=data['Company'],
            sector=data['Sector'],
            industry=data['Industry'],
            country=data['Country']
        )
        stocks.append(stock)
    Stock.objects.bulk_create(stocks, ignore_conflicts=True)


def export_stocks():
    stocks = Stock.objects.all()
    stock_list = []

    for stock in stocks:
        stock_list.append({
            'Ticker': stock.ticker,
            'Company': stock.company,
            'Sector': stock.sector,
            'Industry': stock.industry,
            'Country': stock.country,
        })

    with open('stocks_data.json', 'w') as json_file:
        json.dump(stock_list, json_file, indent=4)


@shared_task
def get_async_options():
    logger.info("Starting get_async_options task.")
    screener = StockScreening()
    screener.run_screening()
    logger.info("Completed get_async_options task.")

