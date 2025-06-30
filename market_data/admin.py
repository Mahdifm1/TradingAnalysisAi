from django.contrib import admin
from .models import Symbol, Candle


@admin.register(Symbol)
class SymbolAdmin(admin.ModelAdmin):
    """
    Admin interface for managing trading symbols.
    Admins can add new symbols and activate/deactivate them for data fetching.
    """
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Candle)
class CandleAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing candle data.
    This interface is strictly read-only to ensure data integrity,
    as candle data should only be populated by the automated fetching tasks.
    """
    list_display = ('symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume')
    list_filter = ('symbol',)
    search_fields = ('symbol__name',)
    date_hierarchy = 'timestamp'  # Allows for quick date-based navigation
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        """Prevent admins from manually adding candles."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent admins from manually editing candles."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion for maintenance, but it's generally not recommended."""
        # You can change this to False if you want to prevent any deletion.
        return True
