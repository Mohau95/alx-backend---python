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