
# Payment Webhook Processing Service

A Dockerized Django-based backend service that receives transaction webhooks from external payment processors, acknowledges them immediately with `202 Accepted`, and processes transactions reliably in the background.

This implementation demonstrates:

- Asynchronous background task processing
- Idempotent webhook handling
- Persistent transaction storage
- Containerized deployment
- Cloud-ready architecture

---

# Architecture Overview

```
Webhook Client
       ↓
Django REST API (Gunicorn)
       ↓
PostgreSQL (Database)
       ↓
Redis (Message Broker)
       ↓
Celery Worker (Background Processing)
```

---

# Tools & Technologies Used

### Django
Used as the primary web framework to build the API layer.

### Django REST Framework
Provides request parsing, response handling, and API structure.

### PostgreSQL
Relational database used for persistent storage of transactions.  
Chosen for reliability, ACID compliance, and support for unique constraints.

### Redis
Used as a message broker for Celery.  
Provides fast in-memory queueing.

### Celery
Handles asynchronous background task execution.  
Ensures webhook processing does not block API response time.

### Gunicorn
Production-grade WSGI server for running Django inside the container.

### Docker
Containerizes the application for environment consistency and portability.

### Docker Compose
Orchestrates multiple services (web, db, redis, celery).

---

# Design Decisions

## Immediate Webhook Response (202 Accepted)

Webhook endpoints must respond quickly to prevent retries from external systems.

Instead of processing transactions synchronously:

1. Transaction is inserted into the database.
2. A Celery task is queued.
3. API returns `202 Accepted`.
4. Processing happens asynchronously in background.

This guarantees response time remains under 500ms.

---

## Idempotency Strategy

Multiple webhook calls with the same `transaction_id` must not create duplicate transactions.

Implemented using:

- A unique constraint on `transaction_id`
- Catching `IntegrityError` on duplicate inserts
- Ensuring background task is only triggered once

Example model constraint:

```
transaction_id = models.CharField(max_length=100, unique=True)
```

This ensures Idempotency.

---

## Background Processing Flow

1. Webhook received.
2. Transaction stored with status `PROCESSING`.
3. Celery task is pushed to Redis.
4. Worker consumes task.
5. 30-second delay simulates external API call.
6. Status updated to `PROCESSED`.
7. `processed_at` timestamp recorded.

---

# API Documentation

---

## 1. Health Check

Endpoint:

```
GET /
```

Response:

```
{
  "status": "HEALTHY",
  "current_time": "2026-02-19T12:00:00Z"
}
```

Purpose:
- Verify service availability
- Used for monitoring

---

## 2. Transaction Webhook

Endpoint:

```
POST /v1/webhooks/transactions
```

Request Body:

```
{
  "transaction_id": "txn_abc123def456",
  "source_account": "acc_user_789",
  "destination_account": "acc_merchant_456",
  "amount": 1500,
  "currency": "INR"
}
```

Response:

```
HTTP 202 Accepted
```

```
{
  "message": "Accepted"
}
```

Internal Behavior:

- Inserts transaction into PostgreSQL
- Queues background task
- Returns immediately

---

## 3. Retrieve Transaction Status

Endpoint:

```
GET /v1/transactions/{transaction_id}
```

Processing Response:

```
{
  "transaction_id": "txn_abc123def456",
  "status": "PROCESSING",
  "processed_at": null
}
```

Processed Response:

```json
{
  "transaction_id": "txn_abc123def456",
  "status": "PROCESSED",
  "processed_at": "2026-02-19T12:00:30Z"
}
```

---

# Running the Project Locally

---

## 1. Clone the Repository

```
git clone git@github.com:SubhasSajjan/confluencr_task.git
cd payment-webhook-service
```

---

## 2. Create Environment File

Create a `.env` file in the project root:

```
DEBUG=True
SECRET_KEY=django-insecure-key

POSTGRES_DB=payments
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

CELERY_BROKER_URL=redis://redis:6379/0
```

---

## 3. Build and Start Containers

```
docker compose up --build
```

This starts:

- PostgreSQL database
- Redis message broker
- Django API server
- Celery worker

---

## 4. Run Database Migrations

```
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

---

# Testing the System

---

## Test Health Endpoint

```
curl http://localhost:8000/
```

---

## Send Webhook

```
curl -X POST http://localhost:8000/v1/webhooks/transactions   -H "Content-Type: application/json"   -d '{
    "transaction_id": "txn_123",
    "source_account": "acc_1",
    "destination_account": "acc_2",
    "amount": 1000,
    "currency": "INR"
}'
```

Expected response:

```
202 Accepted
```

---

## Check Status Immediately

```
curl http://localhost:8000/v1/transactions/txn_123
```

Expected:

```
PROCESSING
```

---

## After 30 Seconds

Run again:

```
PROCESSED
```

---

## Test Duplicate Prevention

Send the same webhook multiple times.

Verify only one transaction exists:

```
docker compose exec db psql -U postgres -d payments
select * from transactions_transaction;
```

Only one row should exist.

---

# Useful Docker Commands

Restart containers:

```
docker compose restart
```

Rebuild containers:

```
docker compose down
docker compose up --build
```

Full reset including database:

```
docker compose down -v
docker compose up --build
```

---

# Deployment (AWS Ready)

This project can be deployed to AWS EC2 or any cloud provider supporting Docker.

Basic deployment steps:

```
git clone <repo>
docker compose up -d --build
```

Expose port 8000 or configure reverse proxy for production.

---

# Key Highlights

- Asynchronous webhook processing
- Immediate 202 acknowledgment
- Idempotent transaction handling
- Persistent storage
- Dockerized and cloud-ready
- Clean separation of concerns
- Scalable architecture (add more Celery workers)

---

# Conclusion

This project demonstrates production-oriented backend design principles:

- Event-driven architecture
- Decoupled background processing
- Database-enforced idempotency
- Containerized deployment
- Cloud compatibility

The service is reliable, scalable, and aligned with modern webhook processing best practices.
