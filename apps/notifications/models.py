from django.db import models
from django.conf import settings

class Notification(models.Model):
    class Type(models.TextChoices):
        NEW_ORDER = "new_order", "New Order"
        ORDER_PLACED = "order_placed", "Order Placed"
        ORDER_SHIPPED = "order_shipped", "Order Shipped"
        ORDER_DELIVERED = "order_delivered", "Order Delivered"
        ORDER_CANCELLED = "order_cancelled", "Order Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=Type.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    order_id = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['user']), models.Index(fields=['is_read']), models.Index(fields=['-created_at'])]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"
