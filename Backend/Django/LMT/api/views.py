from rest_framework import viewsets, status
from rest_framework.decorators import action
from utils.permissions import IsObjectOwner
from decimal import Decimal
from rest_framework.response import Response
from LMT.models import LMT, Stock
from LMT.api.serializers import LMTSerializerForCreate, LMTSerializer
from django.contrib.auth.models import User


class LMTViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (IsObjectOwner,)

    @action(methods=['POST'], detail=False)
    def add(self, request):
        request_data = request.data
        data = {key: request_data.get(key) if key == "symbol" else float(request_data.get(key)) for key in request_data.keys()}
        data['user_id'] = int(data.get("user_id"))
        user_id = request.user.id
        if user_id != data.get("user_id"):
            return Response({
                'success': False,
                'errors': "Incorrect user",
            }, status=status.HTTP_400_BAD_REQUEST)
        stock_symbol = data.get("stock_symbol")
        if LMT.objects.filter(user_id=user_id, stock__symbol=stock_symbol).exists():
            return Response({
                'success': True,
                'message': "Stock already exists!",
            }, status=status.HTTP_201_CREATED)
        serializer = LMTSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        lmt = serializer.save()
        return Response({
            'success': True,
            'stock': LMTSerializer(lmt).data
        }, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False, url_path="get-stocks")
    def get_stocks(self, request):
        user_id = request.user.id
        data = LMT.objects.filter(user_id=user_id)
        serializer = LMTSerializer(data, many=True)
        return Response({
            'success': True,
            'stocks': serializer.data
        }, status=status.HTTP_200_OK)

    @action(methods=['PUT'], detail=False, url_path="update-lmt")
    def update_lmt(self, request):
        user_id = request.user.id
        data = request.data
        symbol = data.get('symbol')
        cost = data.get('cost')
        quantity = data.get('quantity')
        if not symbol or cost is None or quantity is None:
            return Response({
                'success': False,
                'errors': 'Symbol, cost, and quantity are required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            stock = LMT.objects.get(user_id=user_id, stock__symbol=symbol)
            stock.cost = Decimal(cost)
            stock.quantity = Decimal(quantity)
            stock.save()

            serializer = LMTSerializer(stock)
            return Response({
                'success': True,
                'stock': serializer.data
            }, status=status.HTTP_200_OK)
        except LMT.DoesNotExist:
            return Response({
                'success': False,
                'errors': 'Stock not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['POST'], detail=False, url_path="update-all-stocks")
    def update_all_stocks(self, request):
        all_stocks = request.data.getlist('allstocks[]')
        user_id = request.user.id
        for stock in all_stocks:
            Stock.get_or_create(stock, gpt_analysis=False)
        stocks = LMT.objects.filter(user_id=user_id)
        serializer = LMTSerializer(stocks, many=True)
        return Response({
            'success': True,
            'stocks': serializer.data
        }, status=status.HTTP_200_OK)