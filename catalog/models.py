from django.db import models

class Order(models.Model):
    basket_data = models.JSONField()  # Store basket data as JSON
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the order is created

    def __str__(self):
        return f"Order #{self.pk}"
