from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.tasks"]
)

# Celery Configuration
celery.conf.update(
    # Task configuration
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Beat configuration for periodic tasks
    beat_schedule={
        # Refresh Google Books data every 6 hours
        'refresh-google-books-data': {
            'task': 'app.tasks.tasks.refresh_book_data_from_google_books',
            'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
            'options': {
                'queue': 'periodic',
                'priority': 5,
            }
        },
        
        # Calculate statistics every day at 2 AM
        'calculate-daily-statistics': {
            'task': 'app.tasks.tasks.calculate_book_statistics',
            'schedule': crontab(minute=0, hour=2),  # Daily at 2 AM
            'options': {
                'queue': 'periodic',
                'priority': 3,
            }
        },
        
        # Optional: Refresh seed data weekly (Sunday at 3 AM)
        'refresh-seed-data-weekly': {
            'task': 'app.tasks.tasks.refresh_book_data_from_source',
            'schedule': crontab(minute=0, hour=3, day_of_week=0),  # Sunday at 3 AM
            'options': {
                'queue': 'periodic',
                'priority': 1,
            }
        },
    },
    
    # Queue configuration
    task_routes={
        'app.tasks.tasks.refresh_book_data_from_google_books': {'queue': 'periodic'},
        'app.tasks.tasks.calculate_book_statistics': {'queue': 'periodic'},
        'app.tasks.tasks.refresh_book_data_from_source': {'queue': 'periodic'},
        'app.tasks.tasks.send_new_book_notification': {'queue': 'notifications'},
    },
)

# Optional: Configure different queues with different settings
celery.conf.task_annotations = {
    'app.tasks.tasks.refresh_book_data_from_google_books': {
        'rate_limit': '10/h',  # Max 10 executions per hour
        'time_limit': 300,  # 5 minutes max execution time
        'soft_time_limit': 240,  # Soft limit at 4 minutes
    },
}