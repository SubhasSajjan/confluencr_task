from django.db import models

class Transaction(models.Model):

    class Status(models.TextChoices):
        PROCESSING = "PROCESSING"
        PROCESSED = "PROCESSED"

    transaction_id = models.CharField(max_length=100, unique=True)
    source_account = models.CharField(max_length=100)
    destination_account = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROCESSING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
