from django.contrib import admin
from .models import Message, MessageHistory, Notification

admin.site.register(Message)
admin.site.register(MessageHistory)
admin.site.register(Notification)