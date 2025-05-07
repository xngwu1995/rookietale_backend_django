import asyncio
from chatgpt.utils import ChatGPTApi
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from stocks.api.serializers import StrategyOptionDataSerializer, StrategyStockSerializer, TradeRecordSerializer, TradeRecordSerializerForCreate, TradeRecordUpdateSerializer
from stocks.models import Stock, StrategyData, StrategyOptionData, TradeRecord, AIAnalysisData
from stocks.utils import TradingDayAnalyzer
from utils.permissions import IsAdminUser, IsObjectOwner
from datetime import datetime
from django.core.cache import cache
from utils.utils import today_date


class StockViewSet(viewsets.GenericViewSet):
    queryset = Stock.objects.all()
    permission_classes = [IsAuthenticated]

    @action(methods=['GET'], detail=False, url_path="get-stocks")
    def get_stocks(self, request):
        stocks = self.queryset.values('id', 'ticker')
        return Response({
            'success': True,
            'stocks': list(stocks)
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path="get-screened-options")
    def get_screened_options(self, request):
        today_str = today_date()
        results = StrategyOptionData.objects.filter(created_at__date=today_str)
        options = StrategyOptionDataSerializer(results, many=True).data
        return Response({
            'success': True,
            'options': options
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path="get-money")
    def get_money(self, request):
        user = request.user
        dob = user.profile.dob.strftime('%Y-%m-%d')
        gender = user.profile.gender
        user_id = user.id
        today_str = datetime.now().strftime('%Y-%m-%d')
        cache_key = f"good_day_{today_str}_{user_id}_{dob}_{gender}"
        result, buy = cache.get(cache_key, (None, None))
        if not result or not buy:
            result, buy = TradingDayAnalyzer.is_good_day_to_trade(dob, gender)
            cache.set(cache_key, (result, buy))
        return Response({
            'success': True,
            'text': result,
            'buy': buy
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path="get-todays-vcp-options")
    def get_todays_vcp_options(self, request):
        today_str = today_date()

        # Get today's VCP stocks
        vcp_stocks = StrategyData.objects.filter(strategy=StrategyData.VCP, created_at__date=today_str)
        vcp_stock_ids = vcp_stocks.values_list('stock', flat=True)
        # Get option details for today's VCP stocks
        options = StrategyOptionData.objects.filter(stock__in=vcp_stock_ids, decision="Call", total_score__gte=15, created_at__date=today_str)
        
        # Serialize the available trading options
        available_options = [
            {option.stock.ticker: [option.decision, option.weight]} for option in options
        ]
        
        return Response({
            'success': True,
            'date': today_str,
            'available_options': available_options
        }, status=status.HTTP_200_OK)


class StrategyStockViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(methods=['GET'], detail=False, url_path="get-all-strategy-stocks")
    def get_all_strategy_stocks(self, request):
        queryset = StrategyData.objects.all()
        serializer = StrategyStockSerializer(queryset, many=True)
        stocks = serializer.data
        return Response({
            'success': True,
            'stocks': stocks
        }, status=status.HTTP_200_OK)


class TradeRecordViewSet(viewsets.GenericViewSet):
    queryset = TradeRecord.objects.all()
    permission_classes = [IsObjectOwner]
    serializer_class = TradeRecordSerializer

    @action(methods=['GET'], detail=False, url_path="get-all-trade-record")
    def get_all_trade_record(self, request):
        records = TradeRecord.objects.filter(user_id=request.user.id)
        serializer = self.serializer_class(records, many=True)
        return Response({
            'success': True,
            'trade_records': serializer.data
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path="create-trade-record")
    def create_trade_record(self, request):
        user_id = request.user.id
        data = request.data.copy()
        if 'user_id' not in data:
            data['user_id'] = user_id

        serializer = TradeRecordSerializerForCreate(data=data)
        if serializer.is_valid():
            trade_record = serializer.save()
            return Response({
                'success': True,
                'message': 'Trade record created successfully',
                'trade_record': self.serializer_class(trade_record).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Failed to create trade record',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['PUT'], detail=True, url_path="update-trade-record")
    def update_trade_record(self, request, pk=None):
        try:
            trade_record = self.get_object()
        except TradeRecord.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Trade record not found'
            }, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        # Map the fields to match the serializer's expected field names
        if 'sellReason' in data:
            data['sell_reason'] = data.pop('sellReason')[0]
        if 'sellPrice' in data:
            data['sell_price'] = data.pop('sellPrice')[0]
        if 'sellDate' in data:
            data['sell_date'] = data.pop('sellDate')[0]

        # Convert types where necessary
        if 'sell_price' in data and data['sell_price']:
            data['sell_price'] = float(data['sell_price'])
        if 'sell_date' in data and data['sell_date']:
            try:
                data['sell_date'] = datetime.strptime(data['sell_date'], '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid date format. Use YYYY-MM-DD for sell_date.'
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = TradeRecordUpdateSerializer(trade_record, data=data, partial=True)
        if serializer.is_valid():
            trade_record = serializer.save()
            return Response({
                'success': True,
                'message': 'Trade record updated successfully',
                'trade_record': self.serializer_class(trade_record).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Failed to update trade record',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

class AIAnalysisViewSet(viewsets.ModelViewSet):
    queryset = AIAnalysisData.objects.all()
    permission_classes = (IsAdminUser,)

    def get_async_signal(self, stock_symbols, language):
        chatgpt_api = ChatGPTApi()
        results = asyncio.run(chatgpt_api.async_stocks_analysis(stock_symbols, language))
        response_data = []
        for stock_symbol, result in zip(stock_symbols, results):
            response_data.append({
                'stock_symbol': stock_symbol,
                'gpt_result': result,
            })
            if language == 'chinese':
                cache.set(f"{stock_symbol}_gpt_c", result)
            elif language == 'english':
                cache.set(f"{stock_symbol}_gpt_e", result)
        return response_data

    def create(self, request, *args, **kwargs):
        data = request.data
        stock_symbols = data.getlist('stocks[]')
        language = data.get('languageSelect')
        cached_results = {}
        no_cache_symbols = []
        for stock_symbol in stock_symbols:
            if language == 'chinese':
                cached_result = cache.get(f"{stock_symbol}_gpt_c", None)
            elif language == 'english':
                cached_result = cache.get(f"{stock_symbol}_gpt_e", None)
            if cached_result:
                cached_results[stock_symbol] = cached_result
            else:
                no_cache_symbols.append(stock_symbol)
        response_data = self.get_async_signal(no_cache_symbols, language) if no_cache_symbols else []
        for stock_symbol, gpt_result in cached_results.items():
            response_data.append({
                'stock_symbol': stock_symbol,
                'gpt_result': gpt_result
            })

        return Response({'success': True, 'signals': response_data}, status=status.HTTP_200_OK)