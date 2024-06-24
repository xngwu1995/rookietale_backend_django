from yahoo_fin import stock_info as si
from django.core.management.base import BaseCommand
from stocks.models import Stock, StockHistoryData
from typing import List, Tuple

class Command(BaseCommand):
    help: str = 'Import history stock data into the StockHistoryData model using bulk create'

    def handle(self, *args, **kwargs) -> None:
        all_stocks_data: List[Tuple[str, int]] = list(Stock.objects.all().values_list('ticker', 'id'))
        history_stock_objects: List[StockHistoryData] = []
        batch_size = 50000

        for symbol, stock_id in all_stocks_data:
            try:
                data = si.get_data(ticker=symbol)
                if data.isnull().values.any():
                    history_data = data.dropna()
                else:
                    history_data = data
                if history_data.empty:
                    continue
                for date, row in history_data.iterrows():
                    open_val: float = row['open']
                    high: float = row['high']
                    low: float = row['low']
                    close_val: float = row['close']
                    adj_close_val: float = row['adjclose']
                    volume: float = row['volume']
                    history_stock_objects.append(
                        StockHistoryData(
                            stock_id=stock_id,
                            date=date,
                            open_val=open_val if open_val else 0,
                            high=high if high else 0,
                            low=low if low else 0,
                            close_val=close_val if close_val else 0,
                            adj_close_val=adj_close_val if adj_close_val else 0,
                            volume=volume if volume else 0,
                        )
                    )
                if len(history_stock_objects) >= batch_size:
                    StockHistoryData.objects.bulk_create(history_stock_objects, ignore_conflicts=True)
                    self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(history_stock_objects)} stock data using bulk create'))
                    history_stock_objects = []
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fetching data for {symbol}: {e}"))
                continue

        if history_stock_objects:
            StockHistoryData.objects.bulk_create(history_stock_objects, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS('Successfully imported stock data using bulk create'))
