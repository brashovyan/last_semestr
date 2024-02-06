from celery import shared_task
from .models import *


@shared_task
def sample_task():
    method = "123"
    CustomLog.objects.create(method=method)
    print("HELLO")



