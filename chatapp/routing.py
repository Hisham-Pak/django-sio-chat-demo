from django.urls import re_path
from .consumers import ChatConsumer
from .views import chat_page

urlpatterns = [
    re_path(r"socket\.io/?", ChatConsumer.as_asgi()),
]
