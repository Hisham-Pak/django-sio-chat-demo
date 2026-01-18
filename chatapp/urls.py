from django.urls import path, re_path

from .consumers import ChatConsumer
from .views import chat_page

urlpatterns = [
    path("", chat_page),
]