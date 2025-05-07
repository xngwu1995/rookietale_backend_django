from django.contrib import admin
from django.utils.html import format_html
from .models import Stock, StrategyData, AIAnalysisData, StrategyRecordAnalysis, TradeRecord

class StrategyDataAdmin(admin.ModelAdmin):
    list_display = ('stock', 'created_at', 'strategy', 'analysis_link')
    list_filter = ('strategy', 'created_at')
    search_fields = ('stock__ticker',)

    def stock(self, obj):
        return obj.stock.ticker

    def analysis_link(self, obj):
        if StrategyRecordAnalysis.objects.filter(strategy_record=obj).exists():
            analysis = StrategyRecordAnalysis.objects.get(strategy_record=obj)
            return format_html('<a href="/admin/stocks/strategyrecordanalysis/{}/change/">View Analysis</a>', analysis.id)
        return "No Analysis"

    stock.admin_order_field = 'stock'
    stock.short_description = 'Stock Ticker'
    analysis_link.short_description = 'Analysis Link'

admin.site.register(StrategyData, StrategyDataAdmin)
admin.site.register(Stock)
admin.site.register(AIAnalysisData)
admin.site.register(StrategyRecordAnalysis)
admin.site.register(TradeRecord)
