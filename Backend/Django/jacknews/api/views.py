import json
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from jacknews.models import JackNews
from jacknews.api.serializers import JackNewsSerializer, StockSignalSerializer

from jacknews.utils import StockSignal


class JacknewsViewSet(viewsets.ModelViewSet):
    queryset = JackNews.objects.all()
    serializer_class = JackNewsSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Deserialize input data
        serializer = StockSignalSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check stock symbol input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        # Retrieve validated data
        stock_symbol = serializer.validated_data.get('stocksymbol')
        try:
            SS = StockSignal()
            signal = 'BUY'
            gpt_result = SS.get_signal(stock_symbol)
            return Response({'success': True, 'signal': signal, 'gpt_result': gpt_result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='stock-symbols')
    def stock_symbols(self, request):
        try:
            with open('jacknews/stock_data.json', 'r') as file:
                stock_data = json.load(file)
            return Response(stock_data)
        except FileNotFoundError:
            return Response({"error": "Stock data file not found"}, status=status.HTTP_404_NOT_FOUND)
