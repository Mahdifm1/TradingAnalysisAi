from django.db import models


class Symbol(models.Model):
    name = models.CharField(max_length=20, unique=True,
                            help_text="The symbol name as provided by the API (e.g., BTC-USDT)")
    is_active = models.BooleanField(default=True, help_text="Enable/disable data fetching for this symbol")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Symbols"


class Candle(models.Model):
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name='candles')
    timestamp = models.DateTimeField(help_text="The start time of the candle")
    open = models.DecimalField(max_digits=18, decimal_places=8)
    high = models.DecimalField(max_digits=18, decimal_places=8)
    low = models.DecimalField(max_digits=18, decimal_places=8)
    close = models.DecimalField(max_digits=18, decimal_places=8)
    volume = models.DecimalField(max_digits=24, decimal_places=8)

    def __str__(self):
        return f"{self.symbol.name} @ {self.timestamp}"

    class Meta:
        # Ensure that there is only one candle per symbol for a given timestamp
        unique_together = ('symbol', 'timestamp')
        ordering = ['-timestamp']
