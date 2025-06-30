from django.contrib import admin
from .models import Signal


@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing the final, multi-timeframe AI-generated signals.
    This interface is configured to be strictly read-only.
    """
    # FIX: Using the final, correct field names from the updated Signal model.
    list_display = (
        'get_symbol_name',
        'get_candle_timestamp',
        'direction_next_candle',
        'confidence_next_candle',
        'direction_3rd_candle',
        'created_at'
    )
    list_filter = ('candle__symbol__name', 'direction_next_candle', 'direction_3rd_candle')
    search_fields = ('candle__symbol__name',)
    date_hierarchy = 'candle__timestamp'
    ordering = ('-created_at',)

    # Make all fields read-only in the detail view
    readonly_fields = [field.name for field in Signal._meta.get_fields()]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # Custom methods for better display in the admin list
    @admin.display(description='Symbol', ordering='candle__symbol__name')
    def get_symbol_name(self, obj):
        if obj.candle and obj.candle.symbol:
            return obj.candle.symbol.name
        return "N/A"

    @admin.display(description='Candle Time', ordering='candle__timestamp')
    def get_candle_timestamp(self, obj):
        if obj.candle:
            return obj.candle.timestamp
        return "N/A"
