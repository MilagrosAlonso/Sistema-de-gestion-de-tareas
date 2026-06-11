from django.db.models.signals import post_save
from django.dispatch import receiver
from boards.models import Card
from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@receiver(post_save, sender=Card)
def notify_card_assignment(sender, instance, created, **kwargs):
    if instance.assigned_to is not None:
        message = (
            f'Te asignaron la tarjeta "{instance.title}"'
            if created else
            f'Te reasignaron la tarjeta "{instance.title}"'
        )
        Notification.objects.create(
            recipient=instance.assigned_to,
            message=message
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{instance.assigned_to.id}',
            {
                'type': 'notification_message',
                'message': message,
            }
        )