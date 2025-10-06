from django.shortcuts import render
from django.views.decorators.cache import cache_page
from messaging.models import Message

@cache_page(60)
def conversation_view(request):
    messages = Message.objects.select_related('sender', 'receiver').prefetch_related('replies').all()
    return render(request, 'conversation.html', {'messages': messages})