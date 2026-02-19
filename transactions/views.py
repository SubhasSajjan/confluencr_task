from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.utils.timezone import now

from .models import Transaction
from .tasks import process_transaction


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status": "HEALTHY",
            "current_time": now()
        })


class TransactionWebhookView(APIView):
    def post(self, request):
        data = request.data

        try:
            transaction = Transaction.objects.create(
                transaction_id=data["transaction_id"],
                source_account=data["source_account"],
                destination_account=data["destination_account"],
                amount=data["amount"],
                currency=data["currency"],
            )

            process_transaction.delay(transaction.transaction_id)

        except IntegrityError:
            pass

        return Response(
            {"message": "Accepted"},
            status=status.HTTP_202_ACCEPTED
        )


class TransactionDetailView(APIView):
    def get(self, request, transaction_id):
        transaction = Transaction.objects.get(transaction_id=transaction_id)

        return Response({
            "transaction_id": transaction.transaction_id,
            "source_account": transaction.source_account,
            "destination_account": transaction.destination_account,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "status": transaction.status,
            "created_at": transaction.created_at,
            "processed_at": transaction.processed_at,
        })
