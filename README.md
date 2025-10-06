# alx-backend---python
import os

project_name = "Django-signals_orm-0x04"

files = {
    f"{project_name}/messaging/models.py": """
from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    objects = models.Manager()  # default

    class UnreadMessagesManager(models.Manager):
        def for_user(self, user):
            return self.filter(receiver=user, read=False).only('id', 'content', 'sender', 'timestamp')
    unread_messages = UnreadMessagesManager()

    read = models.BooleanField(default=False)

class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    old_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
""",

    f"{project_name}/messaging/signals.py": """
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, MessageHistory, Notification

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Message.objects.get(pk=instance.pk)
        if old_instance.content != instance.content:
            MessageHistory.objects.create(message=instance, old_content=old_instance.content)
            instance.edited = True

@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    Notification.objects.filter(user=instance).delete()
    MessageHistory.objects.filter(message__sender=instance).delete()
""",

    f"{project_name}/messaging/apps.py": """
from django.apps import AppConfig

class MessagingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'

    def ready(self):
        import messaging.signals
""",

    f"{project_name}/chats/views.py": """
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from messaging.models import Message

@cache_page(60)
def conversation_view(request):
    messages = Message.objects.select_related('sender', 'receiver').prefetch_related('replies').all()
    return render(request, 'conversation.html', {'messages': messages})
""",

    f"{project_name}/messaging/admin.py": """
from django.contrib import admin
from .models import Message, MessageHistory, Notification

admin.site.register(Message)
admin.site.register(MessageHistory)
admin.site.register(Notification)
""",

    f"{project_name}/messaging/tests.py": """
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory

class MessagingSignalsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')

    def test_message_notification_created(self):
        msg = Message.objects.create(sender=self.user1, receiver=self.user2, content="Hello!")
        self.assertTrue(Notification.objects.filter(user=self.user2, message=msg).exists())

    def test_message_edit_logged(self):
        msg = Message.objects.create(sender=self.user1, receiver=self.user2, content="Original")
        msg.content = "Edited"
        msg.save()
        self.assertTrue(MessageHistory.objects.filter(message=msg, old_content="Original").exists())
"""
}

# Create folder structure and files
for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip())

print(f"{project_name} folder and all files created successfully!")
