from django.db import models
from django.utils import timezone
from django.db.models import Sum

class Table(models.Model):
    PS_CHOICES = [(4,'PS4'),(5,'PS5')]
    name            = models.CharField(max_length=50)
    ps_type         = models.IntegerField(choices=PS_CHOICES)
    is_open         = models.BooleanField(default=False)
    is_vip          = models.BooleanField(default=False)    # ← VIP flag

    @property
    def current_session_start(self):
        if self.is_open:
            sess = self.session_set.filter(end_time__isnull=True).last()
            if sess: return sess.start_time.isoformat()
        return ''

    @property
    def current_items(self):
        if self.is_open:
            sess = self.session_set.filter(end_time__isnull=True).last()
            if sess: return sess.items.all()
        return []

    @property
    def current_controllers(self):
        if self.is_open:
            sess = self.session_set.filter(end_time__isnull=True).last()
            if sess: return sess.controllers
        return 2


class Pricing(models.Model):
    ps_type      = models.IntegerField(choices=Table.PS_CHOICES, unique=True)
    hourly_rate  = models.DecimalField(max_digits=6, decimal_places=2)


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.price})"

from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.db.models import Sum


class Session(models.Model):
    table        = models.ForeignKey(Table, on_delete=models.CASCADE)
    start_time   = models.DateTimeField(default=timezone.now)
    end_time     = models.DateTimeField(null=True, blank=True)
    controllers  = models.PositiveIntegerField(default=2)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    @property
    def total_price(self):
        pricing   = Pricing.objects.get(ps_type=self.table.ps_type)
        # süre (saniye)
        duration  = (self.end_time or timezone.now()) - self.start_time
        secs      = Decimal(duration.total_seconds())
        if secs < Decimal(3600):
            secs = Decimal(3600)
        hours     = secs / Decimal(3600)

        # ekstra kol ücreti
        extra     = max(self.controllers - 2, 0)
        extra_rate = Decimal('25') if self.table.ps_type == 4 else Decimal('40')

        # base rate + ekstra kontroller
        rate      = pricing.hourly_rate + extra_rate * extra

        # VIP ise tüm saatlik ücreti 2×
        if self.table.is_vip:
            rate = rate * Decimal('2')

        base_cost = rate * hours

        items_sum = self.items.aggregate(s=Sum('product__price'))['s'] or Decimal('0')
        return base_cost + items_sum


class SessionItem(models.Model):
    session = models.ForeignKey(Session, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.session} - {self.product.name}"
