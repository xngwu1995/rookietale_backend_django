import asyncio
from chatgpt.utils import ChatGPTApi
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from stocks.api.serializers import StrategyStockSerializer, TradeRecordSerializer, TradeRecordSerializerForCreate, TradeRecordUpdateSerializer
from stocks.models import Stock, StrategyData, TradeRecord, AIAnalysisData
from utils.permissions import IsAdminUser, IsObjectOwner
from datetime import datetime


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


class StrategyStockViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(methods=['GET'], detail=False, url_path="get-all-strategy-stocks")
    def get_all_strategy_stocks(self, request):
        queryset = StrategyData.objects.all()
        serializer = StrategyStockSerializer(queryset, many=True)
        return Response({
            'success': True,
            'stocks': serializer.data
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

    def get_async_signal(self, stock_symbols):
        chatgpt_api = ChatGPTApi()
        results = asyncio.run(chatgpt_api.async_stocks_analysis(stock_symbols))
        response_data = []
        for stock_symbol, result in zip(stock_symbols, results):
            response_data.append({
                'stock_symbol': stock_symbol,
                'gpt_result': result,
            })
        return response_data

    def create(self, request, *args, **kwargs):
        stock_symbols = request.data.getlist('stocksymbols[]') 
        response_data = self.get_async_signal(stock_symbols)

        return Response({'success': True, 'signals': response_data}, status=status.HTTP_200_OK)