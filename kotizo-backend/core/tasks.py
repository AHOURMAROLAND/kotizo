"""Celery tasks"""
from celery import shared_task

@shared_task
def send_notification_task(message):
    # TODO: Implement notification sending
    pass
