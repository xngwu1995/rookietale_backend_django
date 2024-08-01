from django.contrib import admin

# Register your models here.
from .models import Stock, StrategyData, AIAnalysisData

class StrategyDataAdmin(admin.ModelAdmin):
    list_display = ('stock', 'created_at', 'strategy')
    list_filter = ('strategy', 'created_at')
    search_fields = ('stock__ticker',)

    def stock(self, obj):
        return obj.stock.ticker

    stock.admin_order_field = 'stock'
    stock.short_description = 'Stock Ticker'

admin.site.register(StrategyData, StrategyDataAdmin)
admin.site.register(Stock)
admin.site.register(AIAnalysisData)
