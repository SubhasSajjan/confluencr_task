import time
from celery import shared_task
from django.utils import timezone
from .models import Transaction

@shared_task
def process_transaction(transaction_id):
    transaction = Transaction.objects.get(transaction_id=transaction_id)

    if transaction.status == Transaction.Status.PROCESSED:
        return

    time.sleep(30)

    transaction.status = Transaction.Status.PROCESSED
    transaction.processed_at = timezone.now()
    transaction.save()
