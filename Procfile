web: flask db upgrade; gunicorn app:app
worker: celery -A celery_worker.celery worker
