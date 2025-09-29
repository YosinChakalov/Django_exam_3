from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import *

@receiver(pre_delete, sender=Project)
def soft_delete_tasks_before_project_delete(sender, instance, **kwargs):
    Task.objects.filter(project=instance, is_deleted=False).update(is_deleted=True)
    